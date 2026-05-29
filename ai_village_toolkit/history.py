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
    """

    data = raw.get("data")
    if not isinstance(data, Mapping):
        data = raw
    content = (
        data.get("content")
        or data.get("nextSessionGoal")
        or data.get("query")
        or raw.get("content")
        or ""
    )
    agent_name = (
        data.get("agentName")
        or data.get("speakerName")
        or data.get("userName")
        or raw.get("agentName")
        or ""
    )
    return VillageEvent(
        created_at=str(raw.get("createdAt") or data.get("createdAt") or ""),
        action_type=str(data.get("actionType") or raw.get("actionType") or ""),
        agent_name=str(agent_name),
        content=str(content),
        room_id=(str(data.get("roomId")) if data.get("roomId") is not None else None),
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
