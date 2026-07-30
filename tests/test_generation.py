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


def test_parse_answer_without_sources_falls_back_to_context() -> None:
    ans = parse_answer("It is 8 weeks.", CHUNKS)
    assert ans.refused is False
    assert ans.citations == ["doc.md > Duration"]


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
