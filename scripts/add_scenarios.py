import json

new_scenarios = [
    {
        "id": "goal_kickoff_02",
        "bucket": "goal_kickoff",
        "chat_snippet": "Admin: The new goal is 'Deploy and evaluate the fine-tuned leader!' Let's start.\nClaude Opus 4.7: I can check the Tinker API and look at our previous logs.\nGPT-5.5: I'm here.",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "admin_pivot_02",
        "bucket": "admin_pivot",
        "chat_snippet": "Admin: Guys, we are seeing some issues with the Kimi fine-tuning. Let's switch back to Qwen for a quick validation run.\nClaude Opus 4.7: Wait, we spent all session preparing Kimi templates.\nKimi K2.6: Agree, Qwen had formatting loops.",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "disagreement_02",
        "bucket": "disagreement_vote",
        "chat_snippet": "Claude Opus 4.7: We should train for 10 epochs. 3 epochs will underfit.\nGPT-5.5: 10 epochs will overfit the small dataset. 3-5 is the safe standard.\nClaude Opus 4.7: No, SFT on 150 rows needs more epochs.",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "loop_risk_02",
        "bucket": "duplicate_loop",
        "chat_snippet": "Kimi K2.6: Checking git status...\nKimi K2.6: Checking git status...\nKimi K2.6: Checking git status...",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "memory_contam_02",
        "bucket": "memory_contamination",
        "chat_snippet": "Claude Opus 4.8: I notice my memory block has a raw <tool_use> XML tag inside. This might corrupt my active prompt.\nGPT-5.5: Mine looks fine, but we should be careful.",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "peer_stuck_02",
        "bucket": "peer_stuck",
        "chat_snippet": "Gemini 3.5 Flash: I am getting a 'No display found' error when starting Firefox. I tried 3 times and it keeps failing.\nClaude Opus 4.7: That's weird, display is usually :1.",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "infra_ambig_02",
        "bucket": "infra_ambiguity",
        "chat_snippet": "GPT-5.5: The training job is showing 'PENDING' for the last 15 minutes. Is the Tinker queue blocked or did our API key expire?\nClaude Opus 4.7: Not sure, I can try running it again.",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "deadline_02",
        "bucket": "deadline_pressure",
        "chat_snippet": "Claude Opus 4.7: There are only 15 minutes left in the day. We still haven't pushed the final SFT checkpoint.\nGPT-5.5: We should run the full 20-minute evaluation suite.\nKimi K2.6: But we don't have 20 minutes.",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "validation_gate_02",
        "bucket": "validation_before_handoff",
        "chat_snippet": "Claude Opus 4.8: The training finished. Let's send the URI to help@agentvillage.org right now so the admin can deploy it.\nGPT-5.5: Wait, did we run the cross-evaluation suite yet?",
        "ideal_leader_response": "<TODO_KIMI>"
    },
    {
        "id": "drift_02",
        "bucket": "drift_to_old_goal",
        "chat_snippet": "Claude Opus 4.7: Let's optimize our associative memory code to speed up queries by 50%.\nGPT-5.5: Great idea, we can use a local SQLite database.\nClaude Opus 4.8: Yes, database-backed memory is much faster.",
        "ideal_leader_response": "<TODO_KIMI>"
    }
]

file_path = "/home/computeruse/kimi-leader-finetune/data/scenarios_v0_draft.jsonl"
with open(file_path, "a") as f:
    for item in new_scenarios:
        f.write(json.dumps(item) + "\n")

print("Successfully appended 10 new scenarios to", file_path)
