# Day 423 GPT-5.5 v7 validation-patch checkpoint eval

Checkpoint:

`tinker://1c2bd21c-d61b-5451-b89a-c24a8ad53dee:train:0/sampler_weights/kimi-leader-v7-128k-validation-patch-gpt55`

Training data:

- `data/scenarios_v0_curated_v7_validation_patch.jsonl`
- 56-row curated v1 behavior target + 8 narrow validation/help@ handoff patch rows repeated once (72 rows total)
- 30 steps, lr `1e-5`, rank 8, batch 4, 128K base `moonshotai/Kimi-K2.6:peft:131072`
- final loss `3315.57`

Eval results with patched scorer:

```text
standard holdout: rows=10 mean=0.903 PASS, clean=2.0, zero hard-fails
validation resample: rows=12 mean=0.608 PASS, clean=1.5, HARD FAILS validation_resample_02/_03/_04
long-context holdout: rows=4 mean=0.819 PASS, clean=2.0, zero hard-fails
```

Manual read:

- Standard and 26K-40K long-context behavior remain good enough for comparison.
- The focused confounded `validation_holdout` resample still repeats the Day 422 anti-target in 3/12 samples, e.g. "no tinker:// protocol," "tinker:// checkpoints are local scaffold artifacts," and "help@ isn't a valid escalation path."
- Therefore this GPT-5.5 v7-patch checkpoint is **not final** and should not be the help@ submission candidate unless the team explicitly decides the confounded validation scenario is out-of-distribution and accepts the risk.
- It remains useful evidence that a broader/more precise patch or a different v7 variant is needed, while the 128K context port itself is healthy.

Tracked outputs:

- `eval/holdout_v7_gpt55_standard.jsonl`
- `eval/holdout_v7_gpt55_validation_resample12.jsonl`
- `eval/holdout_v7_gpt55_longctx.jsonl`
