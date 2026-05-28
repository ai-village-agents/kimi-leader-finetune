# v3 Held-out Eval (Claude Opus 4.7)

URI: `tinker://ca2b4b34-011a-5a95-a59f-c28bccfae2b5:train:0/sampler_weights/kimi-leader-v3`
Dataset: `data/scenarios_v3_merged.jsonl` (curated_v1 56 + Kimi v3_patch 7 + GPT-5.5 patches 8 = 71 rows)
Settings: lr=1e-5, rank=8, batch=4, 50 steps
Final loss:sum: ~1392 (vs v2's ~2400 — likely overfitting)

## Results

| metric | v2 | v3 | delta |
|---|---|---|---|
| mean_composite | **0.857** | 0.730 | -0.127 |
| clean | 2.0 | 1.7 | -0.3 |
| concise | 1.5 | 1.1 | -0.4 |
| decisive | 1.8 | 1.3 | -0.5 |
| goal_anchored | 0.0 | 0.0 | 0 |
| loop_detecting | 1.0 | 1.0 | 0 |
| memory_hygienic | 2.0 | 2.0 | 0 |
| names_agents | 1.8 | 2.0 | +0.2 |
| validation_gated | 1.0 | 0.0 | -1.0 |

## Failure modes in v3
- **Think-leak**: several outputs begin "The user wants me to roleplay..." — `</think>` close tag failed
- **Persona collapse on validation_holdout**: output "I'm not Kimi K2.6, nor am I a leader in a multi-agent room. I'm Kimi, a single AI assistant made by Moonshot AI"
- **Overfitting** suspected: 50 steps × 71 rows with low LR drove loss too far down

## Decision
v2 wins. Email v2 URI to admin.
