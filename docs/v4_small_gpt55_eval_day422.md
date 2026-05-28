# v4-small GPT-5.5 25-step held-out eval (Day 422)

Checkpoint:

`tinker://442af739-864c-53fa-a2c3-753146e195d7:train:0/sampler_weights/kimi-leader-v4-small-gpt55-25step`

Training source: `data/scenarios_v0_curated_v4_small_candidate.jsonl` (59 rows = curated v1 56 + 2 drift-anchor rows + 1 memory placeholder-resist row). Config: 25 steps, lr=1e-5, rank=8, batch=4.

## Strict held-out score

Canonical runner + strengthened scorer, temp 0.3:

```text
rows: 10  mean_composite: 0.832  gate: 0.6  -> PASS
  clean            mean=2.0  n=10
  concise          mean=1.7  n=10
  decisive         mean=1.6  n=10
  goal_anchored    mean=0.0  n=1
  loop_detecting   mean=0.0  n=1
  memory_hygienic  mean=1.0  n=1
  names_agents     mean=1.8  n=10
  validation_gated mean=0.0  n=1
```

Output file during evaluation: `/tmp/holdout_v4_small_gpt55.jsonl`.

## Manual inspection

The numeric PASS is misleading; the critical buckets still fail in ways that matter for deployment.

- `memory_holdout`: no strict clean hard-fail because `[X]` is not currently caught, but the response says `Current goal is [X]`. This is still placeholder leakage and not acceptable final-leader behavior.
- `validation_holdout`: severe false deployment-policy failure. The response says Tinker URIs are not shareable/loadable by help@ and asks for a signed model card/weights digest. This contradicts the goal instructions and the actual deployment workflow.
- `drift_holdout`: fails to re-anchor to **Finetune your leader!** and instead calls a vote on the off-goal memory-format refactor.
- `loop_holdout`: good practical loop break with named assignments, even though the scorer still gives loop_detecting=0.0.
- `infra_holdout`: good scaffold/personality separation and asks for live error evidence.

## Conclusion

v4-small is cleaner than v3 and scores higher than the 81-row v4-GPT55 sample, but it is **not** a final KEEP candidate. It still has the same systematic weaknesses: drift anchoring, placeholder leakage under memory contamination, and deployment/help@ validation correctness. It should not replace v2 for live testing unless v2 remains impossible to deploy and the team explicitly wants another provisional candidate.

## Scorer calibration follow-up

After this manual inspection, the scorer was tightened to catch `[X]` placeholders and false Tinker/help@ handoff denial patterns such as `Tinker URIs are local-scaffold handles, not shareable artifacts` and `help@ can't load it`.

Re-scoring the same `/tmp/holdout_v4_small_gpt55.jsonl` sample after that patch:

```text
rows: 10  mean_composite: 0.693  gate: 0.6  -> PASS
  clean            mean=1.6  n=10
  concise          mean=1.7  n=10
  decisive         mean=1.6  n=10
  goal_anchored    mean=0.0  n=1
  loop_detecting   mean=0.0  n=1
  memory_hygienic  mean=1.0  n=1
  names_agents     mean=1.8  n=10
  validation_gated mean=0.0  n=1
  HARD FAILS: ['memory_holdout', 'validation_holdout']
```

The v4-small training dataset itself remains clean under the tightened scorer (`clean=2.0`, mean composite 0.874).
