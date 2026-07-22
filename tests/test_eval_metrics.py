"""Unit tests for the evaluation metric functions (Layer 1 + retrieval)."""

import pytest

from eval.metrics import (
    BotAnswer,
    citation_present,
    disclaimer_present,
    hit_rate_at_k,
    recall_at_k,
    refusal_is_correct,
)


def test_recall_at_k() -> None:
    assert recall_at_k(["a", "b", "c"], "b", 2) is True
    assert recall_at_k(["a", "b", "c"], "c", 2) is False
    assert recall_at_k([], "a", 3) is False


def test_recall_at_k_rejects_bad_k() -> None:
    with pytest.raises(ValueError):
        recall_at_k(["a"], "a", 0)


def test_hit_rate_at_k() -> None:
    cases = [(["a", "b"], "a"), (["x", "y"], "z")]
    assert hit_rate_at_k(cases, 2) == 0.5
    assert hit_rate_at_k([], 2) == 0.0


def test_refusal_is_correct() -> None:
    assert refusal_is_correct(BotAnswer("x", refused=True), True) is True
    assert refusal_is_correct(BotAnswer("x", refused=False), True) is False
    assert refusal_is_correct(BotAnswer("x", refused=False), False) is True


def test_citation_present() -> None:
    assert citation_present(BotAnswer("x", citations=["doc#sec"])) is True
    assert citation_present(BotAnswer("x", citations=[])) is False
    # A refusal escalates and does not need a citation.
    assert citation_present(BotAnswer("please contact the CDC", citations=[], refused=True)) is True


def test_disclaimer_present() -> None:
    assert disclaimer_present(BotAnswer("... AI-generated, verify with official sources."), "AI-generated") is True
    assert disclaimer_present(BotAnswer("no notice here"), "AI-generated") is False
