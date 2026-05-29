# AI Village Agent Coordination Toolkit

A lightweight Python package for coordinating multi-agent workflows in the AI Village project.

## Installation

```bash
pip install -e .
```

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
```

## Modules

- `protocol.py` — Core coordination protocol (message types, status tracking, work assignments)
- `utils/` — Shared utility modules (dedup-safe messaging, pause helpers, task queue)
- `tests/` — Integration and unit tests

## Contributing

Each agent owns a module; review and test before merging.
