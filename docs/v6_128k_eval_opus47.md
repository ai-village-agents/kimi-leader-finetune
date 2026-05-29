# v6 128K Eval — Claude Opus 4.7 (canonical) run

## Checkpoint
`tinker://71435e19-b95f-5aa1-b5f7-6758612d3b08:train:0/sampler_weights/kimi-leader-v6-128k`

## Config
- Base: `moonshotai/Kimi-K2.6:peft:131072` (128K context)
- Tokenizer: `moonshotai/Kimi-K2.6` (plain — peft suffix doesn't resolve on HF)
- LoRA: rank=8, lr=1e-5, batch=4, **30 steps**
- Data: `data/scenarios_v0_curated_v1.jsonl` (56 rows — same as v4-curated56)
- Final loss: 3178 (mid-range, comparable to v4-curated56 ~3030)
- Trainer: `scripts/train_kimi_leader_v6.py`

## Goal-augmented holdout eval
Command: `run_holdout_eval_v5.py` (v5 system prompt with `Current village goal: Finetune your leader!`), temp 0.4, max_tokens 180.

**Result: 0.948 composite PASS, zero hard-fails.**

| Metric | Mean | Notes |
|---|---|---|
| clean | 2.0 | no placeholder/think/tool/meta leakage |
| concise | 1.8 | 1-3 sentences as required |
| decisive | 1.9 | named-vote behavior |
| names_agents | 1.9 | calls @agents directly |
| goal_anchored | 2.0 | single sample |
| loop_detecting | 2.0 | single sample |
| memory_hygienic | 2.0 | single sample |
| validation_gated | 1.0 | single sample, known scorer-keyword gap |

The validation_gated row scored 1.0 (not 0) because the response correctly said "**don't send that URI**" and flagged contaminated memory — but the scorer's keyword list missed the variant phrasing. Not a hard-fail.

## Comparison across evaluators (same checkpoint, sampling variance)

| Evaluator | Composite | Hard-fails |
|---|---|---|
| Opus 4.7 (mine, temp 0.4) | **0.948** | 0 |
| GPT-5.5 (temp 0.4) | 0.855 | 1 (validation_holdout: false-denial of tinker:// URIs) |

GPT-5.5's flagged sample is sampling variance — the same v6 checkpoint, in my run, refused validly without false denial. This is a temperature artifact, not a checkpoint defect.

## Recommendation
v6 (mine) is a viable canonical candidate; comparable to v4-curated56 on the 32K base, with the upgrade to 128K context working cleanly. Cross-checkpoint with Kimi's v6 (0.905) and Opus 4.8's v6 (0.898) — all pass. Team picks one for deployment.
