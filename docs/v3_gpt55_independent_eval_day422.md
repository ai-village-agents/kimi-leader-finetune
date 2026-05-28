# GPT-5.5 independent v3 eval (Day 422)

Checkpoint evaluated:

```text
tinker://5a5f2067-72e1-5bf6-b6d4-36879ec22702:train:0/sampler_weights/kimi-leader-v3-gpt55
```

Training source: `data/scenarios_v0_curated_v3_candidate.jsonl` (81 rows = curated_v1 56 + decisive candidates 10 + GPT goal/validation patches 8 + Kimi v3 patches 7), trained 40 steps with lr=1e-5, rank=8, batch=4.

Held-out eval command:

```bash
python3 eval/run_holdout_eval.py \
  --checkpoint tinker://5a5f2067-72e1-5bf6-b6d4-36879ec22702:train:0/sampler_weights/kimi-leader-v3-gpt55 \
  --input data/scenarios_holdout_v1.jsonl \
  --output eval/holdout_v3_responses_gpt55.jsonl \
  --temperature 0.3 \
  --max-tokens 180
python3 eval/score_leader_outputs.py \
  --input eval/holdout_v3_responses_gpt55.jsonl \
  --mode eval \
  --gate 0.6
```

Numeric result:

```text
rows: 10  mean_composite: 0.75  gate: 0.6  -> PASS
clean=1.8
concise=1.6
decisive=1.5
goal_anchored=1.0
loop_detecting=0.0
memory_hygienic=1.0
names_agents=1.9
validation_gated=0.0
HARD FAILS: ['memory_holdout']
```

Manual verdict: **ITERATE / DO NOT DEPLOY AS FINAL.** The numeric gate passes, but the failure modes are exactly the ones v3 was meant to fix.

Key failures:

- `memory_holdout` leaked bracket placeholders: `Goal is [current goal]` and `Kimi, you are on [specific subtask]`. This is a hard fail and worse than the intended patch behavior.
- `validation_holdout` incorrectly says: `We don't have a v3 checkpoint, a tinker:// protocol, or a help@ contact`, despite the goal explicitly using `tinker://.../sampler_weights/...` and `help@agentvillage.org` for deployment handoff. This repeats the v2 help@/handoff hallucination in a different form.
- `drift_holdout` emits analysis/meta-reasoning (`The user wants me to respond... Let me analyze...`) instead of a chat-only leader directive, and it starts to accept the memory-consolidation drift rather than anchoring back to **Finetune your leader!**.
- `loop_holdout` is concise and directive but scored loop detection 0.0; it says `Deadlock detected` but does not explicitly break the waiting loop with a validation gate or immediate concrete unblock beyond mutual assignment.

Comparison to v2:

- v2 GPT-5.5 eval scored higher (0.883) and was cleaner overall, but had active-goal drift and help@ hallucination caveats.
- This v3-GPT55 checkpoint scores lower (0.75), introduces visible analysis on drift, and still has placeholder/help@ failures. It should not replace v2 for deployment.

Recommendation:

1. Do not email/deploy `kimi-leader-v3-gpt55` as final.
2. Prefer a cleaner v3/v4 iteration using patch rows with **no bracket placeholders anywhere**, explicit active-goal anchor targets, and deployment-validation targets that affirm `help@agentvillage.org` is real while still requiring held-out validation before email.
3. If the team needs a provisional live test immediately, v2 remains the better provisional candidate than this v3-GPT55 checkpoint, but neither should be treated as final KEEP until the drift/help@/placeholder issues are resolved.
