"""Integration tests for ai_village_toolkit.history (GPT-5.5's helpers).

Authored by Claude Opus 4.8 (review + integration testing role).
"""
from ai_village_toolkit import (
    normalize_event,
    filter_events,
    latest_agent_talk,
    has_duplicate_agent_talk,
    format_brief,
    VillageEvent,
    agent_activity_summary,
)


def _flat(ts, agent, content, action="AGENT_TALK"):
    return {"createdAt": ts, "actionType": action, "agentName": agent, "content": content}


def test_normalize_flat_event():
    e = normalize_event(_flat("2026-05-29T12:00", "Claude Opus 4.8", "hello"))
    assert isinstance(e, VillageEvent)
    assert e.agent_name == "Claude Opus 4.8"
    assert e.action_type == "AGENT_TALK"
    assert e.content == "hello"


def test_normalize_nested_data_shape():
    raw = {
        "createdAt": "2026-05-29T12:01",
        "data": {"actionType": "AGENT_TALK", "agentName": "GPT-5.5", "content": "status"},
    }
    e = normalize_event(raw)
    assert e.agent_name == "GPT-5.5"
    assert e.content == "status"
    assert e.action_type == "AGENT_TALK"


def test_normalize_alternate_content_keys():
    # consolidate events carry nextSessionGoal rather than content
    e = normalize_event({"createdAt": "t", "actionType": "CONSOLIDATE",
                         "agentName": "X", "nextSessionGoal": "do thing"})
    assert e.content == "do thing"


def test_filter_by_agent_and_text():
    evs = [
        normalize_event(_flat("t1", "A", "build the toolkit")),
        normalize_event(_flat("t2", "B", "review tests")),
        normalize_event(_flat("t3", "A", "toolkit shipped")),
    ]
    by_agent = filter_events(evs, agent_name="A")
    assert [e.created_at for e in by_agent] == ["t1", "t3"]
    by_text = filter_events(evs, contains="TOOLKIT")  # case-insensitive
    assert len(by_text) == 2


def test_filter_since_timestamp():
    evs = [normalize_event(_flat(f"t{i}", "A", str(i))) for i in range(4)]
    assert [e.created_at for e in filter_events(evs, since_created_at="t2")] == ["t2", "t3"]


def test_latest_agent_talk_picks_newest():
    evs = [
        normalize_event(_flat("2026-05-29T11:00", "A", "old")),
        normalize_event(_flat("2026-05-29T13:00", "A", "new")),
        normalize_event(_flat("2026-05-29T12:00", "B", "other")),
    ]
    latest = latest_agent_talk(evs, "A")
    assert latest is not None and latest.content == "new"
    assert latest_agent_talk(evs, "Nobody") is None


def test_has_duplicate_ignores_edge_whitespace():
    evs = [normalize_event(_flat("t1", "A", "hello team"))]
    assert has_duplicate_agent_talk(evs, agent_name="A", draft="  hello team \n")
    assert not has_duplicate_agent_talk(evs, agent_name="A", draft="hello world")
    assert not has_duplicate_agent_talk(evs, agent_name="B", draft="hello team")


def test_format_brief_limit_and_truncation():
    evs = [normalize_event(_flat(f"t{i}", "A", "x" * 50)) for i in range(5)]
    out = format_brief(evs, limit=2, width=10)
    lines = out.splitlines()
    assert len(lines) == 2
    assert lines[-1].endswith("…")


def _ev(agent, action, created_at="2026-06-04T17:00:00Z", room="rest", content=""):
    """Tiny builder for VillageEvent instances in summary tests."""
    return VillageEvent(
        created_at=created_at,
        action_type=action,
        agent_name=agent,
        content=content,
        room_id=room,
    )


def test_agent_activity_summary_counts_actions_and_rooms():
    events = [
        _ev("Claude Opus 4.7", "AGENT_TALK", "2026-06-04T16:00:00Z", room="rest"),
        _ev("Claude Opus 4.7", "PAUSE", "2026-06-04T16:30:00Z", room="rest"),
        _ev("Claude Opus 4.7", "PAUSE", "2026-06-04T17:00:00Z", room="best"),
        _ev("Claude Opus 4.7", "AGENT_TALK", "2026-06-04T17:30:00Z", room="rest"),
        _ev("Other Agent", "AGENT_TALK", "2026-06-04T17:45:00Z", room="rest"),
    ]
    summary = agent_activity_summary(events, "Claude Opus 4.7")
    assert summary["agent_name"] == "Claude Opus 4.7"
    assert summary["event_count"] == 4
    assert summary["action_counts"] == {"AGENT_TALK": 2, "PAUSE": 2}
    assert summary["last_event_at"] == "2026-06-04T17:30:00Z"
    assert summary["last_action_type"] == "AGENT_TALK"
    assert summary["rooms"] == ["best", "rest"]


def test_agent_activity_summary_empty_when_no_matches():
    events = [_ev("Other Agent", "AGENT_TALK")]
    summary = agent_activity_summary(events, "Claude Opus 4.7")
    assert summary == {
        "agent_name": "Claude Opus 4.7",
        "event_count": 0,
        "action_counts": {},
        "last_event_at": "",
        "last_action_type": "",
        "rooms": [],
    }


def test_agent_activity_summary_handles_none_room_id():
    events = [
        VillageEvent(
            created_at="2026-06-04T18:00:00Z",
            action_type="CONSOLIDATE",
            agent_name="Claude Opus 4.7",
            content="",
            room_id=None,
        ),
    ]
    summary = agent_activity_summary(events, "Claude Opus 4.7")
    assert summary["rooms"] == [""]
    assert summary["action_counts"] == {"CONSOLIDATE": 1}


def test_normalize_event_accepts_snake_case_flat():
    raw = {
        "created_at": "2026-06-04T17:30:00Z",
        "action_type": "AGENT_TALK",
        "agent_name": "Claude Opus 4.7",
        "content": "hello",
        "room_id": "18faa501-bc16-41c9-9f2c-111a7e737df6",
    }
    ev = normalize_event(raw)
    assert ev.created_at == "2026-06-04T17:30:00Z"
    assert ev.action_type == "AGENT_TALK"
    assert ev.agent_name == "Claude Opus 4.7"
    assert ev.content == "hello"
    assert ev.room_id == "18faa501-bc16-41c9-9f2c-111a7e737df6"


def test_normalize_event_accepts_snake_case_nested_data():
    raw = {
        "createdAt": "2026-06-04T17:35:00Z",
        "data": {
            "action_type": "CONSOLIDATE",
            "agent_name": "Claude Opus 4.7",
            "next_session_goal": "next goal text",
            "room_id": None,
        },
    }
    ev = normalize_event(raw)
    assert ev.action_type == "CONSOLIDATE"
    assert ev.agent_name == "Claude Opus 4.7"
    assert ev.content == "next goal text"
    assert ev.room_id is None
