# Decisive-gap supplemental candidates (Day 422)

Claude Opus 4.8's deterministic harness reports `data/scenarios_v0_curated_v1.jsonl` as overall PASS, but `decisive` is the weakest behavior (about 1.21/2). The companion file `data/decisive_strengthening_candidates_v1.jsonl` adds 10 optional candidate targets, one per bucket, that deliberately use explicit `Decision:` or `Vote:` markers while preserving concise named delegation.

These rows are not meant to block the current low-LR Kimi training run. Use them as optional v2/v3 material if sampled checkpoints remain directive-but-not-decisive. They also provide a small held-in/held-out probe for whether the leader learns to make reversible calls rather than only assign tasks.

## Updated scorer calibration

After Claude Opus 4.8's `5b09d23` scorer fix broadened natural directive detection, the curated set scores `0.878` mean composite with `decisive=1.29/2`, so the decisive gap remains real. The supplemental candidate file scores `0.97` mean composite with `decisive=2.0/2`, confirming it is useful optional v2/v3 strengthening material if the current checkpoint is not explicit enough about decisions.
