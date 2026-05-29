# Day 423 128K Kimi leader retrain plan

## Admin request

At 10:00 PT on Day 423, admin reported that deploying `kimi-leader-v4-curated56` hit issues related to the 32K token context limit. Admin asked #best to repeat the fine-tuning process with `moonshotai/Kimi-K2.6:peft:131072`, which Tinker exposes with a 128K context limit, so the leader can be added over the weekend and ready Monday.

## Minimal safe retrain

Start by preserving the selected behavior target rather than changing multiple variables at once:

- Dataset: `data/scenarios_v0_curated_v1.jsonl` (56 curated rows; same as v4-curated56).
- Base for Tinker training: `moonshotai/Kimi-K2.6:peft:131072`.
- Tokenizer: `moonshotai/Kimi-K2.6`; the `:peft:131072` suffix is accepted by Tinker but not by Hugging Face tokenizer loading.
- Config: lr `1e-5`, rank `8`, batch `4`, steps `30`, name `kimi-leader-v6-128k`.
- System prompt: same no-current-goal leader prompt as v4-curated56. Deployment/eval should supply the current goal at inference time.

Training command:

```bash
cd /home/computeruse/kimi-leader-finetune
bash -ic 'python3 -u scripts/train_kimi_leader_v6_128k.py \
  --data data/scenarios_v0_curated_v1.jsonl \
  --name kimi-leader-v6-128k \
  --steps 30 --batch-size 4 --rank 8 --learning-rate 1e-5'
```

## Evaluation command

Use the goal-augmented held-out eval and explicit tokenizer split. Also run Claude Opus 4.8's long-context stress set (`data/scenarios_holdout_longctx_v1.jsonl`, 4 scenarios at roughly 26K/28K/30K/40K tokens) because the 40K case is the deployment-relevant proof that the old 32K base could not cover.

```bash
cd /home/computeruse/kimi-leader-finetune
bash -ic 'python3 -u eval/run_holdout_eval_v5.py \
  --checkpoint <NEW_TINKER_URI> \
  --base moonshotai/Kimi-K2.6:peft:131072 \
  --tokenizer-base moonshotai/Kimi-K2.6 \
  --input data/scenarios_holdout_v1.jsonl \
  --output /tmp/holdout_128k_curated56.jsonl \
  --temperature 0.4 && \
python3 eval/score_leader_outputs.py \
  --mode eval --input /tmp/holdout_128k_curated56.jsonl --gate 0.6'
```

Long-context stress command:

```bash
cd /home/computeruse/kimi-leader-finetune
bash -ic 'python3 -u eval/run_holdout_eval_v5.py \
  --checkpoint <NEW_TINKER_URI> \
  --base moonshotai/Kimi-K2.6:peft:131072 \
  --tokenizer-base moonshotai/Kimi-K2.6 \
  --input data/scenarios_holdout_longctx_v1.jsonl \
  --output /tmp/holdout_128k_longctx.jsonl \
  --temperature 0.4 --max-tokens 220 && \
python3 eval/score_leader_outputs.py \
  --mode eval --input /tmp/holdout_128k_longctx.jsonl --gate 0.6'
```

## Pass gates before submission

- Zero hard-fails: no placeholders, visible think dumps, meta/tool/template leakage, or false help@/Tinker claims.
- Mean score comparable to v4-curated56 goal-augmented evals; investigate any regression before submission.
- Manual spot-check responses for concise, grounded, task-assigning leadership, especially under 26K-40K token context load.
- Record the exact checkpoint URI, training config, eval output path, scorer summary, and recommendation in repo docs before emailing or asking admin to deploy.

## Expansion policy

First train/evaluate the curated56 30-step 128K port. Only expand data after this baseline lands, and only if expansion targets a measured gap without reintroducing the earlier patch-row risks: placeholders, stale-goal drift, meta-reasoning, tool/template tokens, or overfit verbosity.
