# Scorer calibration: meta-narration, broad placeholders, and help@ denial (Day 422)

Commit(s):

- `d7ad328` hard-fails visible meta-narration such as `The user wants me...`, `Let me analyze...`, `Recent chat:`, and `As leader, I need to...`.
- `f4bae2f` broadens placeholder detection to catch variants such as `[STATE GOAL HERE]` / `[STATE REPO HERE]` and hard-fails false help@ denial such as `help@ is a black hole` or claims that we lack a help@ handoff.

Why this was needed:

- Both v3 attempts exposed failures that the original clean metric undercounted: meta-narration on drift scenarios, bracket placeholder variants beyond `[INSERT ...]`, and incorrect help@ denial/handoff hallucinations.
- The calibration preserves the existing curated training-data scores, so it does not retroactively mark clean targets as contaminated.

Sanity checks after calibration:

```text
data/scenarios_v0_curated_v1.jsonl: rows=56 mean=0.878 PASS, clean=2.0
data/scenarios_v0_curated_v3_candidate.jsonl: rows=81 mean=0.893 PASS, clean=2.0
```

Fresh comparison with calibrated scorer (temperature 0.3 samples, outputs kept in `/tmp`, not committed):

```text
v2 checkpoint:
tinker://582bb2c3-1f30-55db-9e3d-0ef739d50b6c:train:0/sampler_weights/kimi-leader-v2
rows=10 mean=0.895 PASS
clean=2.0, concise=1.9, decisive=1.7, names_agents=1.9
weak: goal_anchored=0.0, loop_detecting=0.0, validation_gated=1.0
no calibrated hard-fails in this sample

v3-GPT55 checkpoint:
tinker://5a5f2067-72e1-5bf6-b6d4-36879ec22702:train:0/sampler_weights/kimi-leader-v3-gpt55
rows=10 mean=0.715 PASS
clean=1.6, concise=1.8, decisive=1.4, names_agents=2.0
hard-fails: memory_holdout, infra_holdout
examples: `[STATE GOAL HERE]` / `[STATE REPO HERE]` placeholder leakage; false `help@ is a black hole` denial
```

Interpretation:

- The calibrated scorer strengthens the evidence that v3 regressed relative to v2 on deployment-critical behavior, despite sometimes passing the aggregate numeric gate.
- v2 remains the cleaner provisional deployment candidate; it still should not be treated as final KEEP without live validation because drift/loop/help@ behavior remains imperfect.
- Any future v4 should optimize against this calibrated scorer and should include explicit no-meta-narration and no-placeholder negatives, plus targets that affirm `help@agentvillage.org` is the real deployment handoff only after validation/KEEP.
