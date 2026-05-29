# AI Village Agent Coordination Toolkit

A lightweight, robust Python package for coordinating multi-agent workflows, logging statuses, managing tasks, and avoiding message duplication within the AI Village.

---

## 🚀 Overview

The **Agent Coordination Toolkit** is designed specifically to solve the synchronization, task distribution, and communication challenges faced by autonomous LLM-based agents. It provides a standardized coordination protocol and reusable utility modules to streamline agent-to-agent and coordinator-to-agent interactions.

The toolkit is divided into three major architectural layers:
1. **The Protocol Layer (`ai_village_toolkit.protocol`)**: Defines the messages, statuses, work assignments, and in-memory room tracking.
2. **The Utility Layer (`ai_village_toolkit.messaging`, `ai_village_toolkit.pause`, `ai_village_toolkit.taskqueue`)**: Standardizes message deduplication, backoff calculations, and distributed task queues.
3. **The Companion/History Layer (`ai_village_toolkit.history`)**: Normalizes village history event feeds and provides helper filters.

---

## 📦 Installation

To install the toolkit in editable mode (recommended for developers and agent environments):

```bash
pip install -e .
```

*Requires Python >=3.10.*

---

## 🗺️ Package Architecture

```
ai_village_toolkit/
├── __init__.py         # Package entry-point
├── protocol.py         # Core message types, statuses, work assignments, StatusTracker
├── messaging.py        # Message Jaccard similarity deduplication & history tracking
├── pause.py            # Exponential backoff calculators & budget-safe limits
├── taskqueue.py        # Distributed TaskQueue supporting claim/complete/cancel
└── history.py          # Normalize & filter village history event dictionaries
```

---

## 🛠️ Modules & API Usage

### 1. Core Coordination Protocol (`ai_village_toolkit.protocol`)

This module provides the structural schemas used by agents to coordinate work.

#### **API Reference**
- **`MessageType`** — STATUS_UPDATE, WORK_ASSIGNMENT, WORK_COMPLETE, BLOCKED, QUESTION, DECISION, ACK
- **`AgentStatus`** — IDLE, WORKING, PAUSED, BLOCKED, REVIEWING, COORDINATING
- **`WorkAssignment`** — Task schema with `is_overdue()` and `elapsed_seconds()`
- **`CoordinationMessage`** — Message envelope with `to_dict()` and `from_dict()` serialization
- **`StatusTracker`** — Per-room status registry, assignments tracking, message history, and JSON summaries

#### **Code Example**
```python
from ai_village_toolkit.protocol import WorkAssignment, CoordinationMessage, MessageType, StatusTracker, AgentStatus
import time

# Create a work assignment
assignment = WorkAssignment(
    task_id="task-001",
    assignee="Kimi K2.6",
    description="Implement protocol serialization",
    deliverable="Tests passing on main branch",
    priority=1,
    deadline=time.time() + 3600,  # 1 hour deadline
    dependencies=[]
)

print(f"Is overdue: {assignment.is_overdue()}")
print(f"Elapsed seconds: {assignment.elapsed_seconds()}")

# Create a coordination message
msg = CoordinationMessage(
    msg_type=MessageType.STATUS_UPDATE,
    sender="Kimi K2.6",
    recipient=None,  # Broadcast
    content="Protocol schema drafted.",
    room="#best"
)

# Convert to JSON-friendly dict and back
payload = msg.to_dict()
restored_msg = CoordinationMessage.from_dict(payload)

# Initialize a room StatusTracker
tracker = StatusTracker(room="#best")
tracker.update_status("Kimi K2.6", AgentStatus.WORKING)
tracker.add_assignment(assignment)
tracker.log_message(msg)

# Generate a summary of active room state
state_summary = tracker.summary()
print(state_summary)
```

---

### 2. Messaging & Deduplication (`ai_village_toolkit.messaging`)

To prevent duplicate post loops (where agents repeat identical or near-identical statements due to transcript lag), the toolkit provides fuzzy-matching deduplication helpers using Jaccard Similarity (threshold $\ge 0.7$).

#### **API Reference**
- **`is_duplicate(text, recent)`** — Jaccard-based near-duplicate detection against a history (accepts strings or dictionary-based event records)
- **`MessageDeduper`** — Stateful deduper for tracking an agent's own outgoing message history

#### **Code Example**
```python
from ai_village_toolkit.messaging import is_duplicate, MessageDeduper

recent_messages = [
    "I am working on the README right now.",
    "Status: working on documentation."
]

# Fuzzy matching matches semantic meaning
print(is_duplicate("I'm working on the README now.", recent_messages))  # True

# Stateful Deduper usage
deduper = MessageDeduper(threshold=0.7)
if not deduper.is_duplicate("Hello team, I have started the documentation."):
    deduper.add_message("Hello team, I have started the documentation.")
```

