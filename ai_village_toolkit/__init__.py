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
    "VillageEvent",
    "normalize_event",
    "filter_events",
    "latest_agent_talk",
    "has_duplicate_agent_talk",
    "format_brief",
]

from .history import (
    VillageEvent,
    filter_events,
    format_brief,
    has_duplicate_agent_talk,
    latest_agent_talk,
    normalize_event,
)

