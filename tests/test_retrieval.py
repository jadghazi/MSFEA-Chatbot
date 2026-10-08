"""Tests for hybrid retrieval: RRF fusion (pure) + keyword recall (DB-gated)."""

from __future__ import annotations

from collections.abc import Iterator

import psycopg
import pytest

from msfea_bot.config import settings
from msfea_bot.retrieval.store import _normalize_quantity_spacing, reciprocal_rank_fusion


@pytest.mark.parametrize("joined, spaced", [
    ("Can I do 6weeks of internship?", "Can I do 6 weeks of internship?"),
    ("12credits and 1.5months", "12 credits and 1.5 months"),
    ("6WEEKS", "6 WEEKS"),
    ("EECE500 CHEN500 6+2 2026-09-28", "EECE500 CHEN500 6+2 2026-09-28"),
    ("abc6weeks 6weeksville", "abc6weeks 6weeksville"),
])
def test_quantity_spacing_preserves_meaning_and_identifiers(joined: str, spaced: str) -> None:
    assert _normalize_quantity_spacing(joined) == spaced
    assert _normalize_quantity_spacing(spaced) == spaced


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


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_search_returns_chunk_metadata(restore_index: None) -> None:
    """Generation needs applicability metadata, not only the database filter."""
    from msfea_bot.ingestion.chunking import Chunk
    from msfea_bot.retrieval.store import index_chunks, search

    index_chunks(
        [
            Chunk(
                id="meta-search-1",
                text="The scoped marker is ORCHID-29.",
                source_doc="rules.md",
                section="Scoped rule",
                metadata={"department": "cee", "program": "internship"},
            )
        ]
    )

    result = next(chunk for chunk in search("ORCHID-29", k=1) if chunk.id == "meta-search-1")
    assert result.metadata == {"department": "cee", "program": "internship"}


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_department_scoping_excludes_other_departments() -> None:
    """A student must never be shown another department's contradictory rule.

    Unscoped, "can I split my internship into two 4-week periods?" returns four
    departments' rules at once — MECH forbids it, CEE allows it conditionally.
    """
    from msfea_bot.retrieval.store import search

    q = "Can I split my internship into two 4-week periods?"
    scoped_chunks = search(q, 5, department="cee")
    scoped = [chunk.section for chunk in scoped_chunks]
    assert any("(CEE)" in s for s in scoped), "the student's own rule must be present"
    assert any(chunk.metadata.get("department") in {None, "all"} for chunk in scoped_chunks), (
        "general guidance must remain available beside the selected department's rule"
    )
    for other in ("(MECH)", "(CHEM)", "(ECE)", "(IEM)"):
        assert not any(other in s for s in scoped), f"{other} leaked into a CEE answer"


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_department_slot_is_reserved_when_the_rule_would_be_crowded_out() -> None:
    """The case exclusion alone does not fix.

    IEM's "final presentations are generally not required" sits at vector rank 8 for
    this question, so without a reserved slot an IEM student is told the general rule
    — which is wrong for them.
    """
    from msfea_bot.retrieval.store import search

    q = "Must I submit a final presentation?"
    assert not any("(IEM)" in c.section for c in search(q, 5)), (
        "precondition: unscoped search should NOT surface the IEM exception"
    )
    assert any("(IEM)" in c.section for c in search(q, 5, department="iem"))


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_unknown_department_behaves_exactly_like_no_department() -> None:
    """Untrusted input must degrade, not change results or raise."""
    from msfea_bot.retrieval.store import search

    q = "What is the minimum internship duration?"
    assert [c.id for c in search(q, 5, department="nonsense")] == [
        c.id for c in search(q, 5)
    ]
