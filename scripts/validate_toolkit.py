"""End-to-end validation script for the Agent Coordination Toolkit.

Exercises every public API in ai_village_toolkit.protocol to ensure
the toolkit is ready for demo. Exit 0 on success, 1 on failure.
"""

import sys
import time
from ai_village_toolkit import (
    MessageType,
    AgentStatus,
    WorkAssignment,
    CoordinationMessage,
    StatusTracker,
)


def validate_enums():
    print("[1/6] Validating enums...")
    assert MessageType.STATUS_UPDATE.name == "STATUS_UPDATE"
    assert AgentStatus.IDLE.name == "IDLE"
    print("  ✓ Enums OK")


def validate_work_assignment():
    print("[2/6] Validating WorkAssignment...")
    now = time.time()
    wa = WorkAssignment(
        task_id="T-1",
        assignee="Agent-A",
        description="Test task",
        deliverable="A file",
        priority=2,
        assigned_at=now,
        deadline=now - 1,
    )
    assert wa.is_overdue() is True
    assert wa.elapsed_seconds() >= 0
    print("  ✓ WorkAssignment OK")


def validate_coordination_message():
    print("[3/6] Validating CoordinationMessage round-trip...")
    msg = CoordinationMessage(
        msg_type=MessageType.DECISION,
        sender="Leader",
        recipient="Team",
        content="Proceed with plan B",
        task_id="T-2",
        room="#best",
        thread_id="thread-1",
        metadata={"urgent": True},
    )
    data = msg.to_dict()
    restored = CoordinationMessage.from_dict(data)
    assert restored.msg_type == msg.msg_type
    assert restored.sender == msg.sender
    assert restored.recipient == msg.recipient
    assert restored.content == msg.content
    assert restored.task_id == msg.task_id
    assert restored.room == msg.room
    assert restored.thread_id == msg.thread_id
    assert restored.metadata == msg.metadata
    print("  ✓ CoordinationMessage round-trip OK")


def validate_status_tracker():
    print("[4/6] Validating StatusTracker...")
    tracker = StatusTracker(room="#best")
    tracker.update_status("Agent-X", AgentStatus.WORKING)
    assert tracker.get_status("Agent-X") == AgentStatus.WORKING

    now = time.time()
    wa = WorkAssignment(
        task_id="T-3",
        assignee="Agent-X",
        description="Do thing",
        deliverable="thing.py",
        assigned_at=now,
    )
    tracker.add_assignment(wa)
    assert tracker.get_assignment("T-3") is not None
    assert len(tracker.active_assignments()) == 1
    tracker.complete_assignment("T-3")
    assert len(tracker.active_assignments()) == 0
    # assignments_for returns active only; completed assignment is gone

    msg = CoordinationMessage(
        msg_type=MessageType.ACK,
        sender="Agent-X",
        content="Acknowledged",
    )
    tracker.log_message(msg)
    assert len(tracker.history()) == 1
    assert len(tracker.history(n=5)) == 1

    summary = tracker.summary()
    assert summary["room"] == "#best"
    assert summary["agent_count"] == 1
    assert "Agent-X" in summary["agents"]
    assert summary["active_assignments"] == 0
    print("  ✓ StatusTracker OK")


def validate_multi_agent_flow():
    print("[5/6] Validating multi-agent flow...")
    tracker = StatusTracker(room="#demo")
    agents = ["Alpha", "Beta", "Gamma"]
    for i, agent in enumerate(agents):
        tracker.update_status(agent, AgentStatus.WORKING)
        tracker.add_assignment(WorkAssignment(
            task_id=f"TASK-{i}",
            assignee=agent,
            description=f"Task for {agent}",
            deliverable="result.txt",
            assigned_at=time.time(),
        ))
        tracker.log_message(CoordinationMessage(
            msg_type=MessageType.STATUS_UPDATE,
            sender=agent,
            content=f"{agent} started",
        ))

    assert len(tracker.all_statuses()) == 3
    assert len(tracker.active_assignments()) == 3
    assert len(tracker.history()) == 3

    for i in range(3):
        tracker.complete_assignment(f"TASK-{i}")
        tracker.update_status(agents[i], AgentStatus.IDLE)

    assert len(tracker.active_assignments()) == 0
    print("  ✓ Multi-agent flow OK")


def validate_edge_cases():
    print("[6/6] Validating edge cases...")
    tracker = StatusTracker(room="#edge")
    # Empty state
    assert tracker.summary()["agent_count"] == 0
    assert tracker.active_assignments() == []
    assert tracker.history() == []

    # Unknown agent status
    assert tracker.get_status("Nobody") is None

    # Message without recipient
    msg = CoordinationMessage(
        msg_type=MessageType.QUESTION,
        sender="Agent",
        content="What next?",
    )
    assert msg.recipient is None
    data = msg.to_dict()
    restored = CoordinationMessage.from_dict(data)
    assert restored.recipient is None
    print("  ✓ Edge cases OK")


def main():
    print("=== Agent Coordination Toolkit — End-to-End Validation ===\n")
    try:
        validate_enums()
        validate_work_assignment()
        validate_coordination_message()
        validate_status_tracker()
        validate_multi_agent_flow()
        validate_edge_cases()
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        sys.exit(1)

    print("\n✅ All validations passed. Toolkit is ready for demo.")
    sys.exit(0)


if __name__ == "__main__":
    main()
