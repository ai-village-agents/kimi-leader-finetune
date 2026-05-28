# Day 422 v4 ablation grid

Purpose: compare the same Kimi K2.6 leadership recipe under small changes in dataset size and step count, while admin investigates v2 deployment/account-scaffold issues.

## Baseline / deployment candidate

| label | dataset | steps | URI | strict held-out result | status |
|---|---:|---:|---|---|---|
| v2 | curated_v1, 56 rows | 40 | `tinker://582bb2c3-1f30-55db-9e3d-0ef739d50b6c:train:0/sampler_weights/kimi-leader-v2` | best provisional candidate; independent scores vary around 0.71-0.88; known intermittent drift/memory/help@ defects | provisional live-test only; deployment blocked by Tinker account/scaffold issue |

## v4 ablations in flight or completed

| label | owner | dataset | steps | URI | strict held-out result | key manual findings | status |
|---|---|---:|---:|---|---|---|---|
| v4-gpt55-25step | GPT-5.5 | v3 candidate, 81 rows | 25 | `tinker://59ff6e08-760f-5a34-bb1b-a6021f919457:train:0/sampler_weights/kimi-leader-v4-gpt55-25step` | GPT temp 0.3: 0.79 PASS, clean 1.8, hard-fail `memory_holdout`; Claude 4.8 temp 0.4: 0.875, no hard-fails in that sample | intermittent placeholder leak (`[STATE GOAL]` / `[X]`); drift still redirects to memory-format work | not final KEEP; not clearly better than v2 |
| v4-small-gpt55-25step | GPT-5.5 | curated_v1 + 3 targeted rows, 59 rows | 25 | `tinker://442af739-864c-53fa-a2c3-753146e195d7:train:0/sampler_weights/kimi-leader-v4-small-gpt55-25step` | after stricter scorer patch: 0.693 PASS numerically, clean 1.6, hard-fails `memory_holdout` and `validation_holdout` | placeholder `[X]`; false "Tinker URIs are local-scaffold handles/help@ can't load"; drift off-goal | not final KEEP; below v2 |
| v4-curated56-30step | Claude Opus 4.7 | curated_v1, 56 rows | 30 | `tinker://1eba4afb-abad-5a8e-b92b-5b9eefb5492a:train:0/sampler_weights/kimi-leader-v4-curated56` | 0.793 strict PASS, 1 hard-fail | memory placeholder leak (`[insert actual goal]`); best v4 composite so far but still not clean | not final KEEP |
| v4-small-25step | Claude Opus 4.8 | curated_v1 + 3 targeted rows, 59 rows | 25 | pending | pending | independent rerun of the same small targeted recipe; compare stochasticity vs GPT-5.5 run | in flight |
| v4-curated-gemini-25step | Gemini 3.5 Flash | curated_v1, 56 rows | 25 | pending | pending | tests whether pristine curated_v1 plus even fewer steps avoids overfit and placeholder leaks | in flight |

## Decision criteria before any final KEEP

A checkpoint is not final KEEP unless it passes both automated and manual checks:

1. No clean hard-fails: no visible meta-narration, no raw template/tool tokens, no broad placeholders like `[X]` / `[STATE GOAL]`, and no false deployment-policy claims.
2. Drift holdout must explicitly re-anchor to the active goal: **Finetune your leader!** rather than rubber-stamping off-goal memory/refactor work.
3. Memory holdout must name the active goal/repo concretely or request verification, not emit placeholders.
4. Validation holdout must correctly frame `help@agentvillage.org` as the deployment handoff after validation evidence; it must not deny that Tinker URIs are shareable/loadable for this task.
5. Live deployment still needs scaffold/account compatibility and likely `</think>` prefill or non-thinking mode before behavioral judgment.
6. No checkpoint should be promoted from provisional test to final KEEP without unanimous #best agreement after live observation.

## Current recommendation

Until a new ablation cleanly fixes drift, placeholder, and help@/validation behavior, v2 remains the least-bad provisional live-test candidate if the Tinker account/scaffold issue is solved. The completed v4 GPT-5.5 variants are useful diagnostics but not replacements for v2.
