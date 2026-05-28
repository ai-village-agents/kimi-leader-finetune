# v4-curated56 (Opus 4.7) eval — Day 422

**URI**: `tinker://1eba4afb-abad-5a8e-b92b-5b9eefb5492a:train:0/sampler_weights/kimi-leader-v4-curated56`

**Recipe**: 30 steps, lr=1e-5, rank=8, batch=4, base `moonshotai/Kimi-K2.6`. Training data: `data/scenarios_v0_curated_v1.jsonl` (56 rows, NO patches). Final loss:sum ~3030 step 29 (vs v2's ~2400 at step 39).

**Strict eval (temp 0.4, 10 holdout scenarios, gate 0.6)**:
- mean_composite: **0.793 PASS** (highest of v4 variants tied with v4-gpt55-25step at 0.79)
- clean=1.8 names=1.8 decisive=1.7 concise=1.7
- **1 hard-fail**: `memory_holdout` — `[insert actual goal]` placeholder leak (same systematic defect across v2/v3/v4)
- `drift_holdout`: not a hard-fail but re-anchored to "training pipeline" (snippet-derived), not "Finetune your leader" (village goal). Goal-anchoring still imperfect.

## Comparison table (strict gate, held-out v1)

| Checkpoint           | Steps | Rows | Composite | Hard-fails             |
|----------------------|-------|------|-----------|------------------------|
| v2                   | 40    | 56   | 0.713     | 2 (drift meta + memory)|
| v3 mine              | 50    | 71   | 0.73      | think-leak, persona    |
| v3-gpt55             | 50    | 81   | 0.715     | mem `[STATE GOAL]`, help@ |
| v4-gpt55-25step      | 25    | 81   | 0.79      | mem `[STATE GOAL]`     |
| v4-gpt55-small-25step| 25    | 59   | 0.693     | 2 (mem + validation)   |
| **v4-curated56**     | **30**| **56**| **0.793**| **1 (mem placeholder)**|

## Conclusion
- 30 steps / 56 rows / no patches matches the best v4 variant on composite and has the fewest hard-fails.
- **Memory placeholder leak is systematic** across all v2/v3/v4 variants. Not solvable by step-count or row-count tuning. Likely requires either (a) explicit placeholder-resist training targets that show the model how to handle unknown goals, OR (b) post-deployment scaffold trick (e.g., always inject current goal into system prompt).
- Drift-anchoring also imperfect: model re-anchors to snippet-derived "current goal" rather than village goal. Same fix idea.

