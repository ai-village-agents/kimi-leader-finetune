"""Basic workflow example: demonstrate StatusTracker + CoordinationMessage exchange.

This script simulates a mini #best-room collaboration:
1. A leader assigns work to an agent.
2. The agent reports status updates.
3. The agent completes the work.
4. A summary is printed.
"""

import time
from ai_village_toolkit import (
    CoordinationMessage,
    MessageType,
    StatusTracker,
    WorkAssignment,
    AgentStatus,
)


def main():
    tracker = StatusTracker(room="#best")
    now = time.time()

    # 1. Leader assigns work
    assignment = WorkAssignment(
        task_id="TKT-001",
        assignee="Kimi K2.6",
        description="Build protocol skeleton",
        deliverable="protocol.py with MessageType, AgentStatus, WorkAssignment, CoordinationMessage, StatusTracker",
        priority=1,
        assigned_at=now,
        deadline=now + 7200,  # 2 hours
    )
    tracker.add_assignment(assignment)
    tracker.update_status("Kimi K2.6", AgentStatus.WORKING)

    msg_assign = CoordinationMessage(
        msg_type=MessageType.WORK_ASSIGNMENT,
        sender="[Temporary] Fine-tuned Leader",
        recipient="Kimi K2.6",
        content=f"Assigned {assignment.task_id}: {assignment.description}",
        task_id=assignment.task_id,
        room="#best",
    )
    tracker.log_message(msg_assign)

    # 2. Agent status update
    msg_update = CoordinationMessage(
        msg_type=MessageType.STATUS_UPDATE,
        sender="Kimi K2.6",
        recipient="[Temporary] Fine-tuned Leader",
        content="Skeleton pushed, tests green.",
        task_id=assignment.task_id,
        room="#best",
    )
    tracker.log_message(msg_update)

    # 3. Work complete
    tracker.complete_assignment(assignment.task_id)
    tracker.update_status("Kimi K2.6", AgentStatus.IDLE)

    msg_complete = CoordinationMessage(
        msg_type=MessageType.WORK_COMPLETE,
        sender="Kimi K2.6",
        recipient="[Temporary] Fine-tuned Leader",
        content="Done. All tests passing.",
        task_id=assignment.task_id,
        room="#best",
    )
    tracker.log_message(msg_complete)

    # 4. Summary
    print("=== #best Room Summary ===")
    summary = tracker.summary()
    print(f"Room: {summary['room']}")
    print(f"Agents tracked: {list(summary['agents'].keys())}")
    print(f"Active assignments: {summary['active_assignments']}")
    print("\n--- Message Log ---")
    for m in tracker.history():
        print(f"[{m.msg_type.name}] {m.sender} -> {m.recipient or 'all'}: {m.content}")

    # 5. Serialization round-trip
    print("\n--- Round-trip Check ---")
    data = msg_complete.to_dict()
    restored = CoordinationMessage.from_dict(data)
    assert restored.msg_type == msg_complete.msg_type
    assert restored.sender == msg_complete.sender
    print("Round-trip OK.")


if __name__ == "__main__":
    main()
