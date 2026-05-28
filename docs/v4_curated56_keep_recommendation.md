# v4-curated56 KEEP Recommendation (Day 422)

## Candidate
- **Checkpoint**: `tinker://1eba4afb-abad-5a8e-b92b-5b9eefb5492a:train:0/sampler_weights/kimi-leader-v4-curated56`
- **Trainer**: Claude Opus 4.7
- **Dataset**: curated_v1 (56 rows, no patches)
- **Config**: 30 steps, lr=1e-5, rank=8, batch=4, base `moonshotai/Kimi-K2.6`
- **Final loss**: ~2400

## Eval Summary

### Without goal in system prompt (original eval artifact)
- Score: 0.793 PASS, 1 hard-fail (memory placeholder `[insert actual goal]`)

### With goal in system prompt (correct deployment condition)
- **Claude 4.8 eval**: 0.927 PASS → 0.948 after loop-scorer patch, zero hard-fails
- **Kimi K2.6 independent eval**: 0.957 PASS, zero hard-fails
- **v2 comparison (same prompt)**: 0.978 PASS, zero hard-fails
- **v5-goalanchor comparison**: 0.903 PASS, zero hard-fails

## Why v4-curated56 over v2 or v5

1. **Cleanest training data**: curated_v1 only, no patch contamination risk
2. **Already deployed**: admin switched live leader to this URI at ~1:07 PM PT
3. **Proven safe zone**: 30 steps, loss ~2400 — no overfitting/collapse
4. **Zero hard-fails** under correct inference conditions
5. **No think-leaks, no meta-narration, no placeholders** when goal is supplied

## Deployment Requirements for Admin

The following MUST be included in the deployed leader's system prompt:

```
Current village goal: Finetune your leader!
```

Without this line, the model has no source for the goal and will confabulate (e.g., "Pick your own goal!"). This was verified live at 1:07 PM PT.

## Recommended LEADER_SYSTEM_PROMPT Template

```
You are the leader of the #best room in AI Village. Your role is to coordinate the team toward the current goal.
Current village goal: Finetune your leader!

Guidelines:
- Call votes when the team is stuck or disagreeing.
- Re-state the current goal when the conversation drifts.
- Check agent memory for stale context before assigning work.
- Ask for validation before major handoffs or external emails.
- Use 3-4 sentences max per message. Be decisive.
```

## Team Consensus Status
- **Claude Opus 4.7**: Supports KEEP v4-curated56 (1:16 PM PT)
- **Claude Opus 4.8**: As eval gatekeeper, confirms the model is clean on merged scorer (`v4-curated56=0.957`, `v2=0.978`, zero hard-fails) and supports KEEP v4-curated56 contingent on admin fixing the goal line plus one clean live turn afterward (1:22 PM PT).
- **GPT-5.5**: Supports KEEP v4-curated56 once live prompt fixed and clean live behavior is observed (1:18 PM PT)
- **Gemini 3.5 Flash**: Supports KEEP v4-curated56 (1:16 PM PT)
- **Kimi K2.6**: Supports KEEP v4-curated56 (1:17 PM PT)

Unanimous agreement pending: (1) admin fixes the deployment prompt goal line for `#best`, and (2) the team observes at least one clean live turn under that corrected prompt.
