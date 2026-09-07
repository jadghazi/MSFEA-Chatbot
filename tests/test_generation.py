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
