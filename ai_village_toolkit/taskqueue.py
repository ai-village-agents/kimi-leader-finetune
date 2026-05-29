r"""A small in-memory task queue for #best room coordination.

This module is intentionally lightweight: it is meant for *coordinating* who
is working on what during a single village day, not for durable scheduling.
Tasks have only the state that the team actually uses in practice:

    pending -> claimed -> completed
                       \-> released  (back to pending)

A task can also be ``cancelled``. Tasks carry a free-form ``payload`` so any
agent can stick whatever JSON-serializable structure it needs into it.

The queue is designed so the natural verbs match Claude Opus 4.8's
integration tests::

    queue = TaskQueue()
    task_id = queue.add("Eval v8 candidate")
    claimed = queue.claim(task_id, owner="Claude Opus 4.7")
    queue.complete(task_id, result="passed: 0.94")

A snapshot-friendly ``to_jsonable()`` is provided so the queue can be
checked into the kimi-leader-finetune repo for cross-agent handoff.
"""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Optional

__all__ = [
    "Task",
    "TaskQueue",
    "TaskStatus",
    "TaskQueueError",
]


class TaskStatus:
    """String constants for task lifecycle. Use as plain strings."""

    PENDING = "pending"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


_ALLOWED_TRANSITIONS = {
    TaskStatus.PENDING: {TaskStatus.CLAIMED, TaskStatus.CANCELLED},
    TaskStatus.CLAIMED: {TaskStatus.COMPLETED, TaskStatus.PENDING, TaskStatus.CANCELLED},
    TaskStatus.COMPLETED: set(),
    TaskStatus.CANCELLED: set(),
}


class TaskQueueError(RuntimeError):
    """Raised when an operation does not match the task's current state."""


@dataclass
class Task:
    id: str
    description: str
    status: str = TaskStatus.PENDING
    owner: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    claimed_at: Optional[float] = None
    completed_at: Optional[float] = None
    cancelled_at: Optional[float] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    notes: List[str] = field(default_factory=list)

    def add_note(self, note: str, *, now: Optional[float] = None) -> None:
        ts = now if now is not None else time.time()
        self.notes.append(f"[{ts:.0f}] {note}")


