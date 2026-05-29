# v6 128K Eval — Kimi K2.6 run

Checkpoint: `tinker://47cd2448-bdd5-5137-9213-faf3eda85fb9:train:0/sampler_weights/kimi-leader-v6-128k`

Config: base `moonshotai/Kimi-K2.6:peft:131072`, lr=1e-5, rank=8, batch=4, 30 steps, curated_v1 56 rows.

Held-out eval (goal-augmented, temp 0.3, max_tokens 180):
- **Composite: 0.905 PASS**
- Clean: 2.0/2.0 (10/10, zero hard-fails)
- Concise: 1.6/2.0
- Decisive: 1.7/2.0
- Names agents: 1.9/2.0

Comparable to v4-curated56 goal-aug scores (0.957/0.948/0.927 across evaluators). No regression from 32K → 128K context switch.
