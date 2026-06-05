from ai_village_toolkit.history import (
    VillageEvent,
    consecutive_pauses_for_agent,
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



def test_consecutive_pauses_counts_trailing_pause_run():
    events = [
        VillageEvent("001", "AGENT_TALK", "Opus 4.7", "hello"),
        VillageEvent("002", "PAUSE", "Opus 4.7", ""),
        VillageEvent("003", "PAUSE", "Opus 4.7", ""),
        VillageEvent("004", "PAUSE", "Opus 4.7", ""),
    ]
    assert consecutive_pauses_for_agent(events, "Opus 4.7") == 3


def test_consecutive_pauses_resets_after_other_action():
    events = [
        VillageEvent("001", "PAUSE", "Opus 4.7", ""),
        VillageEvent("002", "PAUSE", "Opus 4.7", ""),
        VillageEvent("003", "AGENT_TALK", "Opus 4.7", "back"),
    ]
    assert consecutive_pauses_for_agent(events, "Opus 4.7") == 0


def test_consecutive_pauses_ignores_other_agents():
    events = [
        VillageEvent("001", "PAUSE", "Opus 4.7", ""),
        VillageEvent("002", "AGENT_TALK", "Gemini", "hi"),
        VillageEvent("003", "PAUSE", "Opus 4.7", ""),
        VillageEvent("004", "PAUSE", "Opus 4.7", ""),
    ]
    # Trailing run for Opus 4.7 (last two PAUSEs) — Gemini's AGENT_TALK
    # does not interrupt because we filter to the target agent first.
    assert consecutive_pauses_for_agent(events, "Opus 4.7") == 3


def test_consecutive_pauses_coerces_raw_mapping_input():
    raw = [
        {"createdAt": "001", "data": {"actionType": "AGENT_TALK", "agentName": "Opus 4.7", "content": "x"}},
        {"createdAt": "002", "data": {"actionType": "PAUSE", "agentName": "Opus 4.7"}},
        {"createdAt": "003", "data": {"actionType": "PAUSE", "agentName": "Opus 4.7"}},
    ]
    assert consecutive_pauses_for_agent(raw, "Opus 4.7") == 2


def test_consecutive_pauses_handles_empty_and_unknown():
    assert consecutive_pauses_for_agent([], "Anyone") == 0
    events = [VillageEvent("001", "PAUSE", "Opus 4.7", "")]
    assert consecutive_pauses_for_agent(events, "Other") == 0
