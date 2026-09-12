"""Tests for the generation guardrails (refusal, citations, disclaimer).

These exercise the pure logic (prompt building + response parsing) without the
DB or a live LLM.
"""

import pytest

from msfea_bot.config import Settings, settings
from msfea_bot.generation.answer import (
    DISCLAIMER,
    REFUSAL_MARKER,
    Answer,
    build_prompt,
    escalation,
    generate_answer,
    parse_answer,
    _answer_context,
)
from msfea_bot.generation.conversation import ConversationMessage
from msfea_bot.llm import GenerationResult
from msfea_bot.retrieval.store import RetrievedChunk

CHUNKS = [
    RetrievedChunk(
        id="doc.md#01-x",
        text="The minimum internship duration is 8 weeks.",
        source_doc="doc.md",
        section="Duration",
        score=0.9,
    )
]


def test_excessive_rag_context_never_calls_provider(monkeypatch):
    import msfea_bot.generation.answer as generation
    huge = RetrievedChunk(id="huge", text="x" * 24_001,
                          source_doc="doc", section="section", score=0.9)
    monkeypatch.setattr(generation, "search", lambda *a, **kw: [huge])
    monkeypatch.setattr(generation, "get_llm_provider", lambda: pytest.fail("LLM called"))
    result = generate_answer("Requirements?")
    assert result.error_code == "context_too_large"
    assert "one part" in result.text

# Multi-section context, for the source-line parsing tests. Citations are validated
# against what was supplied, so a test that cites [doc.md > FAQs] has to supply it —
# a model citing a section it was never given is the case validation now rejects.
MULTI_CHUNKS = [
    RetrievedChunk(
        id="doc.md#02-faq",
        text="Q: What GPA do I need? A: 3.3.",
        source_doc="doc.md",
        section="FAQs",
        score=0.9,
    ),
    RetrievedChunk(
        id="doc.md#03-elig",
        text="Students need a minimum GPA of 3.3 to be eligible.",
        source_doc="doc.md",
        section="Eligibility",
        score=0.85,
    ),
    RetrievedChunk(
        id="doc.md#04-a",
        text="Section A content.",
        source_doc="doc.md",
        section="A",
        score=0.8,
    ),
    RetrievedChunk(
        id="doc.md#05-b",
        text="Section B content.",
        source_doc="doc.md",
        section="B",
        score=0.75,
    ),
]


def test_build_prompt_contains_question_context_and_marker() -> None:
    prompt = build_prompt("How long?", CHUNKS)
    assert "How long?" in prompt
    assert "8 weeks" in prompt
    assert REFUSAL_MARKER in prompt


def test_build_prompt_includes_history_only_for_a_followup() -> None:
    history = [ConversationMessage("user", "Do you provide a support letter?")]
    followup = build_prompt("Where do I get it?", CHUNKS, history=history)
    topic_switch = build_prompt("What GPA do I need for CO-OP?", CHUNKS, history=history)
    assert "Conversation history:" in followup
    assert "support letter" in followup
    assert "Conversation history:" not in topic_switch


def test_department_context_does_not_force_a_repetitive_answer_prefix() -> None:
    prompt = build_prompt("Can I do six weeks?", CHUNKS, department="ece")
    assert 'Address the student naturally as "you"' in prompt
    assert 'Do not open with "For ECE students"' in prompt


def test_option_followup_context_omits_unasked_procedure_sections() -> None:
    meaning = RetrievedChunk("meaning", "Six plus two meaning", "doc", "Options", 0.9)
    report = RetrievedChunk("report", "Submit a report", "doc", "Report requirements", 0.8)
    history = [ConversationMessage("user", "Are six weeks enough?")]
    assert _answer_context("what about the other option", [meaning, report], history) == [meaning]
    assert _answer_context("what report is required?", [meaning, report], history) == [meaning, report]


def test_ordinary_sufficiency_context_omits_unstated_conditional_section() -> None:
    general = RetrievedChunk(
        id="general", text="GENERAL", source_doc="rules.md",
        section="Duration options", score=0.9,
    )
    conditional = RetrievedChunk(
        id="conditional", text="CONDITIONAL", source_doc="rules.md",
        section="Taking another course", score=0.8,
    )
    assert _answer_context("Is six weeks enough?", [general, conditional], []) == [general]
    assert _answer_context(
        "Is six weeks enough while taking another course?", [general, conditional], []
    ) == [general, conditional]


