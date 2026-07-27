"""Tests for the generation guardrails (refusal, citations, disclaimer).

These exercise the pure logic (prompt building + response parsing) without the
DB or a live LLM.
"""

from msfea_bot.generation.answer import (
    DISCLAIMER,
    REFUSAL_MARKER,
    Answer,
    build_prompt,
    escalation,
    parse_answer,
)
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


def test_build_prompt_contains_question_context_and_marker() -> None:
    prompt = build_prompt("How long?", CHUNKS)
    assert "How long?" in prompt
    assert "8 weeks" in prompt
    assert REFUSAL_MARKER in prompt


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
    ans = parse_answer(raw, CHUNKS)
    assert ans.citations == ["doc.md > FAQs", "doc.md > Eligibility"]


def test_parse_answer_splits_comma_separated_sources() -> None:
    raw = "Answer.\nSOURCES: [doc.md > A], [doc.md > B]"
    ans = parse_answer(raw, CHUNKS)
    assert ans.citations == ["doc.md > A", "doc.md > B"]


def test_parse_answer_without_sources_falls_back_to_context() -> None:
    ans = parse_answer("It is 8 weeks.", CHUNKS)
    assert ans.refused is False
    assert ans.citations == ["doc.md > Duration"]


def test_escalation_mentions_a_contact() -> None:
    ans = escalation()
    assert ans.refused is True
    assert ans.text
    assert isinstance(ans, Answer)
