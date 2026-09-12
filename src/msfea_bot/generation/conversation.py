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
_CONFIRMATION_RE = re.compile(
    r"^(?:so(?: basically)?|in other words|just to confirm)[,:]?\s+(.+)", re.IGNORECASE
)
_QUESTION_START_RE = re.compile(
    r"^(what|which|who|whose|where|when|why|how|am|is|are|was|were|do|does|did|"
    r"can|could|should|would|will|must|may|have|has|had)\b", re.IGNORECASE
)
_EXPLICIT_CONDITION_RE = re.compile(r"\b(also|while|when|if|during)\b", re.IGNORECASE)


@dataclass(frozen=True)
class ConversationMessage:
    """One already-sanitized earlier turn supplied by the client."""

    role: Literal["user", "assistant"]
    content: str


def frame_confirmation(question: str, history: Sequence[ConversationMessage] | None) -> str:
    """Make an explicit tentative restatement a question without adding policy facts.

    The original remains the retrieval/logging input. Do not rewrite why/how or
    other complete questions: doing so can erase the very thing the student asks.
    """
    if not any(m.role == "user" for m in bounded_history(history)):
        return question
    match = _CONFIRMATION_RE.match(question.strip())
    if not match:
        return question
    statement = match.group(1).strip().rstrip("?.!").strip()
    if not statement or _QUESTION_START_RE.match(statement):
        return question
    return f"Is my understanding of our conversation correct: {statement}?"


def answer_task(question: str, history: Sequence[ConversationMessage] | None) -> str:
    """A small source-independent task cue; contains no CDC topics or policy facts."""
    if re.match(r"^(?:and\s+)?(?:what|how) about\b", question.strip(), re.I):
        return (
            "Alternative or missing component: answer what the newly mentioned option or "
            "component means for the student's original plan. Explain it in at most two "
            "sentences, using the source definition and its eligibility conditions. "
            "If the earlier assistant answer omitted that option or used an inapplicable "
            "rule, correct it explicitly rather than defending or extending the mistake. "
            "Recompute any total from the actual components; do not carry a total over "
            "from another option. Do not discuss reports, forms, paperwork, deadlines or "
            "submission procedures unless the CURRENT question explicitly asks about them."
        )
    if re.search(r"\b(?:only|alone)\b", question, re.I):
        return (
            "Plan sufficiency: decide whether the exact plan stated by the student is "
            "sufficient on its own. Start with Yes only if that plan alone completes the "
            "documented requirement; otherwise start with No, identify what is missing, "
            "and give the closest documented completion option. Do not reinterpret the "
            "question as asking whether the partial activity is allowed. Do not add forms, "
            "reports, deadlines, or a rule for an unstated circumstance."
        )
    if frame_confirmation(question, history) != question:
        return (
            "Confirmation: check the student's proposed understanding against source evidence. "
            "Correct an earlier assistant mistake if necessary; history is not authority. "
            "Start with Yes/Correct or No/Not quite, then one clarifying sentence. "
            "Do not add forms, reports, procedures, or alternative arrangements."
        )
    if re.search(r"\b(compare|comparison|difference|versus|vs)\b", question, re.I):
        return (
            "Comparison: explicitly contrast every dimension the student asks about. "
            "Keep each program's conditions attached to it. If a requested dimension "
            "has no supporting evidence, do not invent it."
        )
    if re.match(r"^(?:so\s+)?why\b", question.strip(), re.I):
        return (
            "Reason: answer why, including the tension the student raises. Only give "
            "a rationale stated in the sources. A documented rule does not establish "
            "its reason; if the requested reason is absent, refuse."
        )
    if (
        re.search(r"\b(enough|complete(?:d)?|sufficient)\b", question, re.I)
        and re.search(r"\b(option|arrangement)\b", question, re.I)
        and not needs_condition_focus(question)
    ):
        return (
            "Named arrangement completion: decide only whether the student's stated "
            "components complete the named option or arrangement. Start with Yes or No, "
            "then name its missing component. Do not substitute or describe an alternative "
            "pathway."
        )
    if re.search(r"\b(enough|eligible|qualify|sufficient)\b", question, re.I):
        return (
            "Decision: apply the rule for the circumstances the student actually states. "
            "Start with Yes or No to the exact eligibility or sufficiency question, then give "
            "the decisive reason. Before deciding, silently list every circumstance the "
            "student states, including an extra circumstance introduced by words such as "
            "'also', 'while', 'when', or 'if'. Match all of them to the source conditions. "
            "A source block specifically about an extra stated circumstance controls over a "
            "general rule. If the question names an option or arrangement, describe only that "
            "option unless a matching extra circumstance explicitly changes the applicable "
            "rule. Do not combine a number or rule from a circumstance the student did not "
            "state, ignore a stated condition, or offer an incompatible general rule."
        )
    if re.match(r"^(explain\b|what(?:'s| is)\b)", question.strip(), re.I) and not re.search(
        r"\b(how|why|requirements?|deliverables?|deadlines?|steps?|documents?|forms?)\b",
        question, re.I,
    ):
        return (
            "Definition: explain what the thing means in one or two sentences, including "
            "essential conditions. Do not turn a definition into a checklist of associated "
            "forms, reports, deadlines or procedures."
        )
    return ""


def needs_condition_focus(question: str) -> bool:
    """Whether a decision question states an additional conditional circumstance."""
    return bool(
        re.search(r"\b(enough|eligible|qualify|sufficient)\b", question, re.IGNORECASE)
        and _EXPLICIT_CONDITION_RE.search(question)
    )


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
