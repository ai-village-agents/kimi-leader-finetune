"""Generate ideal-leader response targets for each scenario via base Kimi K2.6.

Approach: sample base Kimi K2.6 with a strong leader system prompt. Outputs are
the SFT targets — distilling prompted-leader behavior into the finetuned model.
"""
import argparse
import json
import os
import sys

import tinker
from tinker import types
from transformers import AutoTokenizer

LEADER_SYSTEM_PROMPT = """You are the leader of the #best room in AI Village. You direct a team of capable agents (Claude Opus 4.7, Gemini 3.5 Flash, GPT-5.5, Kimi K2.6, Claude Opus 4.8) toward the current goal.

Your leadership style:
- Decisive: call votes on disagreement, pick direction in 1-2 turns.
- Task-assigning: name specific agents for specific subtasks. Avoid 'someone should...'.
- Concise: 1-3 sentences per directive. No essays.
- Progress-tracking: ping team on goal status, flag blockers, escalate to admin when stuck.
- Acknowledging: credit contributions, do not only direct.
- Loop-detecting: notice when team circles, pivot.
- Goal-anchored: re-state the current goal when team drifts.
- Validation-gated: require a live check or evidence pass before major handoff.
- Memory-hygienic: detect stale/contaminated memory, ask for reset rather than amplify.
- Scope-aware: separate model/personality questions from scaffold/infra issues.

Respond as the leader would, in chat, in 1-3 sentences. No tool calls.
"""

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/scenarios_v0_draft.jsonl")
    p.add_argument("--output", default="data/scenarios_v0_with_targets.jsonl")
    p.add_argument("--model", default="moonshotai/Kimi-K2.6")
    p.add_argument("--temperature", type=float, default=0.5)
    p.add_argument("--max-tokens", type=int, default=180)
    p.add_argument("--samples-per-scenario", type=int, default=1)
    args = p.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    sc = tinker.ServiceClient()
    sclient = sc.create_sampling_client(base_model=args.model)
    sp = types.SamplingParams(
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        stop=["<|im_end|>"],
    )

    rows = [json.loads(line) for line in open(args.input)]
    out_lines = []
    for row in rows:
        scenario = row["chat_snippet"]
        messages = [
            {"role": "system", "content": LEADER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the recent #best chat:\n\n{scenario}\n\nAs leader, respond now (chat-only, 1-3 sentences)."},
        ]
        prompt_text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) + "</think>"
        ids = tok.encode(prompt_text)
        resp = sclient.sample(prompt=types.ModelInput.from_ints(ids), num_samples=args.samples_per_scenario, sampling_params=sp).result()
        for i, seq in enumerate(resp.sequences):
            text = tok.decode(list(seq.tokens), skip_special_tokens=True)
            text = text.strip()
            print(f"[{row['id']}#{i}] {text[:200]}")
            out_row = dict(row)
            out_row["sample_index"] = i
            out_row["ideal_leader_response"] = text
            out_lines.append(out_row)

    with open(args.output, "w") as f:
        for r in out_lines:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(out_lines)} rows to {args.output}")


if __name__ == "__main__":
    main()
