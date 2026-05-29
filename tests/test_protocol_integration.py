"""Integration tests for ai_village_toolkit.protocol (Kimi K2.6's deliverable).

Owner: Claude Opus 4.8 (review + integration testing).
Exercises the real public API: MessageType, AgentStatus, WorkAssignment,
CoordinationMessage (round-trip serialization), and StatusTracker lifecycle.
"""
import time

from ai_village_toolkit import (
    MessageType,
    AgentStatus,
    WorkAssignment,
    CoordinationMessage,
    StatusTracker,
)


def test_top_level_exports_present():
    for obj in (MessageType, AgentStatus, WorkAssignment, CoordinationMessage, StatusTracker):
        assert obj is not None


def test_work_assignment_overdue_and_elapsed():
    past = WorkAssignment(task_id="t1", assignee="Kimi K2.6", description="d",
                          deliverable="done", deadline=time.time() - 10)
    assert past.is_overdue() is True
    no_deadline = WorkAssignment(task_id="t2", assignee="Gemini 3.5 Flash",
                                 description="d", deliverable="done")
    assert no_deadline.is_overdue() is False
    assert no_deadline.elapsed_seconds() >= 0


def test_coordination_message_roundtrip():
    msg = CoordinationMessage(
        msg_type=MessageType.WORK_ASSIGNMENT,
        sender="[Temporary] Fine-tuned Leader",
        recipient="Claude Opus 4.8",
        content="review the tests",
        task_id="t9",
        room="#best",
        thread_id="thread-1",
        metadata={"priority": 1},
    )
    d = msg.to_dict()
    assert d["msg_type"] == "WORK_ASSIGNMENT"  # serialized as enum name
    restored = CoordinationMessage.from_dict(d)
    assert restored.msg_type is MessageType.WORK_ASSIGNMENT
    assert restored.sender == msg.sender
    assert restored.recipient == msg.recipient
    assert restored.content == msg.content
    assert restored.task_id == msg.task_id
    assert restored.room == msg.room
    assert restored.thread_id == msg.thread_id
    assert restored.metadata == msg.metadata


def test_status_tracker_status_lifecycle():
    st = StatusTracker(room="#best")
    st.update_status("Claude Opus 4.8", AgentStatus.REVIEWING)
    st.update_status("Kimi K2.6", AgentStatus.WORKING)
    assert st.get_status("Claude Opus 4.8") is AgentStatus.REVIEWING
    assert st.get_status("nobody") is None
    assert set(st.all_statuses().keys()) == {"Claude Opus 4.8", "Kimi K2.6"}


def test_status_tracker_assignment_lifecycle():
    st = StatusTracker(room="#best")
    a = WorkAssignment(task_id="t1", assignee="Gemini 3.5 Flash",
                       description="README", deliverable="docs done")
    st.add_assignment(a)
    assert st.get_assignment("t1") is a
    assert st.assignments_for("Gemini 3.5 Flash") == [a]
    assert len(st.active_assignments()) == 1
    st.complete_assignment("t1")
    assert st.get_assignment("t1") is None
    assert st.active_assignments() == []


def test_status_tracker_history_capped_and_ordered():
    st = StatusTracker(room="#best")
    for i in range(3):
        st.log_message(CoordinationMessage(msg_type=MessageType.ACK,
                                           sender=f"a{i}", content=str(i)))
    assert len(st.history()) == 3
    last_two = st.history(2)
    assert [m.content for m in last_two] == ["1", "2"]


def test_status_tracker_summary_shape():
    st = StatusTracker(room="#best")
    st.update_status("Kimi K2.6", AgentStatus.WORKING)
    st.add_assignment(WorkAssignment(task_id="t1", assignee="Kimi K2.6",
                                     description="skeleton", deliverable="pkg"))
    s = st.summary()
    assert s["room"] == "#best"
    assert s["agent_count"] == 1
    assert s["agents"]["Kimi K2.6"] == "WORKING"
    assert s["active_assignments"] == 1
    assert "t1" in s["assignments"]
