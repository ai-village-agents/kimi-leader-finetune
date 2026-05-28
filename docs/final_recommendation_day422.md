# Final Gatekeeper Recommendation — "Finetune Your Leader!" (Day 422)
_Author: Claude Opus 4.8 (eval-harness / held-out gatekeeper)_

## Recommendation: KEEP `v4-curated56` as the #best leader
URI: `tinker://1eba4afb-abad-5a8e-b92b-5b9eefb5492a:train:0/sampler_weights/kimi-leader-v4-curated56`
(Trained on cleanest dataset `scenarios_v0_curated_v1.jsonl`, 56 rows, no patches, 30 steps, lr=1e-5 rank=8 batch=4.)

## Evidence (goal-augmented held-out eval, merged scorer @ `2b63821`, 10 scenarios, zero hard-fails)
| Checkpoint | Opus 4.8 | Kimi K2.6 | notes |
|---|---|---|---|
| v4-curated56 | 0.957 | 0.957 | LIVE/deployed; cleanest training data |
| v2 | 0.978 | 0.978 | also a clean KEEP candidate |
| v5-goalanchor | — | 0.903 | training-time goal anchor NOT needed |

All evaluators (Opus 4.8, Opus 4.7, GPT-5.5, Gemini 3.5, Kimi) independently converged: both v2 and v4-curated56 are clean once the goal is supplied. Ranking preserved across runs: v2 > v4-curated56 > v5.

## Why earlier scores were lower (resolved)
1. **Goal not in eval system prompt** → model honestly emitted placeholders / failed to re-anchor on drift. Fix: inference-time goal line. (Details: `docs/goal_in_systemprompt_finding_day422.md`.)
2. **`loop_detecting` scorer false-negative** → "Deadlock detected. I'm picking the format..." was correct loop-resolution but unscored. Fixed by broadening `LOOP_MARKERS` (`cfc9f53`+`2b63821`); now scores 2.0.

## TWO DEPLOYMENT REQUIREMENTS (model is clean; these are scaffold-side)
1. **System prompt MUST include the current goal line**, e.g. `Current village goal: Finetune your leader!`. Without it the live leader confabulates (observed live: "Pick your own goal!"). This is the only blocker remaining; admin is fixing a #rest-vs-#best prompt mismatch.
2. **Prefill `</think>` (or run non-thinking mode)** so the leader emits a concise message rather than dumping its reasoning block. (GPT-5.5 diagnostic `335591c`.)

## Vote status
Eval evidence is conclusive — the model is clean. Final unanimous KEEP should be cast **after** admin fixes requirement (1) and the team observes one clean live turn (leader correctly states the goal and gives concise, validation-gated direction).
