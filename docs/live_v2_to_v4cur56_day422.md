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
