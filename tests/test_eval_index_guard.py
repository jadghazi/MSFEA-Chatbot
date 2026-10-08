"""Evaluation must include both normalized files and active approved revisions."""

import pytest

from eval import index_guard
from msfea_bot.ingestion.chunking import Chunk
from msfea_bot.retrieval.store import _generation_hash


def test_canonical_guard_includes_approved_revision_inputs(monkeypatch: pytest.MonkeyPatch) -> None:
    source = Chunk("source", "Normal rule", "source.md", "Rule")
    revision = Chunk("revision", "Approved addition", "reviewed", "Addition")
    monkeypatch.setattr(index_guard, "chunk_normalized_dir", lambda: [source])
    monkeypatch.setattr(index_guard, "curated_chunks", lambda: [revision])
    expected = _generation_hash([source, revision])
    monkeypatch.setattr(index_guard, "indexed_generation", lambda: expected)
    assert index_guard.canonical_generation() == expected

    # An otherwise valid source-only index is stale when an approved input exists.
    monkeypatch.setattr(index_guard, "indexed_generation", lambda: _generation_hash([source]))
    with pytest.raises(RuntimeError, match="canonical inputs"):
        index_guard.canonical_generation()


def test_unindexed_database_cannot_start_evaluation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(index_guard, "chunk_normalized_dir", lambda: [])
    monkeypatch.setattr(index_guard, "curated_chunks", lambda: [])
    monkeypatch.setattr(index_guard, "indexed_generation", lambda: None)
    with pytest.raises(RuntimeError, match="rebuild first"):
        index_guard.canonical_generation()
