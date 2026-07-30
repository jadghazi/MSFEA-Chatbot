"""Tests for hybrid retrieval: RRF fusion (pure) + keyword recall (DB-gated)."""

from __future__ import annotations

from collections.abc import Iterator

import psycopg
import pytest

from msfea_bot.config import settings
from msfea_bot.retrieval.store import reciprocal_rank_fusion


def test_rrf_rewards_agreement_between_retrievers() -> None:
    # "b" is ranked by both lists -> it should win over items ranked by only one.
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["b", "x", "y"]])
    assert fused[0] == "b"


def test_rrf_includes_items_from_either_list() -> None:
    # An item found by only the keyword side must still survive the fusion.
    fused = reciprocal_rank_fusion([["a"], ["z"]])
    assert set(fused) == {"a", "z"}


def test_rrf_empty_input() -> None:
    assert reciprocal_rank_fusion([[], []]) == []


def test_rrf_ties_prefer_first_list() -> None:
    # Same rank in disjoint single-item lists -> first list's item comes first.
    assert reciprocal_rank_fusion([["a"], ["b"]]) == ["a", "b"]


def _db_available() -> bool:
    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_hybrid_surfaces_exact_keyword_match() -> None:
    # A made-up token has no semantic meaning, so pure vector would rank it poorly;
    # the keyword half must still surface it and fusion must keep it. This is the
    # exact-term recall that motivated hybrid search (ADR-0011).
    from msfea_bot.ingestion.chunking import Chunk
    from msfea_bot.retrieval.store import delete_chunk, search, upsert_chunks

    cid = "zzz-hybrid-test"
    upsert_chunks(
        [
            Chunk(
                id=cid,
                text="The placeholder co-op marker token is qwertyztoken for testing.",
                source_doc="zzz-test",
                section="test",
                metadata={},
            )
        ]
    )
    try:
        results = search("qwertyztoken", k=5)
        assert any(r.id == cid for r in results), "exact keyword not retrieved via hybrid"
    finally:
        delete_chunk(cid)


def _db_available() -> bool:
    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
        return True
    except Exception:
        return False


@pytest.fixture
def restore_index() -> Iterator[None]:
    """Rebuild the real index afterwards.

    These tests call index_chunks, which TRUNCATEs — without this a local `pytest`
    run would leave the dev store holding only test rows, and the next question
    would get an empty-context refusal.
    """
    yield
    from msfea_bot.skeleton import ingest

    ingest()


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_rebuild_is_atomic_and_keeps_the_old_index_on_failure(restore_index: None) -> None:
    """A rebuild that dies part-way must not leave a half-built index serving.

    Under autocommit the TRUNCATE committed on its own, so a mid-loop failure left
    the live API answering from an empty store with nothing to roll back.
    """
    from msfea_bot.ingestion.chunking import Chunk
    from msfea_bot.retrieval.store import index_chunks

    good = [
        Chunk(id="atomic-test-1", text="Alpha content.", source_doc="t.md", section="S"),
        Chunk(id="atomic-test-2", text="Beta content.", source_doc="t.md", section="S"),
    ]
    index_chunks(good)
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        before = conn.execute("SELECT count(*) FROM chunks").fetchone()
        assert before is not None and before[0] == 2

    # Duplicate ids violate the primary key partway through the insert loop.
    broken = [*good, Chunk(id="atomic-test-1", text="Dup.", source_doc="t.md", section="S")]
    with pytest.raises(psycopg.errors.Error):
        index_chunks(broken)

    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        after = conn.execute("SELECT count(*) FROM chunks").fetchone()
    assert after is not None and after[0] == 2, "failed rebuild must roll back, not empty the store"


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_chunk_metadata_is_persisted(restore_index: None) -> None:
    """Backlog B-2's reserved slot: frontmatter must survive into the index."""
    from msfea_bot.ingestion.chunking import Chunk
    from msfea_bot.retrieval.store import index_chunks

    index_chunks(
        [
            Chunk(
                id="meta-test-1",
                text="Departmental rule.",
                source_doc="t.md",
                section="S",
                metadata={"department": "cee", "last_updated": "2026-06"},
            )
        ]
    )
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        row = conn.execute(
            "SELECT metadata->>'department', metadata->>'last_updated'"
            " FROM chunks WHERE id = 'meta-test-1'"
        ).fetchone()
    assert row is not None and row[0] == "cee" and row[1] == "2026-06"
