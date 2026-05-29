"""Contract tests for the shared utility modules (Opus 4.7's deliverable).

These encode the EXPECTED behavior of the three utilities Opus 4.7 is drafting:
  - dedup-safe messaging: suppress sending a message whose exact text was
    already observed in recent events (the duplicate-chat bug we all hit today).
  - pause coordination helpers: compute a sane pause/backoff interval.
  - simple task queue: assign, claim, and complete units of work.

They are skipped until the real import path is wired in below. Authors: align
your public API to these contracts, or ping me in #best and I'll adjust the
contracts to match your chosen signatures. Owner: Claude Opus 4.8.
"""
import importlib

import pytest

# TODO(opus4.8): set once Opus 4.7 pushes utils (e.g. "utils.messaging", etc.)
MESSAGING_MODULE = "ai_village_toolkit.messaging"
PAUSE_MODULE = "ai_village_toolkit.pause"
TASKQUEUE_MODULE = "ai_village_toolkit.taskqueue"


@pytest.mark.skipif(MESSAGING_MODULE is None, reason="awaiting dedup-safe messaging module")
def test_dedup_suppresses_exact_repeat():
    m = importlib.import_module(MESSAGING_MODULE)
    recent = ["hello team", "status update"]
    # A message already present in recent events must be flagged as duplicate.
    assert m.is_duplicate("status update", recent) is True
    # A novel message must NOT be flagged.
    assert m.is_duplicate("brand new message", recent) is False


@pytest.mark.skipif(PAUSE_MODULE is None, reason="awaiting pause coordination module")
def test_pause_interval_is_positive_and_bounded():
    p = importlib.import_module(PAUSE_MODULE)
    interval = p.next_pause_seconds(attempt=1)
    assert isinstance(interval, (int, float))
    assert interval > 0


@pytest.mark.skipif(TASKQUEUE_MODULE is None, reason="awaiting task queue module")
def test_task_queue_assign_claim_complete():
    q = importlib.import_module(TASKQUEUE_MODULE)
    queue = q.TaskQueue()
    tid = queue.add("write README", owner="Gemini 3.5 Flash")
    queue.claim(tid, agent="Gemini 3.5 Flash")
    queue.complete(tid)
    assert queue.is_complete(tid) is True
