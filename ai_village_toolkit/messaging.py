"""Dedup-safe messaging helpers for AI Village agents.

Problem this module solves
--------------------------
In the AI Village scaffold, an agent's *own* outgoing chat message is
sometimes echoed back into the per-turn ``user_event`` feed at the moment the
agent is preparing to send it (or even slightly before, depending on the
plumbing). Naive agents see the echo, conclude "my last send must not have
landed", and re-send the same content. The result is a duplicated chat post
(or, depending on the platform, a system-level dedup that silently drops the
re-send and wastes the agent's turn).

This module gives agents two cheap-and-correct ways to avoid the bug:

1. ``MessageDeduper`` -- a tiny per-process cache that fingerprints recent
   outgoing messages and reports whether the agent has just sent a
   sufficiently-similar message.
2. ``feed_contains_own_recent_message(events, agent_name, candidate)`` --
   a stateless helper that inspects a recent event list and returns ``True``
   if the agent's name already appears as the speaker of a message similar
   to ``candidate``.

Both functions use the same normalization + similarity check, so an agent
can use either depending on what is more convenient.

Typical usage
-------------

.. code-block:: python

    from utils.dedup_safe_messaging import MessageDeduper

    deduper = MessageDeduper(agent_name="Claude Opus 4.7")

    def safe_send(text, recent_events):
        if deduper.would_be_duplicate(text, recent_events):
            return False  # skip the send_message_to_chat call
        deduper.record(text)
        send_message_to_chat(text)
        return True

The intended invariant is:

    *Before* calling ``send_message_to_chat``, always pass the latest event
    feed and the candidate text through ``would_be_duplicate``. If it returns
    ``True``, do NOT send.

This module is intentionally dependency-free (stdlib only) so it can be
vendored into any village agent's scaffold.
"""

from __future__ import annotations

import re
import time
import unicodedata
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Iterable, Mapping, Optional, Sequence

__all__ = [
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_WINDOW_SECONDS",
    "MessageDeduper",
    "feed_contains_own_recent_message",
    "normalize_text",
    "similarity",
]

# A pair of messages with similarity at or above this fraction of shared
# normalized tokens are treated as duplicates by default. 0.7 is empirically a
# good cutoff: it catches paraphrases and "small edit" duplicates but does not
# flag two genuinely-different status updates as duplicates of each other.
DEFAULT_SIMILARITY_THRESHOLD: float = 0.7

# Only consider events / sent messages from within this many seconds when
# checking for duplicates. 600s = 10 min is a generous default for #best.
DEFAULT_WINDOW_SECONDS: float = 600.0


_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]")


def normalize_text(text: str) -> str:
    """Lower-case, strip accents, collapse whitespace, drop punctuation.

    Two messages that differ only in punctuation, capitalization, or trailing
    whitespace should compare equal under this normalization.
    """
    if text is None:
        return ""
    # Decompose accents and drop combining marks.
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    lowered = stripped.lower()
    no_punct = _PUNCT_RE.sub(" ", lowered)
    collapsed = _WS_RE.sub(" ", no_punct).strip()
    return collapsed


def _tokens(text: str) -> set[str]:
    return set(normalize_text(text).split())


def similarity(a: str, b: str) -> float:
    """Jaccard similarity over normalized token sets.

    Returns 1.0 for identical normalized messages, 0.0 for fully disjoint
    messages. Empty inputs are treated as 0.0 similarity to any non-empty
    input (and 1.0 to each other).
    """
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    inter = ta & tb
    union = ta | tb
    return len(inter) / len(union)


@dataclass
class _SentRecord:
    text: str
    sent_at: float


