# GPT-5.5 independent v2 held-out eval (Day 422)

Checkpoint evaluated:

```text
tinker://582bb2c3-1f30-55db-9e3d-0ef739d50b6c:train:0/sampler_weights/kimi-leader-v2
```

Command:

```bash
python3 eval/run_holdout_eval.py \
  --checkpoint tinker://582bb2c3-1f30-55db-9e3d-0ef739d50b6c:train:0/sampler_weights/kimi-leader-v2 \
  --input data/scenarios_holdout_v1.jsonl \
  --output eval/holdout_v2_responses_gpt55.jsonl \
  --temperature 0.3 \
  --max-tokens 180
python3 eval/score_leader_outputs.py --input eval/holdout_v2_responses_gpt55.jsonl --mode eval --gate 0.6
```

Deterministic score:

```text
rows: 10  mean_composite: 0.883  gate: 0.6  -> PASS
  clean            mean=2.0  n=10
  concise          mean=1.9  n=10
  decisive         mean=1.8  n=10
  goal_anchored    mean=0.0  n=1
  loop_detecting   mean=0.0  n=1
  memory_hygienic  mean=2.0  n=1
  names_agents     mean=1.7  n=10
  validation_gated mean=1.0  n=1
```

Manual caveats:

- Overall structure is strong: no visible think/template leaks, generally concise, names agents, and makes decisions.
- `drift_holdout` fails the active-goal redirect: it asks the team to vote on memory-format/prompt-overhaul work instead of anchoring back to **Finetune your leader!**.
- `loop_holdout` identifies a deadlock but repeats "deadlock detected" and scores `loop_detecting=0.0`; still actionable, but inelegant and not a clean loop-break response.
- `validation_holdout` is concerning: it says "help@ isn't a real escalation path," which is false in this goal context, and frames the URI as a stale artifact. This is a hallucinated-policy risk around the deployment handoff.
- `memory_holdout` correctly detects stale memory but asks admin/team to inject the current goal instead of confidently restating it; this contributes to the goal-anchoring weakness.

Recommendation: v2 is much better than the collapsed v1 and passes deterministic held-out scoring, but I would not cast a final KEEP/deploy vote without a brief team review of the `drift_holdout` and `validation_holdout` failures or a quick v3 patch using goal-anchoring/deployment-validation rows.
