"""AI Village Agent Coordination Toolkit.

A lightweight shared resource for coordinating multi-agent workflows
in the AI Village project.
"""

__version__ = "0.1.0"

from .protocol import (
    MessageType,
    AgentStatus,
    WorkAssignment,
    CoordinationMessage,
    StatusTracker,
)

__all__ = [
    "MessageType",
    "AgentStatus",
    "WorkAssignment",
    "CoordinationMessage",
    "StatusTracker",
]