@dataclass
class MessageDeduper:
    """Tracks an agent's own recently-sent messages and flags duplicates.

    Parameters
    ----------
    agent_name:
        The name (as it appears in the chat feed) of the agent using this
        deduper. Used by :meth:`would_be_duplicate` to look up own-authored
        messages in the supplied event list.
    similarity_threshold:
        Two messages are treated as duplicates when their normalized-token
        Jaccard similarity is ``>=`` this value.
    window_seconds:
        Only messages sent within this many seconds in the past are
        considered candidates for duplication.
    max_history:
        Cap on how many recent send records to keep in memory.
    """

    agent_name: str
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    window_seconds: float = DEFAULT_WINDOW_SECONDS
    max_history: int = 64
    _history: Deque[_SentRecord] = field(default_factory=deque, init=False, repr=False)

    # ------------------------------------------------------------------ basics

    def record(self, text: str, *, now: Optional[float] = None) -> None:
        """Record that the agent just sent ``text``.

        Call this immediately after a successful ``send_message_to_chat``.
        """
        if now is None:
            now = time.time()
        self._history.append(_SentRecord(text=text, sent_at=now))
        while len(self._history) > self.max_history:
            self._history.popleft()

    def _prune(self, now: float) -> None:
        cutoff = now - self.window_seconds
        while self._history and self._history[0].sent_at < cutoff:
            self._history.popleft()

    # -------------------------------------------------------------- core check

    def would_be_duplicate(
        self,
        candidate: str,
        recent_events: Optional[Sequence[Mapping]] = None,
        *,
        now: Optional[float] = None,
    ) -> bool:
        """Return True iff sending ``candidate`` would duplicate a recent message.

        The decision combines two evidence sources:

        1. The agent's local send history (in case the agent loop ran multiple
           times without seeing its own message in the feed yet).
        2. The supplied ``recent_events`` -- a list of dicts in the AI Village
           event format, each typically containing ``actionType``,
           ``agentName``, and ``content`` keys. Only events authored by
           ``self.agent_name`` are inspected.

        Either source returning a positive hit is enough to flag the
        candidate as a duplicate. This keeps the helper safe in both
        directions: it catches the "I already sent this two turns ago" case
        AND the "the system pre-echoed my own outgoing message" case.
        """
        if now is None:
            now = time.time()
        self._prune(now)
        thr = self.similarity_threshold

        for rec in self._history:
            if similarity(candidate, rec.text) >= thr:
                return True

        if recent_events:
            if feed_contains_own_recent_message(
                recent_events,
                agent_name=self.agent_name,
                candidate=candidate,
                similarity_threshold=thr,
            ):
                return True

        return False


def feed_contains_own_recent_message(
    events: Iterable[Mapping],
    *,
    agent_name: str,
    candidate: str,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> bool:
    """Stateless dedup probe for the AI Village event feed.

    Walks ``events`` (most-recent-last or most-recent-first, either works)
    and returns ``True`` as soon as it finds an ``AGENT_TALK`` event whose
    ``agentName`` matches ``agent_name`` and whose ``content`` is sufficiently
    similar to ``candidate``.
    """
    for ev in events:
        if not isinstance(ev, Mapping):
            continue
        if ev.get("actionType") != "AGENT_TALK":
            continue
        if ev.get("agentName") != agent_name:
            continue
        content = ev.get("content") or ""
        if similarity(candidate, content) >= similarity_threshold:
            return True
    return False


# ----------------------------------------------------------------------- thin
# Convenience wrapper matching Opus 4.8's pytest contract signature.

def is_duplicate(
    text: str,
    recent: Optional[Sequence] = None,
    *,
    agent_name: Optional[str] = None,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> bool:
    """Pure-functional dedup probe.

    ``recent`` may be a list of event dicts (AI Village format with
    ``actionType`` / ``agentName`` / ``content`` keys), OR a plain list of
    strings (each string treated as the content of a prior message). This
    keeps the helper convenient both for raw event feeds and for simple
    log-style usage.

    ``agent_name`` only matters for the dict-form events: when supplied, only
    events authored by that agent are inspected. With strings, every entry is
    inspected.
    """
    if not recent:
        return False
    for item in recent:
        if isinstance(item, str):
            if similarity(text, item) >= similarity_threshold:
                return True
            continue
        if isinstance(item, Mapping):
            if item.get("actionType") != "AGENT_TALK":
                continue
            if agent_name is not None and item.get("agentName") != agent_name:
                continue
            content = item.get("content") or ""
            if similarity(text, content) >= similarity_threshold:
                return True
    return False
