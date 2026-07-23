"""Tests for deriving live eval cases from curated answers (eval.curated_cases)."""

from __future__ import annotations

from datetime import datetime

import pytest

import eval.curated_cases as cc
from msfea_bot.curation.store import CuratedAnswer


def _row(cid: int, q: str, a: str) -> CuratedAnswer:
    return CuratedAnswer(cid, q, a, "admin", datetime(2026, 7, 23), True)


def test_maps_curated_rows_to_golden_items(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        cc, "list_curated", lambda active_only=True: [_row(10, "How many credits?", "Three.")]
    )
    items = cc.curated_eval_items()
    assert len(items) == 1
    item = items[0]
    assert item.id == "curated-10"
    assert item.question == "How many credits?"
    assert item.expected_answer_or_behavior == "Three."
    assert item.should_refuse is False
    assert item.source_doc == cc.CURATED_SOURCE
    # Evidence is the answer text (verbatim in the chunk) -> precise context-recall.
    assert item.evidence == "Three."
    assert item.is_synthetic is True
    assert "curated" in item.tags


def test_only_active_rows_are_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}
    monkeypatch.setattr(
        cc, "list_curated", lambda active_only=True: seen.update(active_only=active_only) or []
    )
    cc.curated_eval_items()
    assert seen == {"active_only": True}


def test_db_failure_degrades_to_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(active_only: bool = True) -> list[CuratedAnswer]:
        raise RuntimeError("db down")

    monkeypatch.setattr(cc, "list_curated", boom)
    # Must not raise — a DB hiccup should not wipe the file-based eval.
    assert cc.curated_eval_items() == []
