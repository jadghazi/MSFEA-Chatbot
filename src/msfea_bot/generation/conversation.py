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
_OPTIONS_RE = re.compile(
    r"\b(?:what (?:are )?(?:my|our|the|available) options|"
    r"what options (?:do (?:I|we) have|are available))\b", re.I,
)
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
    "fee", "fees", "cost", "price", "tuition", "duration", "length", "contact", "email",
    "applications", "approvals", "deadlines", "documents", "forms", "letters",
    "reports", "programs", "courses", "requirements", "steps", "submissions",
    "links", "contacts", "emails", "options",
})
_QUERY_FILLER = frozenset({
    "a", "about", "an", "and", "are", "at", "be", "can", "could", "do", "does",
    "for", "from", "get", "how", "i", "in", "is", "it", "me", "my", "of", "or",
    "should", "that", "the", "this", "to", "what", "when", "where", "which",
    "who", "why", "would", "you",
    "actually", "instead", "now", "anyway", "okay", "ok", "so", "then", "also",
    "but", "please", "basically", "mean", "means",
})
_RELATIVE_THAT_RE = re.compile(
    r"\b(?:a|an|the|my)\s+\w+(?:\s+\w+)?\s+that\s+"
    r"(?:starts?|ends?|begins?|is|was|has|had|offers?|requires?|allows?|provides?)\b",
    re.IGNORECASE,
)
_ORDINAL_REFERENCE_RE = re.compile(
    r"\b(?:the|its|that|this)\s+(?:first|second|third|next|last|other)\s+"
    r"(?:part|stage|step|term|semester|year|option)\b", re.I,
)
_ATTRIBUTE_GROUPS = (
    (r"\b(?:fees?|costs?|price|tuition|charges?|billing)\b",
     ("fee", "cost", "tuition", "charge", "billing")),
    (r"\b(?:duration|length|how long|how much time|shorter|(?<!no )longer)\b",
     ("duration", "length")),
    (r"\b(?:contact|email|advisor|coordinator)\b",
     ("contact", "email", "advisor", "coordinator")),
    (r"\b(?:links?|urls?|websites?|webpages?)\b", ("link", "url", "website")),
)
_BOUND_REFERENCE_RE = re.compile(
    r"^(?:so\s+)?(?:is|was)\s+(?:that|this|it)\s+(?:a |the )?"
    r"(?:minimum|maximum|lower limit|upper limit)(?:\s+or\s+(?:a |the )?"
    r"(?:minimum|maximum|lower limit|upper limit))?\??$", re.I,
)
_RELATIONSHIP_REFERENCE_RE = re.compile(
    r"\b(?:that|this|those|these)\s+(?:course|program|document|report|form|letter|"
    r"application|requirement|activity|step|workshop|assessment)s?\b|"
    r"\b(?:enrolling|joining|registering|applying|participating|working|training)\s+there\b",
    re.I,
)
_DECISION_SCOPE_RULE = (
    "Distinguish 'not automatically approved' from an explicit prohibition or "
    "a documented shortfall. Where the evidence only requires approval, or the exact "
    "variant is "
    "not documented, explain that limit rather than declaring the proposal invalid. "
    "Match numerical triggers, including their ranges or bounds, and other conditions "
    "before applying a restriction; "
    "a rule for one breakdown does not settle a different breakdown. Apply an "
    "explicit prohibition when its conditions match. Arithmetic "
    "can establish a total, but cannot establish formal acceptance. "
    "Honor explicitly assumed approvals for a hypothetical calculation; this is not "
    "verification of personal records or creation of a new policy exception. For an "
    "official eligibility claim, still apply matching documented restrictions. "
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
            # Retrieval can lexicalize an attribute, but generation must retain
            # the student's actual decision/comparison rather than its search terms.
            prior = bounded_history(history)
            subject = _subject_hint(prior[_anchor_index(prior)].content)
            dimension = _bound_dimension(question, prior)
            return _resolved_query(question, f"{subject} {dimension}" if dimension else subject)
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
    if (re.search(r"\b(?:get(?:ting)? ready|prepar(?:e|ing|ation))\s+for\b", question, re.I)
            and not re.match(r"^(?:can|could|may|must|should)\s+I\b", question.strip(), re.I)):
        return (
            "Preparation: explain practical first actions for the activity the student "
            "wants to prepare for. Include relevant documented preparation resources, "
            "application materials and prerequisites, rather than replacing them with "
            "a description of the whole program or its eventual completion checklist. "
            "Include supplied resource URLs when useful; do not invent unavailable links. "
            "Keep each preparation requirement attached to the correct activity."
        )
    if _OPTIONS_RE.search(question):
        return (
            "Available options: summarize the documented paths that address the student's "
            "actual goal. Do not substitute one narrow FAQ for the range of options or "
            "list unrelated services. Keep each option's scope, eligibility and approval "
            "conditions attached. Include ordinary paths as well as relevant documented "
            "alternatives, without implying that an option guarantees acceptance."
            " Preserve the complete components of each path, including a shared "
            "starting component; alternative additions are not one combined path."
        )
    if is_overview_request(question, history):
        return (
            "Topic overview: orient the student to the subject they named. Combine "
            "supported purpose, normal requirements and main steps into a useful summary. "
            "Do not substitute a narrow FAQ, exceptional arrangement or exhaustive "
            "deliverables checklist. This is an orientation request, so the complete-list "
            "instruction does not require enumerating individual forms. Group the normal "
            "path into major stages and summarize required deliverables collectively. "
            "Omit individual deadlines and exceptional arrangements unless the student "
            "asks about them. When the student has already identified the subject, "
            "do not append instructions to select a different program. "
            "Mention only facts supported by the evidence, "
            "never combine components from separate alternative paths, "
            "state any material gap and offer a useful next direction."
        )
    if re.search(r"\b(?:do|use|try|repeat) (?:the same|it|this|that)(?: again)?\??$",
                 question.strip(), re.I):
        return (
            "Referential decision: identify the activity or arrangement from the CURRENT "
            "student message and its relevant history. If those do not identify what "
            "the student proposes, ask which activity or arrangement they mean. Address "
            "that clarifying question directly to the student; do not repeat an editorial "
            "instruction to ask them. Related "
            "retrieved topics cannot resolve an unnamed proposal. You may explain a "
            "directly relevant general rule, but include the clarifying question and "
            "do not assume a particular plan. If the referent is identified, apply its "
            "documented conditions normally without asking an unnecessary clarification."
        )
    if re.search(r"\b(?:skip|skipping|replace|replaces|replacement|substitute|"
                 r"substitution|waive|waiver|instead of)\b", question, re.I):
        return (
            "Decision: substitution or waiver. Identify the exact activities or obligations "
            "the student is comparing. If the evidence explicitly requires separate "
            "items, completing one does not by itself satisfy the other; explain that "
            "supported relationship rather than requiring a verbatim answer to this "
            "question. Apply a documented substitution or optionality rule when present, "
            "with its actual conditions. Do not infer that an item is required merely "
            "because the source mentions it, or invent a waiver from silence. Keep "
            "this conclusion separate from verification of the student's personal "
            "completion or approval. Ask for clarification only if the current "
            "question and its student anchor leave the compared items unidentified. "
            "Do not add forms, deadlines or unstated exception scenarios unless they "
            "are requested or directly determine this substitution."
        )
    if (re.match(r"^(?:what|which)\b", question.strip(), re.I)
            and re.search(r"\b(?:requirements?|deliverables?|required|must|have to|"
                          r"need to)\b", question, re.I)):
        return (
            "Required items: identify the ordinary applicable obligations for the "
            "named subject and student's scope. Start with those items, not a special "
            "arrangement found in the highest-ranked passage. Preserve applicable "
            "scoped exceptions and distinguish required from optional items. Discuss "
            "a conditional route only if the student states its triggering "
            "circumstances or asks for alternatives; do not make its extra items "
            "sound universal. Include requested details without reproducing "
            "unrelated procedures or assuming an unstated arrangement."
        )
    if (re.match(r"^(?:so\s+)?(?:do I (?:need|have to)|must I)\b", question.strip(), re.I)
            or re.match(r"^(?:so\s+)?(?:is|are)\b", question.strip(), re.I)
            and re.search(r"\b(?:mandatory|required)\b", question, re.I)):
        return (
            "Requirement status: first identify exactly what the student asks whether "
            "they must do. If a pronoun could name several earlier subjects, ask which "
            "one they mean. Otherwise a Yes or No needs evidence explicitly settling "
            "that requirement or prerequisite for that same subject. General guidance "
            "or the absence of a listed prerequisite does not establish that it is "
            "unnecessary. When that status is not documented, state precisely that you "
            "cannot confirm it, then offer directly relevant documented help if available. "
            "Do not turn adjacent advice into permission to bypass a requirement. "
            "Use INSUFFICIENT_CONTEXT when no useful supported help is available."
        )
    prior_questions = [message.content for message in bounded_history(history) if message.role == "user"]
    if (re.match(r"^(?:can|could|would|will)\s+you\b", question.strip(), re.I)
            and re.search(r"\b(?:confirm|verify|check|tell)\b", question, re.I)
            and re.search(r"\b(?:my|our|me|mine)\b", question, re.I)
            and re.search(r"\b(?:approved|accepted|registered|enrolled|grade|graded|passed)\b",
                          question, re.I)
            and not re.search(r"\b(?:how|requirements?|criteria)\b", question, re.I)):
        return (
            "Individual status verification: you cannot access or verify personal "
            "approval, application, enrollment or grading records. State that limit "
            "and offer the directly relevant documented human contact. Do not infer "
            "the requested status from a general policy, elapsed-time estimate or "
            "another student's outcome. Do not assume an application route or add "
            "procedural steps unless the current question asks for them."
        )
    requested_attribute = any(re.search(pattern, question, re.I)
                              for pattern, _ in (_ATTRIBUTE_GROUPS[0], *_ATTRIBUTE_GROUPS[2:]))
    if (re.fullmatch(r"when is (?:the )?deadline\??", question.strip(), re.I)
            and prior_questions and is_overview_request(prior_questions[-1])):
        return (
            "Clarification: the student has not identified a particular deadline after "
            "a topic overview. Ask which application, form or deliverable deadline they "
            "mean. Do not select one arbitrarily or refuse because the referent is missing."
        )
    if (_WHAT_ABOUT_RE.match(question.strip()) and is_contextual_followup(question, history)
            and not requested_attribute
            and (re.search(r"\d|\b(?:option|alternative)\b", question, re.I)
                 or prior_questions and re.search(
                     r"\b(?:can|could) I\b|\b(?:enough|sufficient|only|alone)\b",
                     prior_questions[-1], re.I))):
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
    if (re.match(r"^(?:how|where)\s+(?:(?:do|can|should)\s+(?:I|we)\b|to\b)",
                 question.strip(), re.I) and not requested_attribute):
        return (
            "Procedure: explain the applicable steps in order at the level of detail "
            "requested. Keep each action, actor, prerequisite and approval condition "
            "attached to its own step. If dates are needed, match each action to its "
            "exact table row and the student's track or stage; never borrow a date "
            "from another step or actor. Do not reproduce the full calendar unless "
            "requested. Give the supplied form or page URL when it helps carry out "
            "the requested action; do not refer vaguely to a website when its URL is "
            "available, or invent a URL when absent. Words limiting the requested "
            "explanation, such as 'only the "
            "main steps', do not propose skipping a requirement."
        )
    if (re.search(r"\b(?:only|alone)\b", question, re.I)
            and re.match(r"^(?:(?:can|could|may|should)\s+I\b|(?:is|are|would|will)\b)",
                         question.strip(), re.I)):
        return (
            "Plan sufficiency: decide whether the exact plan stated by the student is "
            "sufficient on its own. Start with Yes only if that plan alone completes the "
            "documented requirement; otherwise start with No, identify what is missing, "
            "and give the closest documented completion option. Do not reinterpret the "
            "question as asking whether the partial activity is allowed. Do not add forms, "
            "reports, deadlines, or a rule for an unstated circumstance."
        )
    if re.match(r"^(?:can|could)\s+i\s+(?:do|complete|combine)\b", question.strip(), re.I):
        quantified_plan = re.search(
            r"\b(?:combine|combined|combination|split|both|plus)\b|\d+\s*\+\s*\d+|"
            r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
            r"[\s-]+(?:full[\s-]+)?(?:weeks?|months?|days?|hours?|credits?|"
            r"parts?|components?|placements?)\b", question, re.I,
        )
        if not quantified_plan:
            return (
                "Activity permission: answer whether the exact activity, location or "
                "format the student proposes is supported, keeping its approval and "
                "eligibility conditions attached. Do not turn this into a question about "
                "an unstated duration or combining components. Do not add alternative "
                "arrangements, deliverables or reporting procedures unless requested "
                "or necessary to answer this specific permission question. If permission "
                "is not documented, identify that gap rather than inventing permission."
            )
        return (
            "Decision: " + _DECISION_SCOPE_RULE +
            "Decide whether the student's exact proposed combination is a "
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
            "Comparison: use the specific documented programs and their requirements, "
            "rather than a generic industry definition. Explicitly contrast every "
            "dimension the student asks about. For a broad comparison with no named "
            "dimensions, include the most consequential documented differences and "
            "relationships, including any stated requirement, optionality or substitution; "
            "do not stop after the first definition's two differences. "
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
    if (re.search(r"\b(enough|eligible|qualify|sufficient)\b", question, re.I)
            or re.match(r"^(?:can|could|may) I\b", question.strip(), re.I)
            or (re.match(r"^(?:can|could)\b", question.strip(), re.I)
                and re.search(r"\b(?:count|qualify|satisfy|make up|replace)\b", question, re.I))):
        return (
            "Decision: " + _DECISION_SCOPE_RULE +
            "Apply the rule for the circumstances the student actually states. "
            "Give Yes or No only when the stated facts support an unconditional decision. "
            "If a missing approval or condition changes the result, explain the supported "
            "conditional outcomes and what must be confirmed. Before deciding, silently list "
            "every circumstance the student states, including an extra circumstance introduced by words such as "
            "'also', 'while', 'when', or 'if'. Match all of them to the source conditions. "
            "A source block specifically about an extra stated circumstance controls over a "
            "general rule. If the question names an option or arrangement, describe only that "
            "option unless a matching extra circumstance explicitly changes the applicable "
            "rule. Do not combine a number or rule from a circumstance the student did not "
            "state, ignore a stated condition, or offer an incompatible general rule. "
            "Keep the answer focused on this permission or eligibility decision. Do not "
            "add forms, reporting procedures, timelines or unstated exception scenarios "
            "unless the current question asks for them or they determine the decision."
        )
    if (re.search(r"\badd(?:s)? up\b|\bsum of\b|\d+\s*\+\s*\d+", question, re.I)
            or re.search(r"\bplus\b", question, re.I)
            and re.search(r"\b(?:makes?|totals?|equals?|right)\b", question, re.I)):
        return (
            "Grounded calculation: answer the numerical relation the student actually "
            "asks about, using their stated facts or hypothetical premises. "
            "A pure arithmetic confirmation needs only the calculation: do not add "
            "policy minima, eligibility judgments or approval evaluations that the "
            "current question did not request. Apply a documented bound only if the "
            "student also asks whether the result meets a requirement or limit. "
            "Honor an explicitly assumed approval within the "
            "hypothetical without claiming to have verified personal records. Do not "
            "turn a sum into a new approval decision or apply a restriction whose "
            "triggering circumstances are absent. If official acceptance is also asked "
            "about, distinguish it from the calculation and apply its actual conditions."
        )
    if (re.search(r"\b(?:does|do|is|are|would|will)\b.+\b(?:mean|imply|automatically)\b",
                  question, re.I)
            and not re.match(r"^(?:what|how|why|where|when|who|which)\b", question.strip(), re.I)):
        return (
            "Policy relationship: answer whether the stated fact establishes the "
            "conclusion the student proposes. Give the supported relationship and "
            "its controlling conditions concisely. Do not assume an unstated route "
            "or add a procedure for one possible case. A confirmation does not "
            "request forms, petitions, deadlines or application instructions."
        )
    if requested_attribute:
        return (
            "Requested attribute: answer the specific cost, contact, link or other "
            "detail actually requested for the named or resolved subject, rather than "
            "returning its topic description. Do not borrow another subject's value. "
            "If that detail is missing, say exactly what cannot be confirmed. Then "
            "offer a verified contact or resource for that same topic if supplied; "
            "this is useful partial help, so do not discard it with the refusal marker. "
            "A suitable reply is: 'I cannot confirm [requested detail]. You can check "
            "[supplied topic resource] or contact [supplied topic contact].' Fill these "
            "only with evidence that is actually supplied; omit unavailable fields. "
            "For a sign-up or resource request, include the supplied URL when useful "
            "rather than referring vaguely to a webpage. "
            "If no relevant documented help is available, use the ordinary "
            "insufficient-context rule. Do not convert billing units to a monetary "
            "amount without a documented price."
        )
    if re.search(r"\b(?:how long|how much time|duration|shorter|(?<!no )longer|"
                 r"how many (?:hours|weeks|months|pages|words|slides))\b",
                 " ".join(question.split()), re.I):
        return (
            "Quantity or range: answer the requested quantity for the named or resolved "
            "subject. Distinguish a minimum from a maximum or an estimate, and use the "
            "correct units. Start with the ordinary applicable rule; do not introduce "
            "an exceptional arrangement, alternate route or additional circumstance "
            "the student has not proposed. If the student states a condition, apply its "
            "controlling scoped rule and preserve every approval condition. Answer a "
            "shorter/longer comparison against the applicable limit, not against a "
            "different document or activity. A short quantity answer is sufficient."
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


def is_overview_request(
    question: str, history: Sequence[ConversationMessage] | None = None,
) -> bool:
    """Recognize orientation wording without a domain-specific topic list."""
    text = " ".join(question.strip().split())
    if _OPTIONS_RE.search(text):
        return True
    if re.search(r"\bwhere (?:should|do) I (?:begin|start)\??$", text, re.I):
        return True
    if re.search(r"\b(?:tell me about|overview of|walk me through|never heard of|"
                 r"what should I know about|whole process|big picture|basics of|"
                 r"general introduction)\b", text, re.I):
        return True
    if (re.search(r"\bbefore (?:we |you |I )?(?:get|getting|go|going) into "
                  r"(?:the )?(?:details|special cases|exceptions)\b", text, re.I)
            and not re.search(r"\b(?:deadline|fee|duration|minimum|maximum|requirements|"
                              r"deliverables)\b", text, re.I)):
        return True
    if re.match(r"^(?:more specifically\s+)?(?:what|how) about\b", text, re.I):
        # A named new topic asks for orientation; an elliptical option still
        # needs the earlier plan and retains the existing decision cue.
        return not is_contextual_followup(text, history)
    return bool(re.match(r"^what (?:do I need to do|support is available)\b", text, re.I))


def unresolved_reference(
    question: str, history: Sequence[ConversationMessage] | None,
) -> bool:
    """A wholly elliptical question with no earlier student subject has no evidence query."""
    prior = bounded_history(history)
    prior_users = [message.content for message in prior if message.role == "user"]
    if prior_users:
        # Singular status questions cannot identify one item in a service menu.
        # Assistant wording helps resolve references, never establishes policy.
        service_menu = re.search(
            r"\bwhat (?:support|services)\b|\bwhat (?:does .+ offer|can .+ help me with)\b",
            prior_users[-1], re.I,
        )
        recent_answer = next((message.content for message in reversed(prior)
                              if message.role == "assistant"), "")
        singular_reference = re.fullmatch(
            r"(?:is (?:this|that|it) (?:required|mandatory|compulsory)|"
            r"do I (?:have to do|need) (?:this|that|it)|"
            r"how (?:do|can) I (?:sign up|register|apply|enroll|enrol) "
            r"(?:for|in) (?:this|that|it))\??", question.strip(), re.I,
        )
        return bool(service_menu and singular_reference
                    and (recent_answer.count(",") >= 2 or recent_answer.count("\n- ") >= 2))
    return bool(re.fullmatch(
        r"(?:how (?:does|do) (?:this|that|it|they) work|"
        r"what (?:about|is) (?:this|that|it)|is (?:this|that|it) (?:required|mandatory))\??",
        question.strip(), re.I,
    ))


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
    # Discourse markers do not make a named question a continuation. Recognize
    # complete questions about a new object without a list of university topics.
    core = re.sub(r"^(?:actually|instead|now|anyway)[,:]?\s+", "", text, flags=re.I)
    named = re.search(
        r"\b(?:explain|about|(?:help|support)(?: (?:is|are) (?:there|available))? for)\s+"
        r"(?:a |an |the )?([\w+-]+)", core, re.I,
    )
    if (named and re.fullmatch(r"[A-Za-z][\w+-]*", named.group(1))
            and named.group(1).lower() not in _GENERIC_REFERENTS
            and not _REFERENCE_RE.fullmatch(named.group(1))):
        return True
    named_how = re.match(r"how (?:does|do)\s+(?:the )?([\w+-]+)\b", core, re.I)
    if (named_how and named_how.group(1).lower() not in _GENERIC_REFERENTS
            and not _REFERENCE_RE.fullmatch(named_how.group(1))
            and named_how.group(1).lower() not in {"i", "we", "you"}):
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


def _strip_topic_framing(question: str) -> str:
    """Remove an abandoned-topic preface only before a self-contained question.

    The original is still used for generation. This prevents negated old-topic
    keywords from dominating retrieval, without erasing a referential follow-up.
    """
    text = " ".join(question.split())
    match = re.match(
        r"^(?:(?:forget|leave|set aside|put aside)\b.+?(?:for (?:a moment|now)|aside)"
        r"[.!;,:]\s*|(?:switching|changing)\s+(?:topics?|subjects?)[.!;,:]\s*)(.+)$",
        text, re.I,
    )
    if (match and _QUESTION_START_RE.match(match.group(1))
            and not re.search(r"\b(?:it|its|that|this|they|them|those|these)\b", match.group(1), re.I)):
        return match.group(1)
    return question


def _subject_hint(anchor: str) -> str:
    """Extract a short subject phrase from the latest substantive user turn."""
    text = " ".join(_strip_topic_framing(anchor).split()).strip(" ?.!")
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
    actor = re.search(
        r"\b(?:does|can|could|will|would)\s+(?:the|a|an)\s+"
        r"([\w+-]+(?:\s+[\w+-]+){0,3}?)\s+"
        r"(?:help|offer|provide|require|include|mean|work)\b", text, re.I,
    )
    if actor:
        return actor.group(1)
    named = re.search(
        r"\b(?:about|for)\s+(?:(?:the|a|an)\s+)?"
        r"([A-Za-z][\w+-]+(?:\s+\d{2,}[A-Za-z]?)?)\b", text,
    )
    if named:
        return named.group(1)
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
    text = " ".join(_strip_topic_framing(question).strip().split())
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


def attribute_search(
    question: str, history: Sequence[ConversationMessage] | None,
) -> tuple[str, tuple[str, ...]] | None:
    """Pair a short attribute follow-up with its substantive conversation subject.

    This small English attribute vocabulary describes intent, not supported
    university topics or facts. Several attribute turns keep the same anchor.
    """
    prior = bounded_history(history)
    if not prior or not is_contextual_followup(question, prior):
        return None
    question = " ".join(question.split())
    dimension = _bound_dimension(question, prior)
    if dimension:
        return _subject_hint(prior[_anchor_index(prior)].content), (dimension,)
    for pattern, terms in _ATTRIBUTE_GROUPS:
        if re.search(pattern, question, re.I):
            return _subject_hint(prior[_anchor_index(prior)].content), terms
    return None


def _bound_dimension(question: str, prior: list[ConversationMessage]) -> str:
    """Resolve a bound from the latest student attribute within the current topic.

    Use student wording, not a number or purported policy in an assistant answer.
    Do not carry attributes across a substantive subject switch.
    """
    if not prior or not _BOUND_REFERENCE_RE.fullmatch(question.strip()):
        return ""
    for message in reversed(prior[_anchor_index(prior):]):
        if message.role != "user":
            continue
        for pattern, terms in _ATTRIBUTE_GROUPS[:2]:
            if re.search(pattern, message.content, re.I):
                return "cost" if terms[0] == "fee" else "duration"
        if re.search(r"\bhow many (?:pages|words|slides)\b", message.content, re.I):
            return "length"
    return ""


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

    text = " ".join(_strip_topic_framing(question).strip().split())
    last_user_question = next(m.content for m in reversed(prior) if m.role == "user")
    if text.casefold() == " ".join(last_user_question.strip().split()).casefold():
        return False
    if re.match(r"^back to (?:the|my)\s+[\w+-]+\b", text, re.I):
        return False
    if (_QUESTION_START_RE.match(text) and _RELATIONSHIP_REFERENCE_RE.search(text)
            and re.search(r"\b(?:replace|instead of|skip|waive|mean|imply|"
                          r"automatically|earn)\b", text, re.I)):
        # A relationship can name one operand while referring to the other from
        # history. A named outcome does not make that antecedent self-contained.
        return True
    if _ORDINAL_REFERENCE_RE.search(text) and not _explicit_subject(text):
        return True
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
    generic_subject = re.search(
        r"\b(?:about|explain)\s+(?:the |my |those |these )?([\w+-]+)\b", text, re.I,
    )
    if generic_subject and generic_subject.group(1).lower() in _GENERIC_REFERENTS:
        return True
    what_about = _WHAT_ABOUT_RE.match(text)
    if what_about:
        subject = text[what_about.end() :]
        if _REFERENCE_RE.search(subject):
            return True
        return True
    if (_REFERENCE_RE.search(text) or _CONTINUATION_RE.search(text)
            or _ORDINAL_REFERENCE_RE.search(text)):
        return True
    if re.search(r"\b[A-Z]{2,}\d*\b", text):
        return False
    return len(text.split()) <= 6 and bool(_QUESTION_START_RE.search(text))


def retrieval_plan(
    question: str, history: Sequence[ConversationMessage] | None
) -> RetrievalPlan:
    """Resolve the current turn and identify when both retrieval paths are useful."""
    question = _strip_topic_framing(question)
    prior = bounded_history(history)
    if re.fullmatch(r"what (?:can you (?:help me with|do)|do you (?:do|offer))\??",
                    question.strip(), re.I):
        # Capability questions need the source-backed service overview, not an
        # arbitrary policy that happens to contain "help". No topic list is encoded.
        return RetrievalPlan("What services and career support does the CDC offer?")
    if not is_contextual_followup(question, prior):
        if re.fullmatch(
            r"how long should (?:the )?[a-z]{3,}\s?\d{3} be\??",
            question.strip(), re.I,
        ):
            return RetrievalPlan(f"Course duration and training length: {question}")
        return RetrievalPlan(question)
    subject = _subject_hint(prior[_anchor_index(prior)].content)
    dimension = _bound_dimension(question, prior)
    if dimension:
        subject = f"{subject} {dimension}"
    resolved = _resolved_query(question, subject)
    if re.search(r"\b(?:shorter|(?<!no )longer)\b", " ".join(question.split()), re.I):
        # Comparative attributes need their implied dimension, not policy facts.
        # "Can it be shorter?" asks about duration of the resolved subject.
        resolved = f"How long is {subject}?"
    # Keep the literal search for substantive restatements even when the short-
    # question cue misclassifies them. Brief, low-information follow-ups still
    # rely on their resolved subject.
    terms = _current_terms(question)
    continuation = bool(
        _REFERENCE_RE.search(question) or _CONTINUATION_RE.match(question)
        or _WHAT_ABOUT_RE.match(question)
    )
    uncertain = len(terms) >= 3 or (len(terms) >= 2 and continuation)
    attribute = attribute_search(question, prior)
    if attribute and (dimension or len(question.split()) <= 10) and not (
        _EXPLICIT_CONDITION_RE.search(question) or re.search(r"\d", question)
    ):
        # A short referential attribute has no independent search subject. Its
        # literal embedding otherwise favors unrelated forms, fees or limits.
        # Substantive conditions retain the dual path.
        uncertain = False
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
        # Detailed questions can still contain a genuine pronoun reference. Keep
        # the current student anchor so the model can verify its referent, while
        # excluding previous assistant claims from these longer restatements.
        if not _REFERENCE_RE.search(question):
            return ""
        prior = [message for message in prior if message.role == "user"]
    if len(question.split()) >= 8 and not _REFERENCE_RE.search(question):
        # A complete restatement supplies its own facts. Earlier assistant guesses
        # can bias a confirmation even though they are not source evidence.
        prior = [message for message in prior if message.role == "user"]
    lines = [f"{m.role.upper()}: {m.content}" for m in prior]
    return "\n".join(lines)