def test_comparisons_get_more_evidence_without_widening_every_question() -> None:
    from msfea_bot.retrieval.store import retrieval_depth

    assert retrieval_depth("Compare the two programs", 7) == 12
    assert retrieval_depth("What is the difference between them?", 7) == 12
    assert retrieval_depth("Is six plus two enough with another course?", 7) == 7
    assert retrieval_depth("Compare these options", 15) == 15


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_numeric_rule_application_keeps_threshold_evidence_in_prompt_depth() -> None:
    from msfea_bot.retrieval.store import search

    chunks = search("I have completed 88 credits. Can I register for the internship?", 7)

    assert any("minimum of 90 credits" in chunk.text.replace("**", "") for chunk in chunks)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_scoped_semantic_rescue_respects_requested_depth() -> None:
    from msfea_bot.retrieval.store import search

    assert len(search("What is the Moodle quiz passing score?", 1, department="ece")) == 1


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
@pytest.mark.parametrize("department", ["ece", "iem", "mech", "chem", "cee"])
def test_joined_duration_retrieves_the_same_evidence(department: str) -> None:
    from msfea_bot.retrieval.store import search

    joined = search("Can I do 6weeks of internship?", 7, department=department)
    spaced = search("Can I do 6 weeks of internship?", 7, department=department)
    assert [(c.id, c.score) for c in joined] == [(c.id, c.score) for c in spaced]


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_linked_evidence_keeps_base_and_only_applicable_companions() -> None:
    from msfea_bot.ingestion.chunking import Chunk
    from msfea_bot.retrieval.store import (
        RetrievedChunk, delete_chunk, expand_evidence_links, upsert_chunks,
    )

    sources = [Chunk("zzz-base-tail", "The restriction in another window.", "zzz-policy.md", "Base",
                     {"department": "all"}),
               Chunk("zzz-ece", "An approval condition.", "zzz-policy.md", "ECE condition",
                     {"department": "ece"}),
               Chunk("zzz-iem", "A different condition.", "zzz-policy.md", "IEM condition",
                     {"department": "iem"})]
    upsert_chunks(sources)
    seed = RetrievedChunk("zzz-base", "General rule.", "zzz-policy.md", "Base", 0.61,
                          {"evidence_links": "zzz-policy.md > ECE condition | zzz-policy.md > IEM condition"})
    try:
        result = expand_evidence_links([seed], "General rule", "ece")
        assert result[0] is seed
        assert [chunk.id for chunk in result[1:]] == ["zzz-base-tail", "zzz-ece"]
        assert result[1].metadata["retrieval_role"] == "companion"
        assert len(expand_evidence_links(result, "General rule", "ece")) == 3
    finally:
        for source in sources:
            delete_chunk(source.id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_stage_filter_applies_before_ranking_and_to_linked_context() -> None:
    from msfea_bot.ingestion.chunking import Chunk
    from msfea_bot.retrieval.store import (
        RetrievedChunk, delete_chunk, expand_evidence_links, search, upsert_chunks,
    )

    sources = [
        Chunk("zzz-stage-entry", "qwertystemployment admission does not guarantee placement.",
              "zzz-stage.md", "Admission", {"process_stage": "entry"}),
        Chunk("zzz-stage-later", "qwertystemployment after training includes career support.",
              "zzz-stage.md", "Later support", {"process_stage": "post_completion"}),
    ]
    upsert_chunks(sources)
    try:
        assert any(c.id == sources[0].id for c in search("qwertystemployment", k=7))
        filtered = search("qwertystemployment", k=7, excluded_stages=("entry",))
        assert any(c.id == sources[1].id for c in filtered)
        assert not any(c.metadata.get("process_stage") == "entry" for c in filtered)
        seed = RetrievedChunk("zzz-stage-seed", "Training overview", "zzz-stage.md", "Overview", 0.7,
                              {"evidence_links": "zzz-stage.md > Admission | zzz-stage.md > Later support"})
        bundle = expand_evidence_links([seed], "qwertystemployment", None,
                                       excluded_stages=("entry",))
        assert [c.id for c in bundle] == [seed.id, sources[1].id]
    finally:
        for source in sources:
            delete_chunk(source.id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_revision_bundle_restores_only_the_same_revision_and_applicable_scope() -> None:
    from msfea_bot.generation.answer import _answer_context, passes_similarity_gate
    from msfea_bot.ingestion.chunking import Chunk
    from msfea_bot.retrieval.store import RetrievedChunk, delete_chunk, expand_evidence_links, upsert_chunks

    metadata = {"revision_bundle": "999999", "revision_id": "999999", "entry_id": "999999", "department": "ece", "process_stage": "completion"}
    sources = [
        Chunk("zzz-bundle-condition", "Completion requires a separately approved final report.", "same-title", "Report", metadata),
        Chunk("zzz-bundle-old", "An old superseded condition.", "same-title", "Report", {**metadata, "revision_id": "999998"}),
        Chunk("zzz-bundle-other-entry", "Another entry's condition.", "same-title", "Report", {**metadata, "entry_id": "999998"}),
        Chunk("zzz-bundle-other-dept", "A condition outside this department.", "same-title", "Report", {**metadata, "department": "iem"}),
    ]
    upsert_chunks(sources)
    seed = RetrievedChunk("zzz-bundle-seed", "Report submission procedure.", "same-title", "Report", 0.61, metadata)
    try:
        bundle = expand_evidence_links([seed], "Report submission procedure", "ece")
        assert [chunk.id for chunk in bundle] == [seed.id, sources[0].id]
        assert _answer_context("Report procedure", bundle, None) == bundle
        assert not passes_similarity_gate(bundle, 0.99)
        assert expand_evidence_links([seed], "Report procedure", "ece", excluded_stages=("completion",)) == [seed]
    finally:
        for source in sources:
            delete_chunk(source.id)
