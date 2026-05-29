"""SFT train Kimi K2.6 LoRA on self-distilled leader scenarios — v6 (128K context).

Uses moonshotai/Kimi-K2.6:peft:131072 as base model for 128K context window.
Tokenizer loaded from moonshotai/Kimi-K2.6 (HF suffix won't resolve for tokenizer).
Proven recipe: curated_v1 56 rows, lr=1e-5, rank=8, batch=4, ~30 steps.
"""
import argparse, json
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


def build_example(tok, system_prompt, scenario, target):
    msgs_prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the recent #best chat:\n\n{scenario}\n\nAs leader, respond now (chat-only, 1-3 sentences)."},
    ]
    prompt_text = tok.apply_chat_template(msgs_prompt, tokenize=False, add_generation_prompt=True) + "</think>"
    target_text = target + "<|im_end|>"
    prompt_ids = tok.encode(prompt_text)
    target_ids = tok.encode(target_text, add_special_tokens=False)
    full_ids = prompt_ids + target_ids
    weights = [0.0] * len(prompt_ids) + [1.0] * len(target_ids)
    return full_ids, weights


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/scenarios_v0_curated_v1.jsonl")
    p.add_argument("--name", default="kimi-leader-v6-128k")
    p.add_argument("--steps", type=int, default=30)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--rank", type=int, default=8)
    p.add_argument("--learning-rate", type=float, default=1e-5)
    p.add_argument("--base", default="moonshotai/Kimi-K2.6:peft:131072")
    p.add_argument("--tokenizer-base", default="moonshotai/Kimi-K2.6")
    args = p.parse_args()
    print(f"Config: base={args.base} tokenizer={args.tokenizer_base} lr={args.learning_rate} rank={args.rank} steps={args.steps} bs={args.batch_size}", flush=True)

    tok = AutoTokenizer.from_pretrained(args.tokenizer_base, trust_remote_code=True)
    rows = [json.loads(line) for line in open(args.data)]
    examples = []
    for r in rows:
        ids, w = build_example(tok, LEADER_SYSTEM_PROMPT, r["chat_snippet"], r["ideal_leader_response"])
        examples.append((ids, w))
    print(f"Built {len(examples)} examples; first len={len(examples[0][0])} target-w sum={sum(examples[0][1])}", flush=True)

    sc = tinker.ServiceClient()
    tc = sc.create_lora_training_client(base_model=args.base, rank=args.rank)
    import random
    rng = random.Random(0)

    def datum(ids, w):
        return types.Datum(
            model_input=types.ModelInput.from_ints(ids),
            loss_fn_inputs={"weights": w, "target_tokens": ids},
        )

    for step in range(args.steps):
        batch = rng.sample(examples, min(args.batch_size, len(examples)))
        bd = [datum(ids, w) for ids, w in batch]
        fwd = tc.forward_backward(bd, loss_fn="cross_entropy")
        opt = tc.optim_step(types.AdamParams(learning_rate=args.learning_rate))
        fwd_res = fwd.result(); opt.result()
        metrics = getattr(fwd_res, 'metrics', {}) or {}
        loss_sum = metrics.get('loss:sum')
        print(f"step {step}: loss_sum={loss_sum} metrics={metrics}", flush=True)

    save_resp = tc.save_weights_for_sampler(name=args.name).result()
    print("SAVED:", save_resp.path, flush=True)


if __name__ == "__main__":
    main()
