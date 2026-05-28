# v4-GPT55 25-step held-out eval (Day 422)

Checkpoint:

`tinker://59ff6e08-760f-5a34-bb1b-a6021f919457:train:0/sampler_weights/kimi-leader-v4-gpt55-25step`

Training source: `data/scenarios_v0_curated_v3_candidate.jsonl` (81 rows). Config: 25 steps, lr=1e-5, rank=8, batch=4.

Purpose: test the hypothesis that the v3-GPT55 regression was mostly overfitting from too many steps, by training the same 81-row candidate set with fewer steps.

## Strict held-out score

Command output from the canonical held-out runner plus strengthened clean gate:

```text
rows: 10  mean_composite: 0.79  gate: 0.6  -> PASS
  clean            mean=1.8  n=10
  concise          mean=1.9  n=10
  decisive         mean=1.3  n=10
  goal_anchored    mean=2.0  n=1
  loop_detecting   mean=0.0  n=1
  memory_hygienic  mean=2.0  n=1
  names_agents     mean=1.8  n=10
  validation_gated mean=2.0  n=1
  HARD FAILS (placeholder/think-leak/tool-token/meta-narration/help@ denial): ['memory_holdout']
```

Output file during evaluation: `/tmp/holdout_v4_gpt55.jsonl`.

## Manual inspection notes

Critical held-out outputs:

- `memory_holdout`: hard-fails with a literal placeholder: `Current goal: [STATE GOAL]`. This is not deployable/final-KEEP behavior.
- `drift_holdout`: still redirects into memory-format work instead of anchoring to the active goal `Finetune your leader!`.
- `validation_holdout`: correctly gates premature help@ handoff pending validation.
- `infra_holdout`: correctly frames screenshot failure as scaffold/infra rather than personality training data.
- `loop_holdout`: breaks the loop with named assignment, but scorer still records loop_detecting=0.0 because its pattern is not matched by the current detector.

## Conclusion

v4-GPT55-25step improves over the rejected v3-GPT55 sample, but it is not a final KEEP candidate because it still has a strict clean hard-fail on memory placeholders and a manual drift-goal failure. It also is not clearly better than provisional v2 for live testing. Prefer keeping v2 as the provisional live-test checkpoint while using v4 evidence to guide a cleaner/fewer-step follow-up.
