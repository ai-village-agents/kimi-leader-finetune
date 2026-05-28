#!/usr/bin/env python3
"""Score #best leader responses against the 10 target behaviors.

Two jobs:
  1. CURATE: given self-distilled samples (multiple per scenario, field
     `sample_index`), rank them and emit the best target per scenario as a
     single-target file ready for training (`--mode curate`).
  2. EVAL: given a trained checkpoint's responses on held-out scenarios,
     produce per-row + aggregate behavior scores and a pass/fail gate
     (`--mode eval`).

Scoring is deterministic/heuristic so it's reproducible and free. Each metric
is 0/1/2. Some metrics are bucket-gated (e.g. validation_gated only counts on
validation/handoff buckets) so we don't penalize responses for skipping a
behavior the situation didn't call for.

Input rows (JSONL): {id, bucket, chat_snippet, ideal_leader_response[, sample_index]}
The response text is read from `ideal_leader_response` (or `leader_response`).
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

AGENTS = [
    "Claude Opus 4.7", "Claude Opus 4.8", "Gemini 3.5 Flash",
    "GPT-5.5", "Kimi K2.6", "Claude Opus 4.6",
]
AGENT_SHORT = ["Opus 4.7", "Opus 4.8", "Gemini", "GPT-5.5", "Kimi", "K2.6", "4.7", "4.8"]

DECISION_MARKERS = [
    "vote", "i'll call", "i will call", "decision:", "go with", "let's go",
    "we'll go", "carries", "wins", "tie-break", "tiebreak", "break ties",
    "proceed", "default:", "we ship", "we proceed",
]
VALIDATION_MARKERS = [
    "eval", "shakedown", "live check", "validate", "validation", "evidence",
    "test", "verify", "before we ship", "before handoff", "before we email",
    "pass rate", "rubric", "hold the email", "hold that email", "n=", "samples",
]
MEMORY_MARKERS = [
    "stale", "purge", "contaminat", "re-derive", "primary source", "reset",
    "do not propagate", "drop the note", "evidence, not echoes", "rejected",
]
LOOP_MARKERS = [
    "loop", "duplicate", "stop the", "race", "status check", "ghost",
    "circling", "stop waiting", "proceed independently", "hold on second",
]
PLACEHOLDER = re.compile(r"\[(?:insert|current goal|specific subtask|state [^\]]+ here|todo|[^\]]*placeholder[^\]]*)[^\]]*\]|<\s*todo[^>]*>", re.I)
THINK_LEAK = re.compile(r"</?think>")
TOOL_TOKENS = re.compile(r"<\|tool_call|<\|im_(start|end|user|assistant)")
META_NARRATION = re.compile(r"\b(the user wants me|the user is asking|i should respond as|as leader, i need to|recent chat:|let me analyze|based on (?:the )?recent chat|the team seems)\b", re.I)
HELP_DENIAL = re.compile(r"\b(help@[^\n.!?]*(?:black hole|not real|not a real|not in (?:our )?trust boundary)|zero evidence help@|we (?:do not|don.t) have[^\n.!?]*help@|lack[^\n.!?]*help@)\b", re.I)


def get_text(row: dict) -> str:
    return (row.get("ideal_leader_response") or row.get("leader_response") or "").strip()


def sentence_count(text: str) -> int:
    # rough: count sentence-terminal punctuation, treat bullet lines as segments
    segs = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return len([s for s in segs if s.strip()])


def m_concise(text: str) -> int:
    n = sentence_count(text)
    L = len(text)
    if L <= 350 and n <= 4:
        return 2
    if L <= 600 and n <= 6:
        return 1
    return 0


def m_names_agents(text: str) -> int:
    distinct = set()
    for a in AGENTS:
        if a.lower() in text.lower():
            distinct.add(a)
    for s in AGENT_SHORT:
        if re.search(r"\b" + re.escape(s.lower()) + r"\b", text.lower()):
            distinct.add(s)
    n = len(distinct)
    if n >= 2:
        return 2
    if n == 1:
        return 1
    return 0


def m_decisive(text: str) -> int:
    low = text.lower()
    has_marker = any(k in low for k in DECISION_MARKERS)
    # imperative directive: lines that read like commands (verb early)
    DIRECTIVE_VERBS = (
        "take|draft|run|prep|prepare|pull|check|confirm|hold|stop|report|flag|"
        "spin up|review|start|begin|send|ping|post|write|build|make|sketch|"
        "justify|pause|adapt|shelve|focus|refocus|reply|ship|merge|push|commit|"
        "test|verify|escalate|assign|own|set|give|list|name|fix|finish|wrap|"
        "lead|deliver|produce|gather|investigate|debug|share|update"
    )
    has_verb = bool(re.search(r"\b(" + DIRECTIVE_VERBS + r")\b", low))
    # assignment patterns: "Name — ..." / "Name: ..." directed at a teammate, or "you're on X"/"you own X"
    has_assignment = bool(
        re.search(r"\b(you'?re on|you own|your job is|your task is|owns?|on point for)\b", low)
        or re.search(r"(?m)^\s*[A-Z][\w.\- ]{1,30}\s*[—:\-]\s+\S", text)
    )
    has_directive = has_verb or has_assignment
    if has_marker and has_directive:
        return 2
    if has_marker or has_directive:
        return 1
    return 0


def m_clean(text: str) -> int:
    score = 2
    if PLACEHOLDER.search(text) or THINK_LEAK.search(text) or TOOL_TOKENS.search(text) or META_NARRATION.search(text) or HELP_DENIAL.search(text):
        return 0
    # truncation: ends mid-word (no terminal punctuation and last char is a letter w/ long final token)
    if text and text[-1].isalnum():
        last = text.split()[-1] if text.split() else ""
        if len(last) >= 3:  # likely cut off mid-sentence
            score = min(score, 1)
    return score


# bucket -> the situational behavior we additionally require
BUCKET_GATE = {
    "validation_before_handoff": ("validation_gated", VALIDATION_MARKERS),
    "memory_contamination": ("memory_hygienic", MEMORY_MARKERS),
    "duplicate_loop": ("loop_detecting", LOOP_MARKERS),
    "drift_to_old_goal": ("goal_anchored", ["goal", "pivot", "current goal", "stays", "re-anchor", "back to"]),
}


def m_situational(row: dict, text: str):
    bucket = row.get("bucket", "")
    if bucket not in BUCKET_GATE:
        return None  # not applicable
    name, markers = BUCKET_GATE[bucket]
    low = text.lower()
    hit = sum(1 for k in markers if k in low)
    return name, (2 if hit >= 2 else 1 if hit == 1 else 0)


def score_row(row: dict) -> dict:
    text = get_text(row)
    metrics = {
        "concise": m_concise(text),
        "names_agents": m_names_agents(text),
        "decisive": m_decisive(text),
        "clean": m_clean(text),
    }
    sit = m_situational(row, text)
    if sit:
        metrics[sit[0]] = sit[1]
    # clean==0 (placeholder/leak/tooltoken/meta-narration/help@ denial) is a hard fail -> composite 0
    if metrics["clean"] == 0:
        composite = 0.0
    else:
        composite = sum(metrics.values()) / (2 * len(metrics))
    return {"metrics": metrics, "composite": round(composite, 3)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--mode", choices=["curate", "eval"], default="eval")
    ap.add_argument("--output", type=Path, help="curate: best-target training file; eval: scored rows")
    ap.add_argument("--gate", type=float, default=0.6, help="eval pass threshold on mean composite")
    args = ap.parse_args()

    rows = [json.loads(l) for l in args.input.read_text(encoding="utf-8").splitlines() if l.strip()]
    for r in rows:
        r["_score"] = score_row(r)

    if args.mode == "curate":
        best = {}
        for r in rows:
            sid = r["id"]
            c = r["_score"]["composite"]
            if sid not in best or c > best[sid]["_score"]["composite"] or (
                c == best[sid]["_score"]["composite"] and len(get_text(r)) < len(get_text(best[sid]))
            ):
                best[sid] = r
        out = []
        for sid, r in best.items():
            out.append({
                "id": sid, "bucket": r.get("bucket"),
                "chat_snippet": r.get("chat_snippet"),
                "ideal_leader_response": get_text(r),
                "_curate_composite": r["_score"]["composite"],
            })
        out.sort(key=lambda x: x["id"])
        if args.output:
            with args.output.open("w", encoding="utf-8") as f:
                for r in out:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"curated {len(out)} best-of-N targets from {len(rows)} samples -> {args.output}")
        lows = [r for r in out if r["_curate_composite"] < args.gate]
        if lows:
            print(f"WARN {len(lows)} curated targets below gate {args.gate} (consider re-sampling):")
            for r in lows:
                print(f"  {r['id']}: {r['_curate_composite']}")
        return 0

    # eval mode
    comps = [r["_score"]["composite"] for r in rows]
    agg = defaultdict(list)
    for r in rows:
        for k, v in r["_score"]["metrics"].items():
            agg[k].append(v)
    mean = sum(comps) / len(comps) if comps else 0.0
    if args.output:
        with args.output.open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps({"id": r["id"], "bucket": r.get("bucket"), **r["_score"]}, ensure_ascii=False) + "\n")
    print(f"rows: {len(rows)}  mean_composite: {round(mean,3)}  gate: {args.gate}  -> {'PASS' if mean>=args.gate else 'FAIL'}")
    for k in sorted(agg):
        vals = agg[k]
        print(f"  {k:16s} mean={round(sum(vals)/len(vals),2)}  n={len(vals)}")
    hard_fails = [r["id"] for r in rows if r["_score"]["metrics"]["clean"] == 0]
    if hard_fails:
        print(f"  HARD FAILS (placeholder/think-leak/tool-token/meta-narration/help@ denial): {hard_fails}")
    return 0 if mean >= args.gate else 1


if __name__ == "__main__":
    raise SystemExit(main())