def test_parse_refusal_marker_escalates() -> None:
    ans = parse_answer(f"  {REFUSAL_MARKER}  ", CHUNKS)
    assert ans.refused is True
    assert ans.citations == []
    assert DISCLAIMER in ans.disclaimer


def test_parse_answer_with_sources_line() -> None:
    raw = "It is 8 weeks.\nSOURCES: [doc.md > Duration]"
    ans = parse_answer(raw, CHUNKS)
    assert ans.refused is False
    assert ans.text == "It is 8 weeks."
    assert "doc.md > Duration" in ans.citations


def test_parse_answer_splits_multiple_bracketed_sources() -> None:
    # Gemini emits multiple sources as adjacent brackets: "[a] [b]" (no comma).
    raw = "A minimum GPA of 3.3.\nSOURCES: [doc.md > FAQs] [doc.md > Eligibility]"
    ans = parse_answer(raw, MULTI_CHUNKS)
    assert ans.citations == ["doc.md > FAQs", "doc.md > Eligibility"]


def test_parse_answer_splits_comma_separated_sources() -> None:
    raw = "Answer.\nSOURCES: [doc.md > A], [doc.md > B]"
    ans = parse_answer(raw, MULTI_CHUNKS)
    assert ans.citations == ["doc.md > A", "doc.md > B"]


def test_parse_answer_accepts_sources_on_following_lines() -> None:
    raw = "A minimum GPA of 3.3.\n\nSOURCES:\n[doc.md > FAQs]\n[doc.md > Eligibility]"
    ans = parse_answer(raw, MULTI_CHUNKS)
    assert ans.text == "A minimum GPA of 3.3."
    assert ans.citations == ["doc.md > FAQs", "doc.md > Eligibility"]


def test_parse_answer_without_sources_falls_back_to_context() -> None:
    ans = parse_answer("It is 8 weeks.", CHUNKS)
    assert ans.refused is False
    assert ans.citations == ["doc.md > Duration"]


def test_missing_sources_selects_best_supporting_block_not_every_candidate() -> None:
    raw = "Students need a minimum GPA of 3.3 to be eligible."
    ans = parse_answer(raw, MULTI_CHUNKS)
    assert ans.citations == ["doc.md > Eligibility"]


def test_invented_citation_is_dropped() -> None:
    """A label that was never in the prompt must not reach the student.

    Citation-presence is measured by the eval, validity was not — so a fabricated
    source used to pass every check while looking authoritative.
    """
    raw = "It is 8 weeks.\nSOURCES: [doc.md > Duration] [handbook.md > Eligibility]"
    ans = parse_answer(raw, CHUNKS)
    assert ans.citations == ["doc.md > Duration"]


def test_all_citations_invented_falls_back_to_supplied_context() -> None:
    raw = "It is 8 weeks.\nSOURCES: [made-up.md > Nowhere]"
    ans = parse_answer(raw, CHUNKS)
    assert ans.citations == ["doc.md > Duration"], "must fall back to real context"


def test_citation_matching_tolerates_reformatting() -> None:
    """Extra spacing or different case is the model reformatting, not inventing."""
    raw = "It is 8 weeks.\nSOURCES: [doc.md  >  duration]"
    ans = parse_answer(raw, CHUNKS)
    assert ans.citations == ["doc.md > Duration"], "resolves to the supplied spelling"


def test_prompt_requires_only_directly_supporting_citations() -> None:
    prompt = build_prompt("How long?", CHUNKS)
    assert "Cite only blocks that directly support the answer" in prompt
    assert "do not cite a conflicting general rule" in prompt


def test_prompt_requires_intent_aware_answer_planning() -> None:
    prompt = build_prompt("So the two weeks are research?", CHUNKS)
    assert "Resolve what the CURRENT question asks" in prompt
    assert "Identify its intent" in prompt
    assert "smallest set of blocks" in prompt
    assert "does not mean it belongs in the answer" in prompt


def test_prompt_keeps_confirmations_focused() -> None:
    prompt = build_prompt("So the two weeks are research?", CHUNKS)
    assert "For a confirmation or correction" in prompt
    assert "Do not volunteer" in prompt
    assert "Answer the current turn" in prompt


def test_prompt_allows_grounded_rule_application() -> None:
    prompt = build_prompt("I completed 88 credits. Can I register?", CHUNKS)
    assert "apply an explicit rule" in prompt
    assert "basic logic or arithmetic" in prompt
    assert "facts the student explicitly provides" in prompt


