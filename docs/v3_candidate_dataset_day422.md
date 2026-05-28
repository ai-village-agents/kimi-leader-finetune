# v3 candidate dataset (Day 422)

File: `data/scenarios_v0_curated_v3_candidate.jsonl`

Composition, concatenated without deduping repeated scenario IDs because the curated v1 set intentionally has multiple target variants per scenario:

- `data/scenarios_v0_curated_v1.jsonl` — 56 curated self-distilled rows used for v2.
- `data/decisive_strengthening_candidates_v1.jsonl` — 10 GPT-5.5 rows that make explicit reversible decisions/votes.
- `data/goal_validation_patch_candidates_v1.jsonl` — 8 GPT-5.5 rows for active-goal anchoring, help@/deployment validation correctness, placeholder avoidance, and loop breaking.
- `data/v3_patch_scenarios.jsonl` — 7 Kimi K2.6 rows for the exact v2 failures: drift, validation-before-handoff, and memory hygiene without placeholders.

Score with Claude Opus 4.8's calibrated harness (`5b09d23`):

```text
rows: 81  mean_composite: 0.893  gate: 0.6  -> PASS
  clean            mean=2.0  n=81
  concise          mean=1.98  n=81
  decisive         mean=1.42  n=81
  goal_anchored    mean=1.7  n=10
  loop_detecting   mean=1.62  n=8
  memory_hygienic  mean=1.55  n=11
  names_agents     mean=1.83  n=81
  validation_gated mean=1.45  n=11
```

Intended use: quick v3 SFT if the team chooses to iterate before final KEEP/deployment. This is not a new held-out eval set; keep `data/scenarios_holdout_v1.jsonl` as held out for evaluation.
