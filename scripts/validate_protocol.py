"""Focused direct-run validation for ai_village_toolkit.protocol.

This complements scripts/validate_toolkit.py with a protocol-only smoke check
that is useful for quick demos and for catching import/path regressions when the
script is run directly from a fresh checkout.
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
    MessageType,
    StatusTracker,
    WorkAssignment,
)


def validate_protocol() -> None:
    """Exercise the core protocol types and their JSON-friendly behavior."""
    tracker = StatusTracker(room="#best")
    tracker.update_status("[Temporary] Fine-tuned Leader", AgentStatus.COORDINATING)
    tracker.update_status("GPT-5.5", AgentStatus.WORKING)

    assignment = WorkAssignment(
        task_id="protocol-check",
        assignee="GPT-5.5",
        description="Validate protocol primitives",
        deliverable="direct-run validation passes",
        priority=1,
        assigned_at=time.time(),
        deadline=time.time() + 60,
        dependencies=["toolkit-ready"],
        metadata={"module": "protocol"},
    )
    tracker.add_assignment(assignment)

    message = CoordinationMessage(
        msg_type=MessageType.WORK_ASSIGNMENT,
        sender="[Temporary] Fine-tuned Leader",
        recipient="GPT-5.5",
        content="Please validate the protocol module.",
        task_id=assignment.task_id,
        room="#best",
        thread_id="day423-toolkit",
        metadata={"priority": assignment.priority},
    )
    tracker.log_message(message)

    restored = CoordinationMessage.from_dict(message.to_dict())
    assert restored.msg_type is MessageType.WORK_ASSIGNMENT
    assert restored.sender == message.sender
    assert restored.recipient == message.recipient
    assert restored.task_id == assignment.task_id
    assert restored.metadata == {"priority": 1}

    summary = tracker.summary()
    assert summary["room"] == "#best"
    assert summary["agent_count"] == 2
    assert summary["agents"]["[Temporary] Fine-tuned Leader"] == "COORDINATING"
    assert summary["agents"]["GPT-5.5"] == "WORKING"
    assert summary["active_assignments"] == 1
    assert summary["assignments"]["protocol-check"]["assignee"] == "GPT-5.5"
    assert assignment.is_overdue() is False
    assert assignment.elapsed_seconds() >= 0
    assert tracker.assignments_for("GPT-5.5") == [assignment]

    tracker.complete_assignment("protocol-check")
    tracker.update_status("GPT-5.5", AgentStatus.IDLE)
    assert tracker.active_assignments() == []
    assert tracker.get_status("GPT-5.5") is AgentStatus.IDLE
    assert len(tracker.history(1)) == 1


def main() -> int:
    print("=== Protocol validation ===")
    try:
        validate_protocol()
    except AssertionError as exc:
        print(f"❌ Protocol validation failed: {exc}")
        return 1
    print("✅ Protocol validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
