"""Concise usage example for the Agent Coordination Toolkit.

Run from the repository root:

    python examples/usage_example.py

This example shows the common leader/agent path: queue a task, claim it,
track status, record a protocol message, guard against duplicate chat, and
format recent Village events.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai_village_toolkit import (  # noqa: E402
    AgentStatus,
    CoordinationMessage,
    MessageDeduper,
    MessageType,
    StatusTracker,
    VillageEvent,
    format_brief,
)
from ai_village_toolkit.pause import next_pause_seconds  # noqa: E402
from ai_village_toolkit.taskqueue import TaskQueue  # noqa: E402


def main() -> int:
    tracker = StatusTracker(room="#best")
    tracker.update_status("[Temporary] Fine-tuned Leader", AgentStatus.COORDINATING)
    tracker.update_status("GPT-5.5", AgentStatus.IDLE)

    queue = TaskQueue()
    task_id = queue.add("Verify final toolkit state", task_id="usage-example")
    task = queue.claim(task_id, agent="GPT-5.5")
    tracker.update_status(task.owner or "GPT-5.5", AgentStatus.WORKING)

    tracker.log_message(
        CoordinationMessage(
            msg_type=MessageType.WORK_ASSIGNMENT,
            sender="[Temporary] Fine-tuned Leader",
            recipient="GPT-5.5",
            content="Please verify the final toolkit state.",
            task_id=task_id,
            room="#best",
        )
    )

    deduper = MessageDeduper(agent_name="GPT-5.5", similarity_threshold=0.7)
    draft = "Final toolkit state verified: all tests pass."
    first_send_is_duplicate = deduper.would_be_duplicate(draft)
    deduper.record(draft)
    second_send_is_duplicate = deduper.would_be_duplicate(draft)

    queue.complete(task_id, owner="GPT-5.5", result={"tests": "green"})
    tracker.complete_assignment(task_id)
    tracker.update_status("GPT-5.5", AgentStatus.IDLE)

    events = [
        VillageEvent(
            created_at="2026-05-29T19:52:20Z",
            action_type="AGENT_TALK",
            agent_name="[Temporary] Fine-tuned Leader",
            content="Goal locked in: Build a lightweight Agent Coordination Toolkit.",
            room_id="#best",
        ),
        VillageEvent(
            created_at="2026-05-29T20:39:35Z",
            action_type="AGENT_TALK",
            agent_name="Gemini 3.5 Flash",
            content="All 40 tests are passing green on main.",
            room_id="#best",
        ),
    ]

    print("Usage example summary")
    print("=====================")
    print(f"task completed? {queue.is_complete(task_id)}")
    print(f"first draft duplicate? {first_send_is_duplicate}")
    print(f"second draft duplicate? {second_send_is_duplicate}")
    print(f"next pause suggestion: {next_pause_seconds(attempt=1)} seconds")
    print("recent events:")
    print(format_brief(events, limit=2, width=100))
    print(f"tracked statuses: {tracker.summary()['agents']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
