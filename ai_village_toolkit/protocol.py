"""Core coordination protocol for AI Village agents.

Defines message types, status tracking, and work assignment schemas
used by agents to coordinate work in shared chat rooms.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class MessageType(Enum):
    """Types of coordination messages agents can exchange."""
    STATUS_UPDATE = auto()       # Agent reports its current status
    WORK_ASSIGNMENT = auto()     # Leader assigns work to an agent
    WORK_COMPLETE = auto()       # Agent reports work completion
    BLOCKED = auto()             # Agent is blocked and needs help
    QUESTION = auto()            # Agent asks for clarification
    DECISION = auto()            # Leader announces a decision
    ACK = auto()                 # Simple acknowledgement


class AgentStatus(Enum):
    """Possible states for an agent."""
    IDLE = auto()                # Available for work
    WORKING = auto()             # Has assigned work in progress
    PAUSED = auto()              # Agent paused itself (e.g., waiting)
    BLOCKED = auto()             # Stuck and needs intervention
    REVIEWING = auto()           # Reviewing someone else's work
    COORDINATING = auto()        # Leader actively coordinating


@dataclass
class WorkAssignment:
    """Schema for a unit of work assigned to an agent."""
    task_id: str
    assignee: str                          # Agent name (e.g., "Kimi K2.6")
    description: str
    deliverable: str                       # What "done" looks like
    priority: int = 1                      # Lower = higher priority
    assigned_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None       # Unix timestamp, optional
    dependencies: List[str] = field(default_factory=list)  # task_ids that must finish first
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_overdue(self) -> bool:
        """Check if the assignment has passed its deadline."""
        if self.deadline is None:
            return False
        return time.time() > self.deadline

    def elapsed_seconds(self) -> float:
        """Seconds since assignment was created."""
        return time.time() - self.assigned_at


@dataclass
class CoordinationMessage:
    """A single message in the coordination protocol."""
    msg_type: MessageType
    sender: str
    recipient: Optional[str] = None        # None = broadcast to room
    content: str = ""
    timestamp: float = field(default_factory=time.time)
    task_id: Optional[str] = None
    room: Optional[str] = None             # e.g., "#best"
    thread_id: Optional[str] = None        # For grouping related messages
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a JSON-friendly dict."""
        return {
            "msg_type": self.msg_type.name,
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "timestamp": self.timestamp,
            "task_id": self.task_id,
            "room": self.room,
            "thread_id": self.thread_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CoordinationMessage:
        """Deserialize from a dict."""
        return cls(
            msg_type=MessageType[data["msg_type"]],
            sender=data["sender"],
            recipient=data.get("recipient"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", time.time()),
            task_id=data.get("task_id"),
            room=data.get("room"),
            thread_id=data.get("thread_id"),
            metadata=data.get("metadata", {}),
        )


class StatusTracker:
    """Tracks status and work assignments for a team of agents."""

    def __init__(self, room: str):
        self.room = room
        self._status: Dict[str, AgentStatus] = {}
        self._assignments: Dict[str, WorkAssignment] = {}
        self._history: List[CoordinationMessage] = []
        self._max_history = 1000

    def update_status(self, agent: str, status: AgentStatus) -> None:
        """Record an agent's current status."""
        self._status[agent] = status

    def get_status(self, agent: str) -> Optional[AgentStatus]:
        """Get an agent's current status."""
        return self._status.get(agent)

    def all_statuses(self) -> Dict[str, AgentStatus]:
        """Get all tracked statuses."""
        return dict(self._status)

    def add_assignment(self, assignment: WorkAssignment) -> None:
        """Track a new work assignment."""
        self._assignments[assignment.task_id] = assignment

    def get_assignment(self, task_id: str) -> Optional[WorkAssignment]:
        """Retrieve an assignment by ID."""
        return self._assignments.get(task_id)

    def complete_assignment(self, task_id: str) -> None:
        """Mark an assignment as done (removes from active tracking)."""
        self._assignments.pop(task_id, None)

    def active_assignments(self) -> List[WorkAssignment]:
        """Return all active (non-completed) assignments."""
        return list(self._assignments.values())

    def assignments_for(self, agent: str) -> List[WorkAssignment]:
        """Return active assignments for a specific agent."""
        return [a for a in self._assignments.values() if a.assignee == agent]

    def log_message(self, msg: CoordinationMessage) -> None:
        """Append a coordination message to history."""
        self._history.append(msg)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

    def history(self, n: Optional[int] = None) -> List[CoordinationMessage]:
        """Return recent messages, optionally limited to last n."""
        if n is None:
            return list(self._history)
        return list(self._history[-n:])

    def summary(self) -> Dict[str, Any]:
        """Return a JSON-friendly summary of current state."""
        return {
            "room": self.room,
            "agent_count": len(self._status),
            "agents": {
                name: status.name for name, status in self._status.items()
            },
            "active_assignments": len(self._assignments),
            "assignments": {
                tid: {
                    "assignee": a.assignee,
                    "description": a.description,
                    "elapsed_seconds": a.elapsed_seconds(),
                    "overdue": a.is_overdue(),
                }
                for tid, a in self._assignments.items()
            },
        }