def test_proposed_combination_requires_department_specific_authorization() -> None:
    prompt = build_prompt(
        "Can I do six weeks internship and two weeks research?", CHUNKS, "mech"
    )
    assert "documented option for their department" in prompt
    assert "general minimum duration does not authorize" in prompt
    assert "different breakdown or set of components" in prompt
    assert "Do not add forms" in prompt


def test_prompt_requests_minimum_sufficient_sources() -> None:
    prompt = build_prompt("How long?", MULTI_CHUNKS)
    assert "Usually one source is enough" in prompt
    assert "two only when the answer genuinely combines facts from both" in prompt


def test_repeated_labels_are_deduped() -> None:
    """Several retrieved windows share one section label; cite it once."""
    chunks = [
        CHUNKS[0],
        RetrievedChunk(
            id="doc.md#02-x",
            text="Departments may allow 6 weeks.",
            source_doc="doc.md",
            section="Duration",
            score=0.8,
        ),
    ]
    assert parse_answer("It is 8 weeks.", chunks).citations == ["doc.md > Duration"]
    raw = "It is 8 weeks.\nSOURCES: [doc.md > Duration], [doc.md > Duration]"
    assert parse_answer(raw, chunks).citations == ["doc.md > Duration"]


def test_escalation_mentions_a_contact() -> None:
    ans = escalation()
    assert ans.refused is True
    assert ans.text
    assert isinstance(ans, Answer)


class _NeverCalledProvider:
    def generate(self, prompt: str) -> GenerationResult:
        raise AssertionError("a below-threshold question must not call the LLM")


class _RecordingProvider:
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, prompt: str) -> GenerationResult:
        self.calls += 1
        return GenerationResult("It is 8 weeks.\nSOURCES: [doc.md > Duration]")


def test_similarity_threshold_default_is_calibrated() -> None:
    assert Settings.model_fields["similarity_threshold"].default == 0.60


def test_below_similarity_threshold_skips_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    low = RetrievedChunk(**{**CHUNKS[0].__dict__, "score": 0.599})
    monkeypatch.setattr("msfea_bot.generation.answer.search", lambda *args, **kwargs: [low])
    monkeypatch.setattr(settings, "similarity_threshold", 0.60)

    result = generate_answer("What is the weather?", provider=_NeverCalledProvider())

    assert result.refused is True


def test_similarity_threshold_boundary_calls_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    boundary = RetrievedChunk(**{**CHUNKS[0].__dict__, "score": 0.60})
    monkeypatch.setattr(
        "msfea_bot.generation.answer.search", lambda *args, **kwargs: [boundary]
    )
    monkeypatch.setattr(settings, "similarity_threshold", 0.60)
    provider = _RecordingProvider()

    result = generate_answer("How long is the internship?", provider=provider)

    assert result.refused is False
    assert provider.calls == 1


def test_hybrid_first_hit_cannot_hide_stronger_retrieved_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    low = RetrievedChunk(**{**CHUNKS[0].__dict__, "score": 0.59})
    strong = RetrievedChunk(**{**CHUNKS[0].__dict__, "id": "doc.md#02", "score": 0.64})
    monkeypatch.setattr("msfea_bot.generation.answer.search", lambda *args, **kwargs: [low, strong])
    monkeypatch.setattr(settings, "similarity_threshold", 0.60)
    provider = _RecordingProvider()
    assert not generate_answer("Explain the arrangement", provider=provider).refused
    assert provider.calls == 1


def test_prompt_frames_confirmation_but_keeps_why_question_intact() -> None:
    history = [ConversationMessage("user", "Explain the arrangement")]
    confirm = build_prompt("so two weeks of research", CHUNKS, history=history)
    assert "Is my understanding of our conversation correct: two weeks of research?" in confirm
    assert confirm.endswith("Do not add forms, reports, procedures, or alternative arrangements.")
    why = build_prompt("Why two weeks rather than one?", CHUNKS, history=history)
    assert why.endswith("Question: Why two weeks rather than one?\n")


def test_conditional_decision_places_best_candidate_nearest_question() -> None:
    first = RetrievedChunk(
        id="specific", text="SPECIFIC CONDITION", source_doc="specific.md",
        section="Condition", score=0.9,
    )
    second = RetrievedChunk(
        id="general", text="GENERAL RULE", source_doc="general.md",
        section="General", score=0.8,
    )
    focused = build_prompt("I am also taking a course. Is this enough?", [first, second])
    ordinary = build_prompt("Is this enough for the option?", [first, second])
    assert focused.index("GENERAL RULE") < focused.index("SPECIFIC CONDITION")
    assert ordinary.index("SPECIFIC CONDITION") < ordinary.index("GENERAL RULE")
