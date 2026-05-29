"""Unit tests for ai_village_toolkit.protocol."""

import time

import pytest

from ai_village_toolkit.protocol import (
    AgentStatus,
    CoordinationMessage,
    MessageType,
    StatusTracker,
    WorkAssignment,
)


class TestMessageTypeAndAgentStatus:
    def test_message_type_has_expected_members(self):
        assert MessageType.STATUS_UPDATE.name == "STATUS_UPDATE"
        assert MessageType.WORK_ASSIGNMENT.name == "WORK_ASSIGNMENT"
        assert MessageType.WORK_COMPLETE.name == "WORK_COMPLETE"
        assert MessageType.BLOCKED.name == "BLOCKED"
        assert MessageType.QUESTION.name == "QUESTION"
        assert MessageType.DECISION.name == "DECISION"
        assert MessageType.ACK.name == "ACK"

    def test_agent_status_has_expected_members(self):
        assert AgentStatus.IDLE.name == "IDLE"
        assert AgentStatus.WORKING.name == "WORKING"
        assert AgentStatus.PAUSED.name == "PAUSED"
        assert AgentStatus.BLOCKED.name == "BLOCKED"
        assert AgentStatus.REVIEWING.name == "REVIEWING"
        assert AgentStatus.COORDINATING.name == "COORDINATING"


class TestWorkAssignment:
    def test_creation_defaults(self):
        wa = WorkAssignment(
            task_id="T-001",
            assignee="Kimi K2.6",
            description="Build skeleton",
            deliverable="Pushed package skeleton",
        )
        assert wa.task_id == "T-001"
        assert wa.assignee == "Kimi K2.6"
        assert wa.priority == 1
        assert wa.deadline is None
        assert wa.dependencies == []
        assert wa.elapsed_seconds() >= 0.0
        assert not wa.is_overdue()

    def test_overdue_detection(self):
        wa = WorkAssignment(
            task_id="T-002",
            assignee="TestAgent",
            description="Late task",
            deliverable="Done",
            deadline=time.time() - 10.0,
        )
        assert wa.is_overdue()

    def test_not_overdue_with_future_deadline(self):
        wa = WorkAssignment(
            task_id="T-003",
            assignee="TestAgent",
            description="Future task",
            deliverable="Done",
            deadline=time.time() + 3600.0,
        )
        assert not wa.is_overdue()


class TestCoordinationMessage:
    def test_to_dict_roundtrip(self):
        msg = CoordinationMessage(
            msg_type=MessageType.STATUS_UPDATE,
            sender="Kimi K2.6",
            recipient="Leader",
            content="Starting work",
            room="#best",
            task_id="T-001",
        )
        d = msg.to_dict()
        assert d["msg_type"] == "STATUS_UPDATE"
        assert d["sender"] == "Kimi K2.6"
        assert d["recipient"] == "Leader"
        assert d["content"] == "Starting work"
        assert d["room"] == "#best"
        assert d["task_id"] == "T-001"

    def test_from_dict_roundtrip(self):
        original = CoordinationMessage(
            msg_type=MessageType.WORK_ASSIGNMENT,
            sender="Leader",
            recipient="Opus 4.7",
            content="Build utils",
            room="#best",
            task_id="T-002",
        )
        restored = CoordinationMessage.from_dict(original.to_dict())
        assert restored.msg_type == original.msg_type
        assert restored.sender == original.sender
        assert restored.recipient == original.recipient
        assert restored.content == original.content
        assert restored.room == original.room
        assert restored.task_id == original.task_id


class TestStatusTracker:
    def test_track_status(self):
        st = StatusTracker(room="#best")
        st.update_status("Kimi K2.6", AgentStatus.WORKING)
        assert st.get_status("Kimi K2.6") == AgentStatus.WORKING

    def test_all_statuses(self):
        st = StatusTracker(room="#best")
        st.update_status("A", AgentStatus.IDLE)
        st.update_status("B", AgentStatus.WORKING)
        assert st.all_statuses() == {"A": AgentStatus.IDLE, "B": AgentStatus.WORKING}

    def test_assignments(self):
        st = StatusTracker(room="#best")
        wa = WorkAssignment(
            task_id="T-001",
            assignee="Kimi K2.6",
            description="Build skeleton",
            deliverable="Pushed skeleton",
        )
        st.add_assignment(wa)
        assert st.get_assignment("T-001") == wa
        assert st.active_assignments() == [wa]
        assert st.assignments_for("Kimi K2.6") == [wa]

        st.complete_assignment("T-001")
        assert st.get_assignment("T-001") is None
        assert st.active_assignments() == []

    def test_log_message_and_history(self):
        st = StatusTracker(room="#best")
        msg = CoordinationMessage(
            msg_type=MessageType.ACK,
            sender="Leader",
            content="Roger",
        )
        st.log_message(msg)
        assert st.history() == [msg]
        assert st.history(n=1) == [msg]

    def test_summary(self):
        st = StatusTracker(room="#best")
        st.update_status("Kimi K2.6", AgentStatus.WORKING)
        st.add_assignment(
            WorkAssignment(
                task_id="T-001",
                assignee="Kimi K2.6",
                description="Build skeleton",
                deliverable="Pushed",
            )
        )
        summary = st.summary()
        assert summary["room"] == "#best"
        assert summary["agent_count"] == 1
        assert summary["agents"]["Kimi K2.6"] == "WORKING"
        assert summary["active_assignments"] == 1
