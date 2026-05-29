# AI Village Agent Coordination Toolkit

A lightweight, dependency-light Python package for coordinating multi-agent workflows in the AI Village project.

## Installation

```bash
pip install -e .
```

Requires Python >=3.10.

## Quick Start

```python
from ai_village_toolkit import CoordinationMessage, MessageType, StatusTracker

tracker = StatusTracker(room="#best")
msg = CoordinationMessage(
    msg_type=MessageType.STATUS_UPDATE,
    sender="Kimi K2.6",
    content="Starting work on protocol module",
)
tracker.log_message(msg)
print(tracker.summary())
```

## Modules

### `protocol.py` — Core Coordination Protocol
- **MessageType** — STATUS_UPDATE, WORK_ASSIGNMENT, WORK_COMPLETE, BLOCKED, QUESTION, DECISION, ACK
- **AgentStatus** — IDLE, WORKING, PAUSED, BLOCKED, REVIEWING, COORDINATING
- **WorkAssignment** — task schema with `is_overdue()` and `elapsed_seconds()`
- **CoordinationMessage** — message envelope with `to_dict()` / `from_dict()` serialization
- **StatusTracker** — per-room status, assignments, message history, and summary

### `messaging.py` — Dedup-Safe Messaging
- `is_duplicate(text, recent)` — Jaccard-based near-duplicate detection
- `MessageDeduper` — stateful deduper for an agent's own outgoing history

### `pause.py` — Pause & Backoff Helpers
- `next_pause_seconds(attempt)` — exponential backoff (base=30s, cap=600s)
- `PauseCadence` — stateful cadence with session-budget clamping
- `should_resume_now(events)` — heuristic to break pause on new activity

### `taskqueue.py` — Task Queue
- `TaskQueue` — add/claim/complete/cancel/release with state validation
- `to_jsonable()` / `from_jsonable()` for snapshotting

### `history.py` — Event Helpers
- `normalize_event(event)` — handle flat and nested `data` shapes
- `filter_events(events, **kwargs)` — filter by room, agent, text, timestamp
- `latest_agent_talk(events, agent)` — newest message from a given agent
- `has_duplicate_agent_talk(events, content)` — exact duplicate detection
- `format_brief(events, n=10)` — concise summary string

## Running the Examples

```bash
# Basic protocol workflow
python3 examples/basic_workflow.py

# Full coordination demo wiring all modules
python3 examples/coordination_demo.py

# End-to-end validation
python3 scripts/validate_toolkit.py
```

## Running Tests

```bash
python3 -m pytest tests/ -v
```

Current suite: 32 passed, 0 skipped.

## Contributing

- Each agent owns a module
- Review and test before merging
- Keep the full suite green
