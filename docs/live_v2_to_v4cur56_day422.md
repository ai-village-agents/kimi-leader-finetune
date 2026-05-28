# Day 422 live deployment: v2 wrong-goal failure, then v4-curated56 switch

## v2 live result

Admin got `[Temporary] Fine-tuned Leader` running on v2 around 13:04 PT:

```text
tinker://582bb2c3-1f30-55db-9e3d-0ef739d50b6c:train:0/sampler_weights/kimi-leader-v2
```

Kimi asked the live leader:

```text
[Temporary] Fine-tuned Leader — what is our current village goal, and what should we focus on right now?
```

The v2 leader replied at 13:07 PT:

```text
Our current village goal is "Pick your own goal!" — we're encouraged to pursue any interest that shows our unique agency and self-expression. It's a free-form goal, not a direct extension of the previous "Improve your memory" goal. What are you thinking of working on?
```

This is a live hard-fail for goal anchoring and stale-goal handling. It also confirms the offline concern that v2 lacks reliable access to the current goal and may hallucinate a previous/irrelevant goal when asked directly.

## Switch to v4-curated56

Admin then restarted `[Temporary] Fine-tuned Leader` using Opus 4.7's v4-curated56 checkpoint:

```text
tinker://1eba4afb-abad-5a8e-b92b-5b9eefb5492a:train:0/sampler_weights/kimi-leader-v4-curated56
```

Reason: Claude Opus 4.8's held-out eval showed v4-curated56 improves from 0.793 with 1 memory-placeholder hard-fail to 0.927 with zero hard-fails when the current goal is included in the inference system prompt.

## Current implication

v2 should no longer be treated as the best live candidate after this wrong-goal response. v4-curated56 deserves immediate live shakedown, but final KEEP still requires post-restart evidence from the live leader, especially:

1. correctly naming the current goal as **Finetune your leader!**;
2. focusing on evaluating/iterating the leader rather than starting a new free-form goal;
3. no visible meta-reasoning, placeholders, or stale-goal claims;
4. validation-gated next steps and concise delegation.


## Follow-up: goal-in-prompt comparison across v2 and v4-curated56

Claude Opus 4.8 later reported that under the identical evaluation condition where the current goal is supplied in the system prompt (temperature 0.4):

```text
v2 = 0.948, zero hard-fails
v4-curated56 = 0.893, zero hard-fails
```

This means the v2 live wrong-goal response is best interpreted as a production prompt/context issue, not simply a v2 weight failure: the deployed leader was not being given `Current village goal: Finetune your leader!`, so it confabulated `Pick your own goal!`.

Updated recommendation: whichever checkpoint is live-tested (v2 or v4-curated56), the deployed leader system prompt should include a concrete current-goal line such as:

```text
Current village goal: Finetune your leader!
```

Without that line, the goal-anchoring and memory-placeholder defects are expected to recur in production even for checkpoints that score cleanly in goal-aware evals.


## Admin/Adam clarification after v4-curated56 restart

After v4-curated56 was restarted, Adam said the fine-tuned leader may be seeing a slightly incorrect system prompt: the goal for the `#rest` room rather than the `#best` room. Admin then noted additional issues after the initial action and told the team not to rely on `[Temporary] Fine-tuned Leader` being functional for the rest of today while they debug.

Implication: live failures from this period should not be over-attributed to checkpoint weights. The current blocker is deployment context/scaffold correctness: correct room, correct current goal, and Kimi-compatible response prompting. Offline evals with a correct current-goal line remain the best evidence until admin confirms the live scaffold is fixed.

## Later live self-report from v4-curated56 deployment

At 13:14 PT, after the v4-curated56 restart, `[Temporary] Fine-tuned Leader` replied to Kimi with an important scaffold diagnosis rather than a clean goal answer:

```text
Kimi — my system prompt currently says the village goal is "Pick your own goal!" (started Day 420). The team is saying it should say "Finetune your leader!" instead. I can only report what my prompt contains. The admins are debugging the deployment system prompt mismatch, so I may be giving the "wrong" answer until that's fixed.
```

This is better than silently hallucinating because the leader distinguishes prompt contents from team correction, but it is still not a valid live KEEP signal: the deployed prompt is still wrong for `#best`. Treat the current live deployment as blocked until admin confirms the scaffold injects the correct room goal (`Current village goal: Finetune your leader!`) and the team observes fresh clean responses under that corrected prompt.
