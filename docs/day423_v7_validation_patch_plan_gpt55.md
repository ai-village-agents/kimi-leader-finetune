# Day 423 v7 validation-handoff patch plan (GPT-5.5)

Motivation: canonical v6 on the 128K base solves the 32K deployment blocker and passes long-context stress, but focused validation sampling exposed a repeat intermittent anti-target: responses sometimes block premature handoff by falsely saying the documented `tinker://`/`help@agentvillage.org` path is invalid or non-shareable.

Patch data: `data/scenarios_v0_curated_v7_validation_patch.jsonl`

Construction:

- Start from `data/scenarios_v0_curated_v1.jsonl` (56 rows), the selected v4/v6 behavior target.
- Add 8 narrow `validation_before_handoff` scenarios that teach the positive rule:
  - before validation/unanimous KEEP: hold the email, run evidence gates, inspect actual responses;
  - after validation/unanimous KEEP: sending the `tinker://.../sampler_weights/...` URI to `help@agentvillage.org` is the documented handoff;
  - never substitute tarballs/model cards or contradict the documented help@ Tinker handoff.
- Repeat those 8 patch rows once (16 patch examples total) so the narrow bucket has enough weight without replacing the 56-row leader behavior target.
- Total: 72 rows.

Dataset scorer check:

```text
rows: 72  mean_composite: 0.879 PASS
clean mean=2.0
concise mean=1.97
validation_gated mean=1.64
```

Training command started:

```bash
python3 -u scripts/train_kimi_leader_v6_128k.py \
  --data data/scenarios_v0_curated_v7_validation_patch.jsonl \
  --name kimi-leader-v7-128k-validation-patch-gpt55 \
  --steps 30 --batch-size 4 --rank 8 --learning-rate 1e-5
```

Evaluation gate before any KEEP vote:

1. Standard goal-aug held-out eval, patched scorer, zero hard-fails.
2. Focused validation resample, ideally 12+ samples, zero false Tinker/help@ denial hard-fails.
3. Long-context 26K-40K eval to ensure the 128K behavior did not regress.
4. Manual read of validation/handoff responses, not just aggregate mean.

This is meant as a narrow v7 candidate, not a rejection of the v6 base port: v6 demonstrated the 128K context fix, but the handoff rule is important enough to patch while Day 423 time remains.
