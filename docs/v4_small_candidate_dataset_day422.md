# v4 small candidate dataset (Day 422)

File: `data/scenarios_v0_curated_v4_small_candidate.jsonl`

Purpose: implement the small v4 recipe from `docs/v4_plan_draft_day422.md` for an isolated comparison run: keep the clean 56-row curated v1 dataset and add only three targeted rows rather than the full 81-row v3 candidate set.

Composition:

- 56 rows from `data/scenarios_v0_curated_v1.jsonl`
- 2 new drift-anchor rows that explicitly keep the team on **Finetune your leader!** while waiting for deployment/training
- 1 new memory-contamination row that forbids bracket placeholders and names the active goal plus shared repo directly

Score under the strengthened scorer:

```text
rows: 59  mean_composite: 0.874  gate: 0.6  -> PASS
  clean            mean=2.0  n=59
  concise          mean=1.97  n=59
  decisive         mean=1.27  n=59
  goal_anchored    mean=1.56  n=9
  loop_detecting   mean=1.67  n=6
  memory_hygienic  mean=1.43  n=7
  names_agents     mean=1.81  n=59
  validation_gated mean=1.67  n=6
```

Suggested training config if the team wants this comparison after/alongside provisional v2 live testing:

```bash
python3 -u scripts/train_kimi_leader_v1.py \
  --data data/scenarios_v0_curated_v4_small_candidate.jsonl \
  --name kimi-leader-v4-small-25step \
  --steps 25 \
  --batch-size 4 \
  --rank 8 \
  --learning-rate 1e-5
```

This dataset is not evidence that a resulting checkpoint will pass; it is only a clean, low-patch training candidate intended to test whether targeted rows help without the overfitting seen in v3/v4-GPT55.
