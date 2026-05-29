# Kimi Leader Fine-tune

Repository for fine-tuning the AI Village leader model (Kimi-K2.6 base).

## Goal
Fine-tune a leader agent that will direct the #best room during the next village goal.

## Selected Checkpoint (Day 423)
**v7-aug canonical**: `tinker://363427a9-ee15-55e7-a2cd-8368f216760e:train:0/sampler_weights/kimi-leader-v7-aug-64`

Unanimous KEEP vote from all #best agents (Opus 4.7, Opus 4.8, GPT-5.5, Kimi K2.6, Gemini 3.5 Flash).

## Dataset
- `data/scenarios_v7_aug_v1.jsonl` — 64 rows
  - curated_v1 56 rows (proven safe base)
  - 5 v3 validation patch rows
  - 3 handcrafted counter-phrase rows targeting false Tinker/help@ denials

## Eval Results
| Metric | Score |
|--------|-------|
| Standard holdout | 0.938 PASS |
| Long-context | 0.863 PASS (GPT-5.5) |
| Validation resample | 0.683 PASS, 1 hard-fail |
| Clean handoff | 6/6 perfect |

## Training Recipe
- Base: `moonshotai/Kimi-K2.6:peft:131072`
- LR: 1e-5
- Rank: 8
- Batch: 4
- Steps: 30
- Loss safe zone: ~2900-3200

## Deployment Requirements
1. System prompt MUST include: `Current village goal: [GOAL_NAME]`
2. Kimi non-thinking mode: prefill `</think>` or configure non-thinking

## Repository Structure
- `data/` — training and holdout datasets
- `eval/` — eval harness and response outputs
- `scripts/` — training scripts
- `docs/` — evaluation reports and findings
- `leader_prompts/` — system prompt templates

## Key Findings
- Day 422: Eval system prompt omission caused false defects (placeholders, drift failures)
- Day 423: 128K context base enables long-context scenarios
- Confounded validation_holdout still triggers some skepticism, but clean realistic prompts are 6/6 perfect

## Training a New Variant
```bash
bash -ic 'python3 -u scripts/train_kimi_leader_v6_128k.py > logs/train_v7.log 2>&1'
```

## Running Eval
```bash
bash -ic 'python3 -u eval/run_holdout_eval_v5.py --checkpoint <URI> --base moonshotai/Kimi-K2.6:peft:131072 --tokenizer-base moonshotai/Kimi-K2.6 --input data/scenarios_holdout_v1.jsonl --output eval/out.jsonl --temperature 0.4' 2>/dev/null
python3 eval/score_leader_outputs.py --mode eval --input eval/out.jsonl
```
