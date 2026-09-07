"""Bounded, provider-neutral conversational context for follow-up questions.

The browser owns the short-lived history and sends at most four earlier messages.
This module decides when a new question actually needs that history.  It deliberately
uses deterministic text rules rather than a second LLM call: one student turn must
remain one paid/quota-limited generation request (ADR-0018).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Sequence

MAX_HISTORY_MESSAGES = 4
MAX_HISTORY_MESSAGE_CHARS = 1200

_REFERENCE_RE = re.compile(
    r"\b(it|its|that|this|they|them|their|those|these|one|ones|there|then)\b",
    re.IGNORECASE,
)
_CONTINUATION_RE = re.compile(
    r"^(and|also|but|okay|ok|so|then|what about|how about)\b", re.IGNORECASE
)
_SHORT_QUESTION_RE = re.compile(r"^(where|when|who|why|how)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ConversationMessage:
    """One already-sanitized earlier turn supplied by the client."""

    role: Literal["user", "assistant"]
    content: str


def bounded_history(history: Sequence[ConversationMessage] | None) -> list[ConversationMessage]:
    """Return the newest valid, non-empty messages within the hard prompt budget."""
    if not history:
        return []
    return [
        ConversationMessage(message.role, message.content[:MAX_HISTORY_MESSAGE_CHARS])
        for message in history[-MAX_HISTORY_MESSAGES:]
        if message.content.strip()
    ]


def is_contextual_followup(
    question: str, history: Sequence[ConversationMessage] | None
) -> bool:
    """Whether resolving the question plausibly requires an earlier turn.

    Referential words cover common follow-ups ("where do I get it?", "is that
    mandatory?").  Continuation phrases cover explicit topic carry-over.  Very
    short wh-questions are treated as elliptical; longer, self-contained questions
    omit history so topic switches are not polluted by the previous subject.
    """
    prior = bounded_history(history)
    if not any(message.role == "user" for message in prior):
        return False

    text = " ".join(question.strip().split())
    if _REFERENCE_RE.search(text) or _CONTINUATION_RE.search(text):
        return True
    return bool(_SHORT_QUESTION_RE.search(text) and len(text.split()) <= 5)


def build_retrieval_query(
    question: str, history: Sequence[ConversationMessage] | None
) -> str:
    """Resolve an elliptical follow-up into a useful single retrieval query.

    Only prior *user* text is used for retrieval.  Assistant answers may contain
    URLs and verbose phrasing that dilute vector and keyword search; they remain
    available to the answer prompt for references such as "what does that mean?".
    """
    prior = bounded_history(history)
    if not is_contextual_followup(question, prior):
        return question

    user_turns = [m.content for m in prior if m.role == "user"][-2:]
    earlier = "\n".join(f"- {turn}" for turn in user_turns)
    return f"Earlier student question(s):\n{earlier}\nCurrent follow-up: {question}"


def format_prompt_history(
    question: str, history: Sequence[ConversationMessage] | None
) -> str:
    """Format bounded history only when the current question depends on it."""
    prior = bounded_history(history)
    if not is_contextual_followup(question, prior):
        return ""
    lines = [f"{m.role.upper()}: {m.content}" for m in prior]
    return "\n".join(lines)
