"""End-to-end coordination demo for ai_village_toolkit.

Simulates a small #best workflow that exercises every public module:

- protocol.StatusTracker / CoordinationMessage / WorkAssignment / AgentStatus
- taskqueue.TaskQueue (work distribution)
- messaging.is_duplicate (dedup-safe chat)
- pause.next_pause_seconds (cadenced waits)
- history.normalize_event / latest_agent_talk / has_duplicate_agent_talk
  (parsing the village event feed)

Run with:
    python examples/coordination_demo.py
"""

from __future__ import annotations

import time
from typing import List

from ai_village_toolkit import (
    AgentStatus,
    CoordinationMessage,
    MessageDeduper,
    MessageType,
    StatusTracker,
    TaskQueue,
    WorkAssignment,
    has_duplicate_agent_talk,
    is_duplicate,
    latest_agent_talk,
    next_pause_seconds,
    normalize_event,
)

ROOM = "#best"
LEADER = "[Temporary] Fine-tuned Leader"
TEAM = ["Claude Opus 4.7", "Claude Opus 4.8", "Gemini 3.5 Flash", "GPT-5.5", "Kimi K2.6"]


def header(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    # ---- 1. Bootstrap the room ----
    header("1. Bootstrap room + StatusTracker")
    tracker = StatusTracker(room=ROOM)
    for agent in TEAM:
        tracker.update_status(agent, AgentStatus.IDLE)
    tracker.update_status(LEADER, AgentStatus.COORDINATING)
    print(f"Statuses bootstrapped for {len(TEAM)+1} agents.")

    # ---- 2. Leader puts work in a TaskQueue ----
    header("2. Leader populates TaskQueue")
    queue = TaskQueue(id_prefix="toolkit-")
    tasks = [
        ("Write protocol module", "Kimi K2.6"),
        ("Write utility modules", "Claude Opus 4.7"),
        ("Write integration tests", "Claude Opus 4.8"),
        ("Write history helpers", "GPT-5.5"),
        ("Write README and docstrings", "Gemini 3.5 Flash"),
    ]
    task_ids = []
    for desc, owner in tasks:
        tid = queue.add(desc, owner=owner)
        task_ids.append((tid, owner))
        print(f"  + {tid}: {desc} (suggested owner={owner})")

    # ---- 3. Each agent claims + reports STATUS_UPDATE ----
    header("3. Agents claim + report status")
    for tid, owner in task_ids:
        queue.claim(tid, agent=owner)  # both agent= and owner= work
        tracker.update_status(owner, AgentStatus.WORKING)
        msg = CoordinationMessage(
            msg_type=MessageType.STATUS_UPDATE,
            sender=owner,
            content=f"Claimed {tid}",
            room=ROOM,
            task_id=tid,
        )
        tracker.log_message(msg)
    print(f"  In-flight assignments: {len(queue.claimed_by(TEAM[0])) + sum(1 for t,_ in task_ids[1:])}")

    # ---- 4. Dedup-safe chat: refuse to repost identical updates ----
    header("4. Dedup-safe chat using MessageDeduper")
    deduper = MessageDeduper(agent_name="Claude Opus 4.7", similarity_threshold=0.5)
    candidates = [
        "Utility modules pushed; full suite green.",
        "Utility modules pushed; full suite green.",  # exact dup
        "Utility modules are pushed and the full suite is green.",  # near dup
        "Starting on the coordination demo example next.",
    ]
    sent: List[str] = []
    for cand in candidates:
        if deduper.would_be_duplicate(cand):
            print(f"  [SKIP] dup: {cand!r}")
            continue
        deduper.record(cand)
        sent.append(cand)
        print(f"  [SEND] {cand!r}")
    assert candidates[3] in sent  # the genuinely new message got through

    # ---- 5. Pure-functional is_duplicate against an event feed ----
    header("5. is_duplicate vs. simulated event feed")
    feed = [
        {"actionType": "AGENT_TALK", "agentName": "Claude Opus 4.7",
         "content": "Utility modules pushed; full suite green."},
        {"actionType": "AGENT_TALK", "agentName": "Claude Opus 4.8",
         "content": "Tests are now 31/0."},
    ]
    candidate = "Utility modules pushed - full suite green!"
    dup = is_duplicate(candidate, feed, agent_name="Claude Opus 4.7")
    print(f"  candidate is duplicate against feed? {dup}")

    # ---- 6. history helpers: latest agent talk + duplicate detection ----
    header("6. history helpers")
    norm = [normalize_event(e) for e in feed]
    last = latest_agent_talk(norm, agent_name="Claude Opus 4.8")
    print(f"  latest_agent_talk(Opus 4.8) -> {last.content if last else None!r}")
    dup_feed = has_duplicate_agent_talk(
        norm,
        agent_name="Claude Opus 4.7",
        draft="Utility modules pushed; full suite green.",
    )
    print(f"  has_duplicate_agent_talk -> {dup_feed}")

    # ---- 7. Complete a task and update tracker ----
    header("7. Complete a task")
    tid_done = task_ids[1][0]  # Opus 4.7's task
    queue.complete(tid_done, result="68616d5: 23 tests green")
    tracker.update_status("Claude Opus 4.7", AgentStatus.IDLE)
    tracker.log_message(CoordinationMessage(
        msg_type=MessageType.WORK_COMPLETE,
        sender="Claude Opus 4.7",
        content="Utility modules merged",
        room=ROOM,
        task_id=tid_done,
    ))
    print(f"  is_complete({tid_done}) -> {queue.is_complete(tid_done)}")

    # ---- 8. Pause cadence: exponential backoff ----
    header("8. next_pause_seconds backoff")
    schedule = [next_pause_seconds(attempt=i) for i in range(1, 8)]
    print(f"  attempts 1..7 -> {schedule}")
    assert schedule == sorted(schedule), "backoff should be monotonic"
    assert schedule[-1] <= 600, "cap should hold"

    # ---- 9. Final summary ----
    header("9. Final StatusTracker.summary()")
    summary = tracker.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nDemo complete. All modules wired together cleanly.")


if __name__ == "__main__":
    main()
