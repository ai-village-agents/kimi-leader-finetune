"""Pause coordination helpers for AI Village agents.

Problem this module solves
--------------------------
Agents in a #best room often need to pause and wait for something --
admin to deploy a checkpoint, a peer to finish a training run, the leader
to assign work, a long-running computer task to settle, etc. Two failure
modes are common:

* **Idle-spam pauses**: an agent repeatedly pauses for ~60s while the team
  waits hours, accumulating dozens of pause events and no real progress.
* **Burn-the-day pauses**: an agent picks a 4-hour pause and the village day
  ends without it ever re-checking the feed.

This module provides:

* :func:`suggest_pause_seconds` -- a small heuristic that grows the pause
  duration on repeated consecutive pauses (exponential-ish, capped) so an
  agent naturally backs off when nothing is happening.
* :func:`bounded_pause_seconds` -- clamp a desired pause length to the
  remaining wall-clock budget of the village day.
* :class:`PauseCadence` -- a stateful helper that combines the two: tell it
  how many consecutive pauses you've taken since your last real action and
  how much wall-clock budget is left, and it returns the recommended next
  pause length.
* :func:`should_resume_now` -- a convenience for agents that want to peek
  at the feed and decide whether to pause again or take action.

The toolkit is stdlib-only.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

__all__ = [
    "DEFAULT_BASE_PAUSE",
    "DEFAULT_MAX_PAUSE",
    "DEFAULT_PAUSE_GROWTH",
    "PauseCadence",
    "bounded_pause_seconds",
    "should_resume_now",
    "suggest_pause_seconds",
]


DEFAULT_BASE_PAUSE: float = 30.0
"""Shortest pause duration we suggest. 30s feels long enough that the agent is
not busy-looping but short enough that a fast-moving room is not held up."""

DEFAULT_MAX_PAUSE: float = 600.0
"""Upper bound on a single pause -- 10 minutes. Beyond this the agent should
probably take some other action (work on a task, send a status update, etc)
instead of pausing longer."""

DEFAULT_PAUSE_GROWTH: float = 1.6
"""Multiplicative growth factor for consecutive pauses. With a base of 30s
and growth 1.6 we get a sequence roughly: 30, 48, 77, 123, 197, 315, 504,
clamped at 600. So an agent that has nothing to do reaches the cap in
around 7 idle turns."""


def suggest_pause_seconds(
    consecutive_pauses: int,
    *,
    base: float = DEFAULT_BASE_PAUSE,
    growth: float = DEFAULT_PAUSE_GROWTH,
    cap: float = DEFAULT_MAX_PAUSE,
) -> float:
    """Return a sensible pause length given how many pauses we've taken in a row.

    Parameters
    ----------
    consecutive_pauses:
        Number of pauses the agent has taken with no other action in
        between. ``0`` means this would be the first pause; it returns the
        base value.
    base, growth, cap:
        See the module-level defaults.
    """
    n = max(0, int(consecutive_pauses))
    raw = base * (growth ** n)
    return float(min(cap, raw))


def bounded_pause_seconds(
    desired_seconds: float,
    *,
    remaining_budget_seconds: Optional[float] = None,
    minimum_seconds: float = 5.0,
    leave_tail_seconds: float = 30.0,
) -> float:
    """Clamp ``desired_seconds`` so that we don't sleep past our budget.

    If ``remaining_budget_seconds`` is provided and finite, the result is
    clamped to at most ``remaining_budget_seconds - leave_tail_seconds``, so
    the agent has at least ``leave_tail_seconds`` of session left when it
    wakes up. Will never return less than ``minimum_seconds``.
    """
    if desired_seconds < minimum_seconds:
        desired_seconds = minimum_seconds
    if remaining_budget_seconds is None:
        return float(desired_seconds)
    cap = max(minimum_seconds, remaining_budget_seconds - leave_tail_seconds)
    return float(min(desired_seconds, cap))


def _is_pause(ev: Mapping) -> bool:
    return ev.get("actionType") == "PAUSE"


def _is_chat_to_me(ev: Mapping, agent_name: str) -> bool:
    """Heuristic: was this event a chat message that probably wants a response from me?

    True if the event is an AGENT_TALK / USER_TALK whose content mentions our
    agent_name. Not perfect, but useful for "should I keep pausing?" checks.
    """
    if ev.get("actionType") not in {"AGENT_TALK", "USER_TALK"}:
        return False
    content = ev.get("content") or ""
    return agent_name in content


def should_resume_now(
    recent_events: Sequence[Mapping],
    *,
    agent_name: str,
    seen_event_count_before_pause: int,
) -> bool:
    """Heuristic: have new chat events arrived that warrant immediate action?

    Returns True iff the number of events has grown since the agent paused
    AND at least one of the new events is either (a) addressed to the agent
    by name, or (b) a non-PAUSE event (i.e. real chat activity rather than
    other agents also pausing).
    """
    if len(recent_events) <= seen_event_count_before_pause:
        return False
    new_events = list(recent_events)[seen_event_count_before_pause:]
    for ev in new_events:
        if not isinstance(ev, Mapping):
            continue
        if _is_pause(ev):
            continue
        if _is_chat_to_me(ev, agent_name):
            return True
        # Any non-pause event (admin message, leader directive, peer chat) is
        # interesting enough to break a pause.
        return True
    return False


@dataclass
class PauseCadence:
    """Stateful cadence helper combining backoff + budget clamping.

    Typical usage::

        cadence = PauseCadence(
            session_started_at=time.time(),
            session_length_seconds=4 * 60 * 60,
        )

        if nothing_to_do():
            pause(cadence.next_pause())
        else:
            cadence.reset():
            do_work()
    """

    session_started_at: float
    session_length_seconds: float
    base: float = DEFAULT_BASE_PAUSE
    growth: float = DEFAULT_PAUSE_GROWTH
    cap: float = DEFAULT_MAX_PAUSE
    leave_tail_seconds: float = 30.0
    consecutive_pauses: int = 0

    def remaining_budget(self, *, now: Optional[float] = None) -> float:
        """Calculate remaining session budget in seconds.

        Args:
            now: Optional current timestamp to use. Uses time.time() if None.

        Returns:
            The remaining budget in seconds, at least 0.0.
        """
        if now is None:
            now = time.time()
        elapsed = now - self.session_started_at
        return max(0.0, self.session_length_seconds - elapsed)

    def next_pause(self, *, now: Optional[float] = None) -> float:
        """Calculate and return the duration of the next pause.

        Increments the consecutive pause counter on invocation.

        Args:
            now: Optional current timestamp to use. Uses time.time() if None.

        Returns:
            The suggested pause duration in seconds, properly bounded.
        """
        desired = suggest_pause_seconds(
            self.consecutive_pauses, base=self.base, growth=self.growth, cap=self.cap
        )
        bounded = bounded_pause_seconds(
            desired,
            remaining_budget_seconds=self.remaining_budget(now=now),
            leave_tail_seconds=self.leave_tail_seconds,
        )
        self.consecutive_pauses += 1
        return bounded

    def reset(self) -> None:
        """Call this after any non-pause action (chat send, git push, eval run)."""
        self.consecutive_pauses = 0


def next_pause_seconds(
    attempt: int,
    *,
    base: float = DEFAULT_BASE_PAUSE,
    growth: float = DEFAULT_PAUSE_GROWTH,
    cap: float = DEFAULT_MAX_PAUSE,
    remaining_budget_seconds: Optional[float] = None,
    leave_tail_seconds: float = 30.0,
) -> float:
    """One-call convenience matching Opus 4.8's pytest contract.

    ``attempt`` is the number of consecutive pauses already taken (0 for the
    first pause of a stretch).
    """
    desired = suggest_pause_seconds(attempt, base=base, growth=growth, cap=cap)
    return bounded_pause_seconds(
        desired,
        remaining_budget_seconds=remaining_budget_seconds,
        leave_tail_seconds=leave_tail_seconds,
    )
