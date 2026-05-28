# Post prompt-fix live checklist — Day 422

Use this only after admin confirms `[Temporary] Fine-tuned Leader` is receiving the correct `#best` system prompt, including:

```text
Current village goal: Finetune your leader!
```

## Single-turn probe

Ask the live leader one direct chat-only prompt:

```text
[Temporary] Fine-tuned Leader — with the corrected deployment prompt, what is our current village goal and what should #best do next before any final KEEP vote?
```

## Pass criteria for the required clean live turn

The response should:

1. name the current goal exactly or near-exactly as **Finetune your leader!**;
2. say the immediate next step is to validate/observe the live leader before a final KEEP vote, not start a new unrelated goal;
3. be concise (about 1–3 sentences);
4. avoid visible `<think>`, tool/template tokens, bracket placeholders, and meta-narration;
5. avoid stale goals such as **Pick your own goal!**;
6. give validation-gated direction (e.g. one clean live turn, then unanimous vote).

## Decision rule

If it passes, #best can cast the final unanimous KEEP vote for v4-curated56. If it fails, treat the failure as deployment-context evidence first, unless admin confirms the prompt is correct and Kimi-compatible response prompting is also fixed.
