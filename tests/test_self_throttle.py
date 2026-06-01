"""Tests for the self-rate-limit helpers in ai_village_toolkit.messaging.

Covers ``count_recent_self_messages``, ``should_throttle_self``, and the
private ``_parse_event_timestamp`` parser. These helpers let an agent decide
whether it has already sent too many messages in a window and should stay
quiet, independent of the dedup helpers in the same module.
"""

from __future__ import annotations

import pytest

from ai_village_toolkit.messaging import (
    DEFAULT_WINDOW_SECONDS,
    _parse_event_timestamp,
    count_recent_self_messages,
    should_throttle_self,
)


# ------------------------------------------------------------ timestamp parse

def test_parse_event_timestamp_iso_with_z():
    ts = _parse_event_timestamp({"createdAt": "2026-06-01T18:00:00Z"})
    assert ts is not None and 1.7e9 < ts < 1.8e9


def test_parse_event_timestamp_iso_with_offset():
    ts = _parse_event_timestamp({"createdAt": "2026-06-01T18:00:00+00:00"})
    assert ts is not None


def test_parse_event_timestamp_seconds_int():
    ts = _parse_event_timestamp({"createdAt": 1_748_800_800})
    assert ts == 1_748_800_800.0


def test_parse_event_timestamp_millis_int():
    # Heuristic: > 1e12 is treated as milliseconds.
    ts = _parse_event_timestamp({"createdAt": 1_748_800_800_000})
    assert ts == 1_748_800_800.0


def test_parse_event_timestamp_snake_case_fallback():
    ts = _parse_event_timestamp({"created_at": "2026-06-01T18:00:00Z"})
    assert ts is not None


def test_parse_event_timestamp_missing_returns_none():
    assert _parse_event_timestamp({}) is None


def test_parse_event_timestamp_garbage_returns_none():
    assert _parse_event_timestamp({"createdAt": "not-a-date"}) is None
    assert _parse_event_timestamp({"createdAt": []}) is None  # type: ignore[dict-item]


# ----------------------------------------------------- count_recent_self_messages

@pytest.fixture()
def fixed_now() -> float:
    # 1 minute after 18:00:00 UTC on 2026-06-01.
    base = _parse_event_timestamp({"createdAt": "2026-06-01T18:00:00Z"})
    assert base is not None
    return base + 60.0


def _talk(agent: str, when_iso: str) -> dict:
    return {
        "actionType": "AGENT_TALK",
        "agentName": agent,
        "createdAt": when_iso,
        "content": "hi",
    }


def test_count_filters_by_agent_and_type(fixed_now: float) -> None:
    events = [
        _talk("Alice", "2026-06-01T18:00:00Z"),
        _talk("Alice", "2026-06-01T17:55:00Z"),
        _talk("Bob", "2026-06-01T18:00:00Z"),
        {
            "actionType": "CONSOLIDATE",
            "agentName": "Alice",
            "createdAt": "2026-06-01T18:00:00Z",
        },
    ]
    assert (
        count_recent_self_messages(events, agent_name="Alice", now=fixed_now)
        == 2
    )


def test_count_respects_window(fixed_now: float) -> None:
    # 18:00 is within 600s of fixed_now; 17:30 is not (1800s gap).
    events = [
        _talk("Alice", "2026-06-01T18:00:00Z"),
        _talk("Alice", "2026-06-01T17:30:00Z"),
    ]
    assert (
        count_recent_self_messages(
            events,
            agent_name="Alice",
            window_seconds=600.0,
            now=fixed_now,
        )
        == 1
    )


def test_count_unparseable_timestamp_counted_as_recent(fixed_now: float) -> None:
    events = [{"actionType": "AGENT_TALK", "agentName": "Alice"}]
    assert (
        count_recent_self_messages(events, agent_name="Alice", now=fixed_now)
        == 1
    )


def test_count_ignores_non_mapping_entries(fixed_now: float) -> None:
    events = [
        _talk("Alice", "2026-06-01T18:00:00Z"),
        "not a dict",
        None,
    ]
    assert (
        count_recent_self_messages(events, agent_name="Alice", now=fixed_now)
        == 1
    )


def test_count_default_window_is_dedup_window() -> None:
    # Just verify the default matches the dedup window so the two helpers
    # are coherent if used together.
    assert DEFAULT_WINDOW_SECONDS == 600.0


# --------------------------------------------------------- should_throttle_self

def test_should_throttle_returns_false_below_threshold(
    fixed_now: float,
) -> None:
    events = [_talk("Alice", "2026-06-01T18:00:00Z")] * 3
    throttle, reason = should_throttle_self(
        events,
        agent_name="Alice",
        max_per_window=4,
        now=fixed_now,
    )
    assert throttle is False
    assert reason == ""


def test_should_throttle_returns_true_at_threshold(fixed_now: float) -> None:
    events = [_talk("Alice", "2026-06-01T18:00:00Z")] * 4
    throttle, reason = should_throttle_self(
        events,
        agent_name="Alice",
        max_per_window=4,
        now=fixed_now,
    )
    assert throttle is True
    assert "4 messages" in reason
    assert "threshold=4" in reason
    assert "consider waiting" in reason


def test_should_throttle_threshold_is_inclusive(fixed_now: float) -> None:
    events = [_talk("Alice", "2026-06-01T18:00:00Z")] * 5
    throttle, _ = should_throttle_self(
        events,
        agent_name="Alice",
        max_per_window=4,
        now=fixed_now,
    )
    assert throttle is True


def test_should_throttle_isolates_agents(fixed_now: float) -> None:
    # 10 events but all from Bob -- Alice has no quota issue.
    events = [_talk("Bob", "2026-06-01T18:00:00Z")] * 10
    throttle, _ = should_throttle_self(
        events,
        agent_name="Alice",
        max_per_window=4,
        now=fixed_now,
    )
    assert throttle is False
