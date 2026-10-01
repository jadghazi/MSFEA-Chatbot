"""Bounded, provider-neutral conversational context for follow-up questions.

The browser owns the short-lived history and sends at most eight earlier messages.
This module decides when a new question actually needs that history.  It deliberately
uses deterministic text rules rather than a second LLM call: one student turn must
remain one paid/quota-limited generation request (ADR-0018).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Sequence

MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_MESSAGE_CHARS = 1200

_REFERENCE_RE = re.compile(
    r"\b(it|its|that|this|they|them|their|those|these|one|ones|other|another|"
    r"option|alternative|former|latter|there|then)\b",
    re.IGNORECASE,
)
_CONTINUATION_RE = re.compile(r"^(and|also|but|okay|ok|so|then|actually|instead)\b", re.IGNORECASE)
_WHAT_ABOUT_RE = re.compile(r"^(?:and\s+)?(?:what|how) about\b", re.IGNORECASE)
_CONFIRMATION_RE = re.compile(
    r"^(?:so(?: basically)?|in other words|just to confirm)[,:]?\s+(.+)", re.IGNORECASE
)
_QUESTION_START_RE = re.compile(
    r"^(what|which|who|whose|where|when|why|how|am|is|are|was|were|do|does|did|"
    r"can|could|should|would|will|must|may|have|has|had)\b", re.IGNORECASE
)
_EXPLICIT_CONDITION_RE = re.compile(r"\b(also|while|when|if|during)\b", re.IGNORECASE)
_GENERIC_REFERENTS = frozenset({
    "answer", "application", "approval", "deadline", "document", "form", "letter",
    "link", "option", "process", "report", "requirement", "step", "submission",
})
_QUERY_FILLER = frozenset({
    "a", "about", "an", "and", "are", "at", "be", "can", "could", "do", "does",
    "for", "from", "get", "how", "i", "in", "is", "it", "me", "my", "of", "or",
    "should", "that", "the", "this", "to", "what", "when", "where", "which",
    "who", "why", "would", "you",
})
_RELATIVE_THAT_RE = re.compile(
    r"\b(?:a|an|the|my)\s+\w+(?:\s+\w+)?\s+that\s+"
    r"(?:starts?|ends?|begins?|is|was|has|had|offers?|requires?|allows?|provides?)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ConversationMessage:
    """One already-sanitized earlier turn supplied by the client."""

    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class RetrievalPlan:
    """One compact resolved query, optionally paired with the literal question."""

    query: str
    standalone_query: str | None = None


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


def contextual_question(question: str, history: Sequence[ConversationMessage] | None) -> str:
    """Name the resolved subject in the answer task as well as in retrieval."""
    if not re.fullmatch(r"how long should (?:the )?[a-z]{3,}\s?\d{3} be\??",
                        question.strip(), re.I):
        framed = frame_confirmation(question, history)
        if framed != question:
            return framed
        plan = retrieval_plan(question, history)
        has_reference = re.search(
            r"\b(it|its|that|this|they|them|those|these)\b", question, re.I
        )
        if is_contextual_followup(question, history) and (
            plan.standalone_query is None or has_reference
        ):
            return plan.query
        return question
    previous = [m.content for m in bounded_history(history) if m.role == "user"]
    if not previous:
        return question
    return (
        f"{question}\nImmediately preceding student question: {previous[-1]}\n"
        "If this could mean either the course or the item just discussed, ask which duration "
        "the student means. Do not silently choose one."
    )


def answer_task(question: str, history: Sequence[ConversationMessage] | None) -> str:
    """A small source-independent task cue; contains no CDC topics or policy facts."""
    if _WHAT_ABOUT_RE.match(question.strip()) and is_contextual_followup(question, history):
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
    if re.match(r"^(?:can|could)\s+i\s+(?:do|complete|combine)\b", question.strip(), re.I):
        return (
            "Decision: decide whether the student's exact proposed combination is a "
            "documented option for their department. A general minimum duration does not "
            "authorize adding unlike components together; require a source that explicitly "
            "allows that arrangement for the student's department. If it is not documented, "
            "say that directly, then explain the closest documented completion option "
            "and its approval conditions. Distinguish an activity that counts as part of "
            "a requirement from one that satisfies the whole requirement on its own. "
            "Do not assume the student excludes additional components unless they say so. "
            "A restriction on a different breakdown is not a reason to reject their plan. "
            "When an exception depends on approval or a missing detail, give the conditional "
            "outcomes instead of an unconditional Yes or No. Keep required approvals attached "
            "to each option you mention. Mention only completion options that directly address "
            "the proposed activity; omit unrelated arrangements and restrictions. "
            "Do not add forms, reports, deadlines, or "
            "other procedures unless the student asks for them."
        )
    if frame_confirmation(question, history) != question:
        return (
            "Confirmation: check the student's proposed understanding against source evidence. "
            "Correct an earlier assistant mistake if necessary; history is not authority. "
            "If the proposed arrangement is valid, say Yes even if other arrangements "
            "also exist; do not reject it just because it is not the only option. "
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
            "Give Yes or No only when the stated facts support an unconditional decision. "
            "If a missing approval or condition changes the result, explain the supported "
            "conditional outcomes and what must be confirmed. Before deciding, silently list "
            "every circumstance the student states, including an extra circumstance introduced by words such as "
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
        (re.search(r"\b(enough|eligible|qualify|sufficient)\b", question, re.IGNORECASE)
         or re.match(r"^(?:can|could)\s+i\s+(?:do|complete|combine)\b", question, re.I))
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


def _explicit_subject(text: str) -> bool:
    """Recognize a named subject without maintaining a list of CDC programs."""
    if re.match(r"^back to (?:the|my)\s+[\w+-]+\b", text, re.I):
        return True
    if re.search(r"\b[A-Z]{2,}\d*\b|[A-Z][a-z]+\+", text):
        return True
    what_about = _WHAT_ABOUT_RE.match(text)
    if what_about:
        subject = text[what_about.end():].strip(" ?.!")
        if _REFERENCE_RE.search(subject):
            return False
        words = subject.lower().split()
        if not words:
            return False
        if words[0] in {"a", "an", "the"}:
            words = words[1:]
            return len(words) > 1 and words[0] not in _GENERIC_REFERENTS
        return len(words) <= 3 and words[0] not in _GENERIC_REFERENTS
    named_definition = re.fullmatch(
        r"what (?:is|are) (?:a |an |the )?([\w+-]+(?:\s+[\w+-]+){0,2})\??",
        text, re.IGNORECASE,
    )
    if named_definition:
        words = named_definition.group(1).lower().split()
        return words[0] not in _GENERIC_REFERENTS
    if _RELATIVE_THAT_RE.search(text) and len(text.split()) >= 8:
        return True
    if (
        len(text.split()) >= 12 and len(_current_terms(text)) >= 6
        and not _CONTINUATION_RE.match(text)
        and not re.search(r"\b(it|its|they|them|their|those|these|one|ones)\b", text, re.I)
    ):
        # A detailed question can contain a demonstrative or conjunction without
        # depending on the previous turn ("that letter ... company ... internship").
        return True
    return False


def _anchor_index(prior: list[ConversationMessage]) -> int:
    """Find the latest substantive student subject, skipping elliptical turns."""
    user_indices = [index for index, message in enumerate(prior) if message.role == "user"]
    for index in reversed(user_indices):
        text = prior[index].content.strip()
        if _explicit_subject(text):
            return index
        if _REFERENCE_RE.search(text) or _CONTINUATION_RE.match(text):
            continue
        if len(text.split()) > 6 or not _QUESTION_START_RE.match(text):
            return index
    return user_indices[-1]


def _subject_hint(anchor: str) -> str:
    """Extract a short subject phrase from the latest substantive user turn."""
    text = " ".join(anchor.split()).strip(" ?.!")
    switch_back = re.match(r"back to (?:the|my)\s+([\w+-]+)\b", text, re.I)
    if switch_back:
        return switch_back.group(1)
    noun_phrase = re.search(
        r"\b(?:a|an|the|my)\s+((?:[A-Z]{2,}\s+)?[\w+-]+\s+"
        r"(?:letter|form|report|program|course))\b", text, re.IGNORECASE,
    )
    if noun_phrase:
        return noun_phrase.group(1)
    document = re.search(r"\b(?:a|an|the|my)\s+(letter|form|report)\b", text, re.I)
    if document:
        # A named artifact is the referent, rather than its provider's acronym.
        return document.group(1)
    named = re.search(r"\b(?:about|for)\s+(?:the\s+)?([A-Z][\w+-]+)\b", text)
    if named:
        return named.group(1)
    offered = re.search(
        r"\bdoes\s+(?:the|a|an)\s+([\w+-]+(?:\s+[\w+-]+){0,2}?)\s+"
        r"(?:offer|provide|require|include|mean|work)\b", text, re.IGNORECASE,
    )
    if offered:
        return offered.group(1)
    definition = re.fullmatch(
        r"what (?:is|are) (?:a |an |the )?([\w+-]+(?:\s+[\w+-]+){0,2})",
        text, re.IGNORECASE,
    )
    if definition:
        return definition.group(1)
    acronym: list[str] = re.findall(r"\b[A-Z]{2,}(?:-[A-Z]{2,})?\d*\b|[A-Z][a-z]+\+", text)
    if acronym:
        return acronym[-1]
    after_about = re.search(r"\babout\s+(?:the\s+)?([\w+-]+(?:\s+[\w+-]+)?)", text, re.I)
    if after_about:
        return after_about.group(1)
    named_activity = re.search(r"\b(?:of|during|in)\s+(?:the\s+)?([\w+-]+)\b", text, re.I)
    if named_activity and named_activity.group(1).lower() not in _QUERY_FILLER:
        return named_activity.group(1)
    words = [word for word in re.findall(r"[\w+-]+", text) if word.lower() not in _QUERY_FILLER]
    return " ".join(words[-3:]) if words else text[:60]


def _resolved_query(question: str, subject: str) -> str:
    """Replace a reference with its subject; never paste whole chat turns."""
    text = " ".join(question.strip().split())
    if re.search(r"\b(it|its|that|this|one|they|them|those|these)\b", text, re.I):
        return re.sub(
            r"\b(it|its|that|this|one|they|them|those|these)\b",
            subject, text, count=1, flags=re.IGNORECASE,
        )
    return f"{text.rstrip('?')} for {subject}?"


def _current_terms(question: str) -> set[str]:
    return {
        token.lower() for token in re.findall(r"[A-Za-z0-9+-]+", question)
        if token.lower() not in _QUERY_FILLER and len(token) > 1
    }


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
    last_user_question = next(m.content for m in reversed(prior) if m.role == "user")
    if text.casefold() == " ".join(last_user_question.strip().split()).casefold():
        return False
    if re.match(r"^back to (?:the|my)\s+[\w+-]+\b", text, re.I):
        return False
    named_current = re.match(
        r"^(?:and\s+)?(?:do|does|is|are|can|could|should|will|has|have)\s+"
        r"(?:the|my)\s+([\w+-]+)\b", text, re.I,
    )
    if (named_current and named_current.group(1).lower() not in _GENERIC_REFERENTS
            and not re.search(r"\b(it|its|they|them|those|these)\b", text, re.I)):
        return False
    if re.fullmatch(r"how long should .+ be\??", text, re.I):
        return True
    if _explicit_subject(text):
        return False
    what_about = _WHAT_ABOUT_RE.match(text)
    if what_about:
        subject = text[what_about.end() :]
        if _REFERENCE_RE.search(subject):
            return True
        return True
    if _REFERENCE_RE.search(text) or _CONTINUATION_RE.search(text):
        return True
    if re.search(r"\b[A-Z]{2,}\d*\b", text):
        return False
    return len(text.split()) <= 6 and bool(_QUESTION_START_RE.search(text))


def retrieval_plan(
    question: str, history: Sequence[ConversationMessage] | None
) -> RetrievalPlan:
    """Resolve the current turn and identify when both retrieval paths are useful."""
    prior = bounded_history(history)
    if not is_contextual_followup(question, prior):
        if re.fullmatch(
            r"how long should (?:the )?[a-z]{3,}\s?\d{3} be\??",
            question.strip(), re.I,
        ):
            return RetrievalPlan(f"Course duration and training length: {question}")
        return RetrievalPlan(question)
    subject = _subject_hint(prior[_anchor_index(prior)].content)
    resolved = _resolved_query(question, subject)
    # Keep the literal search for substantive restatements even when the short-
    # question cue misclassifies them. Brief, low-information follow-ups still
    # rely on their resolved subject.
    terms = _current_terms(question)
    continuation = bool(
        _REFERENCE_RE.search(question) or _CONTINUATION_RE.match(question)
        or _WHAT_ABOUT_RE.match(question)
    )
    uncertain = len(terms) >= 3 or (len(terms) >= 2 and continuation)
    return RetrievalPlan(resolved, question if uncertain and resolved != question else None)


def build_retrieval_query(
    question: str, history: Sequence[ConversationMessage] | None
) -> str:
    """Return a short standalone retrieval query for the current turn."""
    return retrieval_plan(question, history).query


def format_prompt_history(
    question: str, history: Sequence[ConversationMessage] | None
) -> str:
    """Format bounded history only when the current question depends on it."""
    prior = bounded_history(history)
    if not is_contextual_followup(question, prior):
        return ""
    prior = prior[_anchor_index(prior):]
    if len(question.split()) >= 10 and not _CONTINUATION_RE.match(question):
        # A detailed current question is usually self-contained. Search both paths,
        # but do not let a previous answer redefine what the student now describes.
        return ""
    if len(question.split()) >= 8 and not _REFERENCE_RE.search(question):
        # A complete restatement supplies its own facts. Earlier assistant guesses
        # can bias a confirmation even though they are not source evidence.
        prior = [message for message in prior if message.role == "user"]
    lines = [f"{m.role.upper()}: {m.content}" for m in prior]
    return "\n".join(lines)
