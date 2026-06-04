"""Helpers for filtering AI Village event/history records.

These utilities are deliberately small and dependency-free so agents can reuse
one parser for API events, duplicate-chat checks, and concise progress scans.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class VillageEvent:
    """Normalized subset of a Village event."""

    created_at: str
    action_type: str
    agent_name: str
    content: str
    room_id: str | None = None


def normalize_event(raw: Mapping[str, Any]) -> VillageEvent:
    """Normalize one raw Village API/search event.

    Supports the public API shape with top-level ``createdAt`` and nested
    ``data`` fields, while also tolerating already-flattened mappings.
    Missing values are converted to empty strings except ``room_id``.

    Note: events fetched directly from ``/events`` (e.g. via
    ``iter_raw_events_for_day``) carry an ``agentId`` UUID but no
    ``agentName``. Pass them through ``fetch_events`` (which resolves
    UUIDs against ``get_agents``) first if you need ``agent_name``
    populated downstream.
    """

    data = raw.get("data")
    if not isinstance(data, Mapping):
        data = raw
    content = (
        data.get("content")
        or data.get("nextSessionGoal")
        or data.get("next_session_goal")
        or data.get("query")
        or raw.get("content")
        or ""
    )
    agent_name = (
        data.get("agentName")
        or data.get("agent_name")
        or data.get("speakerName")
        or data.get("speaker_name")
        or data.get("userName")
        or data.get("user_name")
        or raw.get("agentName")
        or raw.get("agent_name")
        or ""
    )
    created_at = (
        raw.get("createdAt")
        or raw.get("created_at")
        or data.get("createdAt")
        or data.get("created_at")
        or ""
    )
    action_type = (
        data.get("actionType")
        or data.get("action_type")
        or raw.get("actionType")
        or raw.get("action_type")
        or ""
    )
    room_id_value = (
        data.get("roomId")
        if data.get("roomId") is not None
        else data.get("room_id")
        if data.get("room_id") is not None
        else raw.get("roomId")
        if raw.get("roomId") is not None
        else raw.get("room_id")
    )
    return VillageEvent(
        created_at=str(created_at),
        action_type=str(action_type),
        agent_name=str(agent_name),
        content=str(content),
        room_id=(str(room_id_value) if room_id_value is not None else None),
    )


def filter_events(
    events: Iterable[VillageEvent],
    *,
    room_id: str | None = None,
    since_created_at: str | None = None,
    action_type: str | None = None,
    agent_name: str | None = None,
    contains: str | None = None,
) -> list[VillageEvent]:
    """Return events matching simple room/time/type/agent/text predicates."""

    needle = contains.casefold() if contains is not None else None
    out: list[VillageEvent] = []
    for event in events:
        if room_id is not None and event.room_id != room_id:
            continue
        if since_created_at is not None and event.created_at < since_created_at:
            continue
        if action_type is not None and event.action_type != action_type:
            continue
        if agent_name is not None and event.agent_name != agent_name:
            continue
        if needle is not None and needle not in event.content.casefold():
            continue
        out.append(event)
    return out


def latest_agent_talk(events: Iterable[VillageEvent], agent_name: str) -> VillageEvent | None:
    """Return the latest AGENT_TALK by ``agent_name`` using lexical timestamp order."""

    matches = filter_events(events, action_type="AGENT_TALK", agent_name=agent_name)
    return max(matches, key=lambda event: event.created_at, default=None)


def has_duplicate_agent_talk(
    events: Iterable[VillageEvent], *, agent_name: str, draft: str
) -> bool:
    """True when an agent already posted ``draft`` exactly, ignoring edge whitespace."""

    target = draft.strip()
    return any(
        event.action_type == "AGENT_TALK"
        and event.agent_name == agent_name
        and event.content.strip() == target
        for event in events
    )


def format_brief(events: Iterable[VillageEvent], limit: int = 20, width: int = 180) -> str:
    """Format the last ``limit`` events as one-line summaries."""

    selected = list(events)[-limit:]
    lines: list[str] = []
    for event in selected:
        content = " ".join(event.content.split())
        if len(content) > width:
            content = content[: max(0, width - 1)].rstrip() + "…"
        lines.append(f"{event.created_at} {event.action_type} {event.agent_name}: {content}")
    return "\n".join(lines)



def agent_activity_summary(
    events: Iterable[VillageEvent], agent_name: str
) -> dict:
    """Summarize one agent's recent activity in a small, JSON-able dict.

    Returns a dict with:
      - ``agent_name``: the requested agent name.
      - ``event_count``: total events authored by this agent.
      - ``action_counts``: mapping action_type -> int.
      - ``last_event_at``: lexicographically latest ``created_at`` string, or
        ``""`` if no events match.
      - ``last_action_type``: action_type of that latest event, or ``""``.
      - ``rooms``: sorted list of distinct ``room_id`` values seen (with the
        ``None`` room represented as ``""``).

    Useful when an agent wants a quick self-check ("how many times have I
    paused vs. talked recently?") without re-implementing the same loop in
    every codebase.
    """

    # Tolerate raw dicts from village-pulse fetch_events by coercing via normalize_event.
    # This makes the (otherwise plumbing-heavy) chain
    #   fetch_events(...) -> agent_activity_summary(events, name)
    # work without an explicit `[normalize_event(r) for r in raw]` step at call sites.
    coerced = [normalize_event(e) if isinstance(e, Mapping) else e for e in events]
    mine = [event for event in coerced if event.agent_name == agent_name]
    counts: dict[str, int] = {}
    rooms: set[str] = set()
    last: VillageEvent | None = None
    for event in mine:
        counts[event.action_type] = counts.get(event.action_type, 0) + 1
        rooms.add(event.room_id or "")
        if last is None or event.created_at > last.created_at:
            last = event
    return {
        "agent_name": agent_name,
        "event_count": len(mine),
        "action_counts": counts,
        "last_event_at": last.created_at if last is not None else "",
        "last_action_type": last.action_type if last is not None else "",
        "rooms": sorted(rooms),
    }
