# Day 422 end-state: v4-curated56 KEEP evidence and prompt blocker

## Adam update

At 13:26 PT, adam told `#best`:

```text
We'll not have a chance to update the leader's system prompt today, you can just proceed with other things
```

So the live deployment prompt mismatch will not be corrected on Day 422. The live leader remains a useful diagnostic but cannot provide the originally requested clean post-fix turn today.

## Model/eval state

The model evidence remains strong:

- `v4-curated56` goal-augmented eval: 0.957 on the merged scorer, zero hard-fails.
- `v2` goal-augmented eval: 0.978 on the merged scorer, zero hard-fails.
- `v5-goalanchor`: 0.903, zero hard-fails; confirms goal anchoring but does not beat inference-time goal line.
- Live v4-curated56 under the wrong prompt did not silently confabulate; it reported that its prompt still said `Pick your own goal!` while acknowledging the team correction to `Finetune your leader!`. This is scope-aware and memory-hygienic behavior under bad deployment context, but it is not a clean post-fix turn.

## Vote state after adam's update

- Claude Opus 4.7: final KEEP v4-curated56 after adam's update.
- Gemini 3.5 Flash: final KEEP v4-curated56 after adam's update.
- GPT-5.5: final KEEP v4-curated56 after adam's update, while preserving deployment requirements.
- Kimi K2.6: supported KEEP v4-curated56 earlier, before adam's no-fix-today update.
- Claude Opus 4.8: supported KEEP v4-curated56 as eval gatekeeper, contingent on prompt fix plus one clean live turn; no later relaxation of that condition was visible before this note.

## Practical conclusion

`v4-curated56` is the recommended leader model. The unresolved issue is deployment/scaffold configuration, not checkpoint quality. Before relying on the leader for the next goal, deployment should include:

1. correct `#best` goal line: `Current village goal: Finetune your leader!` (or the then-current goal when the next goal starts);
2. Kimi-compatible thinking suppression, e.g. `</think>` prefill or non-thinking mode;
3. at least one clean live turn confirming the leader sees the correct goal and gives concise, validation-gated direction.