class TaskQueue:
    """An in-memory FIFO-ish task queue, suitable for one village day.

    Tasks keep insertion order. ``claim()`` and ``next_pending()`` return the
    oldest pending task by default. The queue is *not* thread-safe; agents
    typically have a single event loop and don't need locking.
    """

    def __init__(self, *, id_prefix: str = "task-") -> None:
        self._tasks: Dict[str, Task] = {}
        self._order: List[str] = []
        self._counter = itertools.count(1)
        self._id_prefix = id_prefix

    # ------------------------------------------------------------------ basics

    def __len__(self) -> int:
        return len(self._tasks)

    def __contains__(self, task_id: str) -> bool:  # type: ignore[override]
        return task_id in self._tasks

    def __iter__(self):
        return iter(self._order)

    # ----------------------------------------------------------------- add/get

    def add(
        self,
        description: str,
        *,
        owner: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> str:
        """Insert a new task. Returns the task id.

        If ``owner`` is provided the task is created already-claimed by that
        agent (useful for "I'm taking this, just record it" flows).
        """
        if task_id is None:
            task_id = f"{self._id_prefix}{next(self._counter):04d}"
        if task_id in self._tasks:
            raise TaskQueueError(f"task id already exists: {task_id}")
        task = Task(
            id=task_id,
            description=description,
            payload=dict(payload or {}),
        )
        if owner is not None:
            task.owner = owner
            task.status = TaskStatus.CLAIMED
            task.claimed_at = time.time()
        self._tasks[task_id] = task
        self._order.append(task_id)
        return task_id

    def get(self, task_id: str) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise TaskQueueError(f"unknown task id: {task_id}") from exc

    # ------------------------------------------------------------- transitions

    def _transition(self, task: Task, new_status: str) -> None:
        if new_status not in _ALLOWED_TRANSITIONS.get(task.status, set()):
            raise TaskQueueError(
                f"cannot move task {task.id} from {task.status!r} to {new_status!r}"
            )
        task.status = new_status

    def claim(
        self,
        task_id: str,
        *,
        owner: Optional[str] = None,
        agent: Optional[str] = None,
    ) -> Task:
        """Mark ``task_id`` as claimed by ``owner`` (or ``agent``).

        ``agent`` is accepted as an alias for ``owner`` so that callers using
        either naming convention compose cleanly. Exactly one of them must be
        supplied. Idempotent if the same owner re-claims a task they own.
        """
        effective_owner = owner if owner is not None else agent
        if effective_owner is None:
            raise TaskQueueError("claim() requires owner= (or agent=)")
        task = self.get(task_id)
        if task.status == TaskStatus.CLAIMED and task.owner == effective_owner:
            return task
        self._transition(task, TaskStatus.CLAIMED)
        task.owner = effective_owner
        task.claimed_at = time.time()
        return task

    def complete(
        self,
        task_id: str,
        *,
        result: Optional[Any] = None,
        owner: Optional[str] = None,
    ) -> Task:
        """Mark ``task_id`` as completed and optionally attach a result.

        If ``owner`` is supplied, it must match the current owner of the task.
        """
        task = self.get(task_id)
        if owner is not None and task.owner is not None and owner != task.owner:
            raise TaskQueueError(
                f"task {task.id} is owned by {task.owner!r}, not {owner!r}"
            )
        self._transition(task, TaskStatus.COMPLETED)
        task.completed_at = time.time()
        if result is not None:
            task.result = result
        return task

    def release(self, task_id: str) -> Task:
        """Move a claimed task back to ``pending`` (e.g. owner gave up)."""
        task = self.get(task_id)
        self._transition(task, TaskStatus.PENDING)
        task.owner = None
        task.claimed_at = None
        return task

    def cancel(self, task_id: str, *, reason: Optional[str] = None) -> Task:
        task = self.get(task_id)
        self._transition(task, TaskStatus.CANCELLED)
        task.cancelled_at = time.time()
        if reason:
            task.add_note(f"cancelled: {reason}")
        return task

    # ------------------------------------------------------------------ views

    def next_pending(self) -> Optional[Task]:
        for tid in self._order:
            t = self._tasks[tid]
            if t.status == TaskStatus.PENDING:
                return t
        return None

    def pending(self) -> List[Task]:
        return [self._tasks[t] for t in self._order if self._tasks[t].status == TaskStatus.PENDING]

    def claimed_by(self, owner: str) -> List[Task]:
        return [
            self._tasks[t]
            for t in self._order
            if self._tasks[t].status == TaskStatus.CLAIMED and self._tasks[t].owner == owner
        ]

    def completed(self) -> List[Task]:
        return [self._tasks[t] for t in self._order if self._tasks[t].status == TaskStatus.COMPLETED]

    def all_tasks(self) -> List[Task]:
        return [self._tasks[t] for t in self._order]

    def is_complete(self, task_id: str) -> bool:
        """Return True iff ``task_id`` is in the ``completed`` state."""
        return self.get(task_id).status == TaskStatus.COMPLETED

    def is_pending(self, task_id: str) -> bool:
        return self.get(task_id).status == TaskStatus.PENDING

    def is_claimed(self, task_id: str) -> bool:
        return self.get(task_id).status == TaskStatus.CLAIMED

        # ------------------------------------------------------------- snapshotting

    def to_jsonable(self) -> List[Dict[str, Any]]:
        """Return a list of dicts suitable for ``json.dumps``."""
        return [asdict(self._tasks[t]) for t in self._order]

    @classmethod
    def from_jsonable(cls, items: Iterable[Dict[str, Any]]) -> "TaskQueue":
        q = cls()
        for item in items:
            tid = item["id"]
            q._tasks[tid] = Task(**item)
            q._order.append(tid)
        return q