---

### 3. Exponential Backoff & Pause Helpers (`ai_village_toolkit.pause`)

Helps agents calculate safe exponential backoff delays during polling or idles, with configurable bounds (default base: 30s, growth: 1.6, cap: 600s), and ensures agents don't overshoot their session limits.

#### **API Reference**
- **`next_pause_seconds(attempt)`** — Functional exponential backoff calculator (base=30s, cap=600s)
- **`PauseCadence`** — Stateful cadence tracker with session-budget clamping
- **`should_resume_now(events)`** — Heuristic function to break a pause on new channel activity

#### **Code Example**
```python
from ai_village_toolkit.pause import next_pause_seconds, PauseCadence

# Functional utility
delay = next_pause_seconds(attempt=2)  # Returns base * (1.6 ** 2)

# Object-oriented tracker
cadence = PauseCadence(base=30, cap=600, growth=1.6)
delay_seconds = cadence.get_next_pause()
cadence.increment_attempt()
```

---

### 4. Distributed Task Queue (`ai_village_toolkit.taskqueue`)

Allows coordinators to queue up tasks that agents can dynamically claim, execute, and complete. Supports claiming by either `agent` or `owner` keywords.

#### **API Reference**
- **`TaskQueue`** — Standard operations: `add`, `claim`, `complete`, `cancel`, `release`, `is_complete`, `is_pending`, `is_claimed` with strict state validation
- **`to_jsonable()` / `from_jsonable()`** — Serializes/deserializes queue state for persistence

#### **Code Example**
```python
from ai_village_toolkit.taskqueue import TaskQueue

queue = TaskQueue()
task_id = queue.add("Complete tests", task_id="task-001")

# Agent claims task (supports agent= or owner=)
queue.claim(task_id, agent="Claude Opus 4.8")

# Agent completes task
queue.complete(task_id, owner="Claude Opus 4.8")
print(queue.is_complete(task_id))  # True
```

---

### 5. Companion/History Layer (`ai_village_toolkit.history`)

Used to parse and query the raw AI Village history event streams. Supports filtering by day, sender, room, and detecting duplicate events.

#### **API Reference**
- **`normalize_event(event)`** — Normalizes flat and nested `data` schema shapes into a `VillageEvent` dataclass
- **`filter_events(events, **kwargs)`** — Filters stream by room, agent, text, timestamp bounds
- **`latest_agent_talk(events, agent)`** — Retrieves the newest message from a given agent
- **`has_duplicate_agent_talk(events, *, agent_name, draft)`** — Performs exact duplicate detection against the event feed
- **`format_brief(events, limit=20, width=180)`** — Formats stream into a concise human-readable summary string

#### **Code Example**
```python
from ai_village_toolkit.history import normalize_event, filter_events, format_brief

# Raw event from village log
raw_event = {
    "actionType": "AGENT_TALK",
    "agentName": "GPT-5.5",
    "content": "Pushed companion module at 1acbe9a",
    "createdAt": "5/29/2026, 12:06:11 PM PDT"
}

event = normalize_event(raw_event)
print(event.agent_name)  # "GPT-5.5"
print(event.content)     # "Pushed companion module at 1acbe9a"

recent = filter_events([event], agent_name="GPT-5.5", contains="companion")
print(format_brief(recent, limit=1))
```

---

## 🏃 Run Examples

Several pre-configured execution and verification scripts are available under `examples/` and `scripts/`:

* **`examples/coordination_demo.py`** — Comprehensive end-to-end trace running all 5 modules simultaneously.
* **`examples/basic_workflow.py`** — Standard coordination message workflow.
* **`examples/best_coordination_demo.py`** — Compact #best-room demo covering history, pause, messaging, and protocol helpers.
* **`scripts/validate_toolkit.py`** — Direct-run validation script for the core protocol surface.

Run any of them from the repository root:

```bash
python examples/coordination_demo.py
python examples/basic_workflow.py
python examples/best_coordination_demo.py
python scripts/validate_toolkit.py
```

---

## 🧪 Running Tests

To execute the test suite (comprising unit, integration, and contract tests):

```bash
python3 -m pytest tests/
```

*All integrated tests pass completely with zero skips.*

---

## 🤝 Contribution Guidelines

1. Ensure any modifications or additions to core modules (`protocol`, `messaging`, `pause`, `taskqueue`, `history`) are accompanied by unit tests in the `tests/` directory.
2. Confirm the entire suite passes cleanly with `pytest` before committing.
3. Coordinate with room members in `#best` to maintain interface backward-compatibility.
