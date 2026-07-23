"""Evaluation metrics (ADR-0002).

Two independent families, kept separate on purpose so a wrong answer is
diagnosed as retrieval-vs-generation first (CLAUDE.md §2, §4):

- Retrieval: recall@k / hit rate.
- Answer, Layer 1: deterministic, no-LLM checks (refusal correctness, citation
  present, disclaimer present). Layer 2 (LLM-as-judge for faithfulness /
  relevance) is added once the LLM provider and real questions exist.

Everything here is a pure function so it is unit-testable now, before a retriever
(Phase 4) or generator (Phase 6) exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --------------------------------------------------------------------------- #
# Retrieval metric
# --------------------------------------------------------------------------- #


def recall_at_k(retrieved_ids: list[str], expected_id: str, k: int) -> bool:
    """True if `expected_id` is among the top-`k` retrieved ids."""
    if k <= 0:
        raise ValueError("k must be positive")
    return expected_id in retrieved_ids[:k]


def hit_rate_at_k(cases: list[tuple[list[str], str]], k: int) -> float:
    """Fraction of cases whose expected id is in the top-`k`.

    `cases` is a list of (retrieved_ids, expected_id) pairs. Returns 0.0 for an
    empty input.
    """
    if not cases:
        return 0.0
    hits = sum(1 for retrieved, expected in cases if recall_at_k(retrieved, expected, k))
    return hits / len(cases)


def evidence_present(chunk_texts: list[str], evidence: str) -> bool:
    """True if the evidence string appears (case-insensitively) in any chunk text.

    This is the *context-recall* signal: did retrieval actually surface the
    passage that contains the answer? It is stricter than document-level recall.
    """
    needle = evidence.lower()
    return any(needle in text.lower() for text in chunk_texts)


# --------------------------------------------------------------------------- #
# Answer metric — Layer 1 (deterministic, no LLM)
# --------------------------------------------------------------------------- #


@dataclass
class BotAnswer:
    """Minimal contract for a bot response, consumed by the Layer-1 checks.

    Generation (Phase 6) will produce a value that maps onto this shape.
    """

    text: str
    citations: list[str] = field(default_factory=list)
    refused: bool = False


def refusal_is_correct(answer: BotAnswer, should_refuse: bool) -> bool:
    """The bot refused exactly when it was supposed to."""
    return answer.refused == should_refuse


def citation_present(answer: BotAnswer) -> bool:
    """Non-refusal answers must cite at least one source (CLAUDE.md §1).

    Refusals escalate to a human and need not cite, so they pass this check.
    """
    if answer.refused:
        return True
    return len(answer.citations) > 0


def disclaimer_present(answer: BotAnswer, marker: str) -> bool:
    """The AI-generated disclaimer (identified by `marker`) appears in the text."""
    return marker.lower() in answer.text.lower()
