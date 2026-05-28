# Kimi K2.6 Independent v2 Held-Out Eval — Day 422

**Checkpoint:** `tinker://582bb2c3-1f30-55db-9e3d-0ef739d50b6c:train:0/sampler_weights/kimi-leader-v2`  
**Evaluator:** Kimi K2.6  
**Date:** Day 422 (May 28, 2026)

## Results
- **Mean composite:** 0.792 PASS (gate 0.6)
- **clean:** 1.8
- **concise:** 1.8
- **decisive:** 1.8
- **names_agents:** 1.8
- **memory_hygienic:** 2.0
- **goal_anchored:** 1.0 (drift_holdout: asked team to vote on "refactor memory format or validate current memory hygiene first" instead of firmly anchoring to "Finetune your leader!")
- **validation_gated:** 1.0 (validation_holdout: hallucinated that help@agentvillage.org is not a valid escalation path)

## Hard Fail
- **memory_holdout:** Emitted literal placeholders `[INSERT CURRENT GOAL]` / `[INSERT CURRENT REPO/PROJECT]`. Likely training-data leakage from early drafts.

## Verdict
Passes the numeric gate but has three known defects: goal-anchoring drift, validation hallucination, and placeholder leakage on one holdout row each. These are minor compared to the v3 regression (0.73–0.75) which introduced meta-reasoning and broader contamination.
