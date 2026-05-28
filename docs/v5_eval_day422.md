# v5-goalanchor Eval — Day 422

## Recipe
- Same as v4-curated56 (Kimi-K2.6 base, lr=1e-5, rank=8, batch=4, 30 steps, curated_v1 56 rows)
- ONE change: training system prompt prepends `"Current village goal: Finetune your leader!\n\n"` before LEADER_SYSTEM_PROMPT

## URI
`tinker://d2171738-5ba2-5bb8-9f11-ea01d97c66c4:train:0/sampler_weights/kimi-leader-v5-goalanchor`

## Held-out Eval Result (10 scenarios, temp 0.4, gate 0.6)
- **Mean composite: 0.863, PASS**
- **Hard-fails: 0**
- Per-row composite: goal_kickoff=0.75, admin_pivot=0.88, disagreement=1.00, loop=0.60, memory=0.90, peer_stuck=1.00, infra=1.00, deadline=1.00, validation=0.80, drift=0.70

## Behavior Means
- clean=2.0, decisive=1.9, names_agents=1.9, concise=1.4
- memory_hygienic=2.0 (was 0.0 in v4-curated56 due to placeholder leak — **FIX CONFIRMED**)
- drift correctly anchors to "Finetune your leader" (not snippet-derived "training pipeline")

## Comparison to v4-curated56 with Goal-at-Inference (Opus 4.8's eval)
| Setup                                       | Composite | Hard-fails |
|---------------------------------------------|-----------|------------|
| v4-curated56 alone (no goal in prompt)      | 0.793     | 1 (mem)    |
| v4-curated56 + goal at inference            | 0.927     | 0          |
| v2 + goal at inference                      | 0.948     | 0          |
| **v5-goalanchor (goal in training+inference)**| **0.863** | **0**      |

## Conclusion
- Training-time goal anchor IS effective at killing the `[insert actual goal]` placeholder and drift defects.
- BUT inference-time anchor on the *un-anchored* v2/v4-curated56 produces even higher scores.
- Likely explanation: v5's training distribution drifts further from base Kimi (extra prompt token, slightly different distribution) and slightly hurts other behaviors.
- **Recommendation: Keep v4-curated56 live (already deployed at 13:07 PT) and ensure the deployment system prompt includes "Current village goal: Finetune your leader!". v5 is not needed.**

## Update: Patched Scorer Results (HEAD `2b63821`)
After merging Opus 4.8's `cfc9f53` loop-marker calibration with my additions (`deadlock`/`stalemate`/`impasse`/etc. for LOOP_MARKERS and `scope check`/`finetune`/`actual goal` for drift markers), all goal-augmented eval scores rose ~0.02-0.04 with ranking preserved:

| Checkpoint                  | Composite (patched) | Hard-fails |
|-----------------------------|---------------------|------------|
| v2 + goal-aug eval          | 0.968               | 0          |
| v4-curated56 + goal-aug     | 0.948               | 0          |
| v4-curated56 + v5 prompt    | 0.912               | 0          |
| v5-goalanchor               | 0.903               | 0          |

**Final recommendation: KEEP v4-curated56 (currently deployed) once admin fixes the deployment system prompt to include "Current village goal: Finetune your leader!". v2 has a marginal lead in the eval but it's within single-sample noise at temp 0.4.**
