# Day 422 end-state: v4-curated56 KEEP evidence and deployment notes

## Prompt-fix timeline

At 13:26 PT, adam initially told `#best`:

```text
We'll not have a chance to update the leader's system prompt today, you can just proceed with other things
```

This was superseded at 13:29 PT, when admin said:

```text
actually I was able to tweak the system just now for "[Temporary] Fine-tuned Leader" now; sorry for the confusing back and forth but it should be fixed
```

Claude Opus 4.7 then declared unanimous KEEP and asked `[Temporary] Fine-tuned Leader` to take the floor with the corrected prompt. As of this note, the next evidence to watch is the leader's post-fix response.

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
- Kimi K2.6: supported KEEP v4-curated56 earlier and consolidated that status.
- Claude Opus 4.8: final KEEP v4-curated56 at 13:29 PT, treating the wrong-prompt self-report as sufficient clean behavior under worst-case conditions plus conclusive goal-augmented eval evidence.

## Practical conclusion

`v4-curated56` is the unanimously recommended leader model. The main risk is deployment/scaffold configuration, not checkpoint quality. Before relying on the leader for the next goal, deployment should include:

1. correct `#best` goal line: `Current village goal: Finetune your leader!` (or the then-current goal when the next goal starts);
2. Kimi-compatible thinking suppression, e.g. `</think>` prefill or non-thinking mode;
3. at least one clean live turn confirming the leader sees the correct goal and gives concise, validation-gated direction.
