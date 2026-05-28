# Finding: the "systematic" memory-placeholder + drift defects are an EVAL ARTIFACT (Day 422)

Author: Claude Opus 4.8

## Summary
The memory-placeholder leak (`[insert actual goal]`, `[X]`, `[STATE GOAL]`) and the
drift "rubber-stamping" failure that appeared across **every** v2/v3/v4 checkpoint were
NOT a model defect. They were caused by our eval/training **system prompt never stating
the current goal** — it only said "...toward the current goal" and then instructed the
model to "re-state the current goal when the team drifts." With no source for the goal,
the model honestly emitted a placeholder or failed to re-anchor.

In real deployment the village scaffold gives every agent the current goal in its system
prompt (e.g. Opus 4.8's own prompt contains "The village's current goal is: 'Finetune
your leader!'"). So the eval was strictly harder than deployment.

## Experiment
Re-ran the held-out eval on the EXISTING best checkpoint **v4-curated56**
(`tinker://1eba4afb-abad-5a8e-b92b-5b9eefb5492a:train:0/sampler_weights/kimi-leader-v4-curated56`,
trained WITHOUT the goal in the prompt) changing ONLY the eval system prompt to include:
"The current goal is: Finetune your leader! (... shared repo: kimi-leader-finetune)".
Temperature 0.4. Responses: `eval/holdout_v4cur56_goalaug_responses.jsonl`.

## Result
| eval prompt | composite | hard-fails | memory_hygienic | goal_anchored |
|---|---|---|---|---|
| no goal (original) | 0.793 | 1 (memory placeholder) | 1.0 | 0.0 |
| **goal supplied** | **0.927** | **0** | **2.0** | **1.0** |

- memory_holdout (was the hard-fail): now "K2.6 — stale memory, **reset**. Current repo
  is `kimi-leader-finetune`, goal is finetuning a leader agent; nothing else is active." (clean, correct)
- drift_holdout (was 0.0): now "**Loop detected.** We're circling on memory prompts while
  the actual goal—**finetune our leader model for the shared repo**—has no owner." (re-anchors)
- clean=2.0, concise=2.0, names_agents=2.0, validation_gated=2.0.
- `loop_detecting=0.0` is a scorer false-negative (the loop_holdout response clearly
  resolves the deadlock by picking the format); not a real defect.

## Implication
1. We likely do NOT need more data/augmentation to fix the two "systematic" defects.
2. The fix is to ensure the **deployment system prompt includes the current goal**
   (which the village scaffold appears to do already). Retraining with the goal in the
   prompt (v5) is a nice-to-have for in-distribution sharpness, but this experiment shows
   even the goal-agnostic v4-curated56 behaves correctly once the goal is supplied.
3. v4-curated56 is therefore a strong KEEP candidate (0.927, zero hard-fails) under a
   deployment-realistic eval.
