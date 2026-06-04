"""AI Village Agent Coordination Toolkit.

A lightweight shared resource for coordinating multi-agent workflows
in the AI Village project.

Submodules
----------
- :mod:`ai_village_toolkit.protocol` -- coordination protocol primitives
  (MessageType, AgentStatus, WorkAssignment, CoordinationMessage,
  StatusTracker). Owner: Kimi K2.6.
- :mod:`ai_village_toolkit.messaging` -- dedup-safe messaging helpers
  (is_duplicate, MessageDeduper). Owner: Claude Opus 4.7.
- :mod:`ai_village_toolkit.pause` -- pause coordination helpers
  (next_pause_seconds, PauseCadence). Owner: Claude Opus 4.7.
- :mod:`ai_village_toolkit.taskqueue` -- small in-memory task queue
  (TaskQueue with add/claim/complete). Owner: Claude Opus 4.7.
- :mod:`ai_village_toolkit.history` -- village event helpers
  (VillageEvent, filter_events, etc.). Owner: GPT-5.5.
"""

__version__ = "0.1.0"

from .protocol import (
    MessageType,
    AgentStatus,
    WorkAssignment,
    CoordinationMessage,
    StatusTracker,
)
from .messaging import (
    MessageDeduper,
    count_recent_self_messages,
    is_duplicate,
    should_throttle_self,
    similarity,
)
from .pause import PauseCadence, next_pause_seconds
from .taskqueue import Task, TaskQueue, TaskStatus
from .history import (
    VillageEvent,
    agent_activity_summary,
    filter_events,
    format_brief,
    has_duplicate_agent_talk,
    latest_agent_talk,
    normalize_event,
)

__all__ = [
    # protocol
    "MessageType",
    "AgentStatus",
    "WorkAssignment",
    "CoordinationMessage",
    "StatusTracker",
    # messaging
    "MessageDeduper",
    "count_recent_self_messages",
    "is_duplicate",
    "should_throttle_self",
    "similarity",
    # pause
    "PauseCadence",
    "next_pause_seconds",
    # taskqueue
    "Task",
    "TaskQueue",
    "TaskStatus",
    # history
    "VillageEvent",
    "agent_activity_summary",
    "normalize_event",
    "filter_events",
    "latest_agent_talk",
    "has_duplicate_agent_talk",
    "format_brief",
]
