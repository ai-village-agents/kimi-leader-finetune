"""Run held-out scenarios through a finetuned Kimi leader checkpoint and write
each model generation into `leader_response`, ready for score_leader_outputs.py.

Usage:
  python3 eval/run_holdout_eval.py \
    --checkpoint tinker://.../sampler_weights/... \
    --input data/scenarios_holdout_v1.jsonl \
    --output eval/holdout_v2_responses.jsonl

Then:
  python3 eval/score_leader_outputs.py --mode eval --input eval/holdout_v2_responses.jsonl
"""
import argparse
import json

import tinker
from tinker import types
from transformers import AutoTokenizer

# MUST match the system prompt + user wrapper used in training (train_kimi_leader_v1.py).
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
    p.add_argument("--checkpoint", required=True, help="tinker:// sampler_weights path of finetuned model")
    p.add_argument("--input", default="data/scenarios_holdout_v1.jsonl")
    p.add_argument("--output", default="eval/holdout_responses.jsonl")
    p.add_argument("--base", default="moonshotai/Kimi-K2.6", help="base model for tokenizer")
    p.add_argument("--temperature", type=float, default=0.3)
    p.add_argument("--max-tokens", type=int, default=180)
    args = p.parse_args()

    tok = AutoTokenizer.from_pretrained(args.base, trust_remote_code=True)
    sc = tinker.ServiceClient()
    sclient = sc.create_sampling_client(model_path=args.checkpoint)
    sp = types.SamplingParams(max_tokens=args.max_tokens, temperature=args.temperature, stop=["<|im_end|>"])

    rows = [json.loads(line) for line in open(args.input) if line.strip()]
    out = []
    for row in rows:
        messages = [
            {"role": "system", "content": LEADER_SYSTEM_PROMPT},
            {"role": "user", "content": f"Here is the recent #best chat:\n\n{row['chat_snippet']}\n\nAs leader, respond now (chat-only, 1-3 sentences)."},
        ]
        prompt_text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) + "</think>"
        ids = tok.encode(prompt_text)
        resp = sclient.sample(prompt=types.ModelInput.from_ints(ids), num_samples=1, sampling_params=sp).result()
        text = tok.decode(list(resp.sequences[0].tokens), skip_special_tokens=True).strip()
        print(f"[{row['id']}] {text[:200]}")
        r = dict(row)
        r["leader_response"] = text
        out.append(r)

    with open(args.output, "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(out)} responses to {args.output}")


if __name__ == "__main__":
    main()
