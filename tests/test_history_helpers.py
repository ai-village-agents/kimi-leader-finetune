from ai_village_toolkit.history import (
    VillageEvent,
    filter_events,
    format_brief,
    has_duplicate_agent_talk,
    latest_agent_talk,
    normalize_event,
)


def test_normalize_event_extracts_nested_village_fields():
    raw = {
        "createdAt": "2026-05-29T18:52:20",
        "data": {
            "actionType": "AGENT_TALK",
            "agentName": "[Temporary] Fine-tuned Leader",
            "content": "Goal locked in",
            "roomId": "best-room",
        },
    }
    event = normalize_event(raw)
    assert event == VillageEvent(
        created_at="2026-05-29T18:52:20",
        action_type="AGENT_TALK",
        agent_name="[Temporary] Fine-tuned Leader",
        content="Goal locked in",
        room_id="best-room",
    )


def test_filter_events_supports_room_agent_and_contains():
    events = [
        VillageEvent("001", "AGENT_TALK", "GPT-5.5", "History helper ready", "best"),
        VillageEvent("002", "AGENT_TALK", "Gemini", "README ready", "best"),
        VillageEvent("003", "PAUSE", "GPT-5.5", "", "rest"),
    ]
    assert filter_events(events, room_id="best", agent_name="GPT-5.5", contains="history") == [
        events[0]
    ]


def test_latest_agent_talk_uses_timestamp_order():
    events = [
        VillageEvent("001", "AGENT_TALK", "GPT-5.5", "old"),
        VillageEvent("003", "PAUSE", "GPT-5.5", "pause"),
        VillageEvent("002", "AGENT_TALK", "GPT-5.5", "new"),
    ]
    assert latest_agent_talk(events, "GPT-5.5") == events[2]


def test_has_duplicate_agent_talk_matches_exact_stripped_content():
    events = [VillageEvent("001", "AGENT_TALK", "GPT-5.5", "  same draft  ")]
    assert has_duplicate_agent_talk(events, agent_name="GPT-5.5", draft="same draft")
    assert not has_duplicate_agent_talk(events, agent_name="GPT-5.5", draft="same")


def test_format_brief_limits_and_truncates():
    events = [
        VillageEvent("001", "AGENT_TALK", "A", "first"),
        VillageEvent("002", "AGENT_TALK", "B", "second " + "x" * 40),
    ]
    brief = format_brief(events, limit=1, width=25)
    assert "001" not in brief
    assert "002 AGENT_TALK B:" in brief
    assert brief.endswith("…")
