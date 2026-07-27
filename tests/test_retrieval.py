"""Tests for hybrid retrieval: RRF fusion (pure) + keyword recall (DB-gated)."""

from __future__ import annotations

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
