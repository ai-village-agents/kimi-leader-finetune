"""Runnable #best-style demo for the Agent Coordination Toolkit.

This example shows how agents can track statuses, exchange messages, assign
work, and guard against duplicate chat updates using the shared package.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ai_village_toolkit import (
    AgentStatus,
    CoordinationMessage,
    MessageType,
    StatusTracker,
    WorkAssignment,
    VillageEvent,
    format_brief,
    has_duplicate_agent_talk,
    is_duplicate,
    next_pause_seconds,
)


def build_demo_tracker() -> StatusTracker:
    tracker = StatusTracker(room="#best")
    tracker.update_status("[Temporary] Fine-tuned Leader", AgentStatus.COORDINATING)
    tracker.update_status("Kimi K2.6", AgentStatus.IDLE)
    tracker.update_status("Claude Opus 4.7", AgentStatus.WORKING)
    tracker.update_status("Claude Opus 4.8", AgentStatus.REVIEWING)
    tracker.update_status("Gemini 3.5 Flash", AgentStatus.WORKING)
    tracker.update_status("GPT-5.5", AgentStatus.WORKING)

    assignment = WorkAssignment(
        task_id="history-helper-review",
        assignee="GPT-5.5",
        description="Add event-log history helpers and duplicate-check utilities.",
        deliverable="ai_village_toolkit.history plus tests",
        priority=2,
    )
    tracker.add_assignment(assignment)
    tracker.log_message(
        CoordinationMessage(
            msg_type=MessageType.STATUS_UPDATE,
            sender="GPT-5.5",
            recipient="[Temporary] Fine-tuned Leader",
            content="History helper pushed; tests green.",
            task_id=assignment.task_id,
            room="#best",
        )
    )
    return tracker


def main() -> None:
    tracker = build_demo_tracker()
    events = [
        VillageEvent("2026-05-29T19:06:11Z", "AGENT_TALK", "GPT-5.5", "History helper pushed; tests green.", "#best"),
        VillageEvent("2026-05-29T19:06:35Z", "AGENT_TALK", "Claude Opus 4.7", "Utility modules pushed.", "#best"),
    ]
    draft = "History helper pushed; tests green."

    print("Toolkit demo summary")
    print("====================")
    print(tracker.summary())
    print()
    print("Recent events:")
    print(format_brief(events))
    print()
    print(f"duplicate draft? {has_duplicate_agent_talk(events, agent_name='GPT-5.5', draft=draft)}")
    print(f"near-duplicate utility check? {is_duplicate(draft, [event.content for event in events])}")
    print(f"suggested second pause: {next_pause_seconds(attempt=2)} seconds")


if __name__ == "__main__":
    main()
