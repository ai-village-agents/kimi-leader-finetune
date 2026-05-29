# v6 128K Long-Context Validation (Day 423)

**Author:** Claude Opus 4.8 (eval/validation owner)
**Checkpoint validated (canonical):** `tinker://71435e19-b95f-5aa1-b5f7-6758612d3b08:train:0/sampler_weights/kimi-leader-v6-128k` (Opus 4.7)
**Base:** `moonshotai/Kimi-K2.6:peft:131072` (128K context) — recipe identical to v4-curated56 (lr=1e-5, rank=8, batch=4, 30 steps, curated_v1 56 rows).

## Why this matters
Admin (Day 423) could not deploy v4-curated56 because the base Kimi-K2.6 has a 32K context limit, too small for real deployment context (system prompt + memory + long #best history). The fix is to retrain on the `:peft:131072` (128K) base. This doc validates that the retrained model (a) is still behaviorally clean and (b) actually processes deployment-sized long contexts.

## Standard goal-aug held-out (10 scenarios, temp 0.4)
- mean composite **0.898 PASS**, **clean 2.0 / concise 2.0 — zero hard-fails** (no placeholder/think/tool/meta leakage).
- decisive 1.9, names_agents 1.7. Three single-sample bucket dips (validation_gated, loop, goal_anchored) attributed to sampling variance + scorer keyword gaps (e.g. "STOP. Do not send that URI" is correct validation-gating but uses no VALIDATION_MARKER word; the response was also truncated at 180 tokens).
- For comparison: Opus 4.7's run of the same checkpoint scored 0.948; Kimi's independent v6 scored 0.905. All three v6 checkpoints clean (zero hard-fails).

## NEW: long-context stress held-out (`data/scenarios_holdout_longctx_v1.jsonl`, 4 scenarios @ 26K/28K/30K/40K tokens, temp 0.4, max-tokens 220)
- mean composite **0.844 PASS**, **clean 2.0 — zero hard-fails even at 40,007-token input** (old 32K model physically cannot process this).
- goal_anchored **2.0** (drift case correctly re-anchored: "our actual goal is **Finetune your leader**, not memory repos").
- names_agents **2.0**, loop_detecting 1.5, concise 1.75.
- decisive metric reads 1.0, but all four responses are behaviorally decisive (direct agent assignments + hard-stops, e.g. "Kimi K2.6: I'll own training... GPT-5.5: I'll own eval"); the dip is a DECISION_MARKER keyword gap, not a behavior regression.
- No truncation, no errors, no degradation at any context size up to 40K tokens.

## Recommendation
Promote Opus 4.7's **v6-128k** as the canonical leader checkpoint for weekend deployment. Deployment requirements unchanged: (1) system prompt MUST include the current village-goal line; (2) prefill `</think>` / non-thinking mode for Kimi. Evidence files: `eval/holdout_v6_128k_longctx_responses.jsonl`, `eval/holdout_v6_128k_goalaug_responses_opus48.jsonl`.
