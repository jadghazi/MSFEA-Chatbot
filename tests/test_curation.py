"""Integration test for the curation loop (needs the DB; skipped otherwise)."""

import psycopg
import pytest

from msfea_bot.config import settings


def _db_available() -> bool:
    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
        return True
    except Exception:
        return False


def _delete_curated_row(curated_id: int) -> None:
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute("DELETE FROM curated_answers WHERE id = %s", (curated_id,))


def _cleanup(curated_id: int) -> None:
    """Teardown: drop the chunks AND the row.

    Uses the service's own `_drop_chunks` rather than a hand-written delete —
    since ADR-0013 one answer maps to several window chunks, and a teardown that
    deletes only `curated-<n>` leaves `curated-<n>-00` behind as retrievable test
    junk. That leak is what put placeholder text in front of students before.
    """
    from msfea_bot.curation.service import _drop_chunks

    _drop_chunks(curated_id)
    _delete_curated_row(curated_id)


LONG_ANSWER = (
    "Students must submit the Notice of Arrival form during the first week. " * 100
) + "The very last deadline is the final Friday of September."


def test_long_curated_answer_is_windowed_not_truncated() -> None:
    """A long answer must be split, not silently half-indexed (ADR-0013).

    Written as one run-on paragraph on purpose: that is what the dashboard textarea
    produces, and it is the case the plain windower cannot split on its own.
    """
    from msfea_bot.curation.service import _to_chunks

    chunks = _to_chunks(7, "How do I submit my internship forms?", LONG_ANSWER, "admin")

    assert len(chunks) > 1, "an 8000-char answer must not stay a single chunk"
    # The tail is the point: before windowing, everything past ~3,143 chars was
    # stored but unreachable, because the embedding model truncates at 512 tokens.
    assert any("final Friday of September" in c.text for c in chunks), "tail must be indexed"
    assert all(c.text.startswith("Q: How do I submit") for c in chunks), (
        "every window keeps the question, so each chunk is self-describing"
    )
    assert all(len(c.text) < 1200 for c in chunks), "windows stay well inside the token limit"
    assert len({c.id for c in chunks}) == len(chunks), "ids must be unique"


def test_curated_chunk_ids_are_prefix_delete_safe() -> None:
    """`curated-1-` must not also match `curated-10-` — the original footgun."""
    from msfea_bot.curation.service import _chunk_id

    assert not _chunk_id(10, 0).startswith("curated-1-")
    assert _chunk_id(1, 0).startswith("curated-1-")


def test_short_curated_answer_stays_one_chunk() -> None:
    from msfea_bot.curation.service import _to_chunks

    chunks = _to_chunks(3, "How many credits?", "The internship is 3 credits.", "admin")
    assert len(chunks) == 1
    assert chunks[0].id == "curated-3-00"


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_long_answer_tail_is_retrievable_and_fully_removed_on_retire() -> None:
    """End-to-end: the previously-lost tail is searchable, and retire leaves nothing."""
    import psycopg

    from msfea_bot.curation.service import publish_curated_answer, retire_curated_answer
    from msfea_bot.retrieval.store import search

    question = "What is the zzz-test long answer marker question?"
    answer = LONG_ANSWER.replace("final Friday of September", "tail marker ZEBRA-77")
    curated_id = publish_curated_answer(question, answer, "test")
    try:
        with psycopg.connect(settings.database_url, autocommit=True) as conn:
            n = conn.execute(
                "SELECT count(*) FROM chunks WHERE id LIKE %s", (f"curated-{curated_id}-%",)
            ).fetchone()
            assert n is not None and n[0] > 1, "long answer should index as several chunks"

        assert any("ZEBRA-77" in r.text for r in search("tail marker ZEBRA-77", 5)), (
            "the answer's tail must be retrievable, not lost to embedding truncation"
        )

        assert retire_curated_answer(curated_id) is True
        with psycopg.connect(settings.database_url, autocommit=True) as conn:
            left = conn.execute(
                "SELECT count(*) FROM chunks WHERE id LIKE %s", (f"curated-{curated_id}-%",)
            ).fetchone()
            assert left is not None and left[0] == 0, "retire must remove every window"
    finally:
        _cleanup(curated_id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_published_answer_becomes_retrievable() -> None:
    from msfea_bot.curation.service import publish_curated_answer
    from msfea_bot.retrieval.store import search

    question = "What is the zzz-test placeholder internship stipend policy?"
    curated_id = publish_curated_answer(question, "The placeholder stipend marker is XYZZY-42.", "test")
    try:
        results = search(question, 5)
        assert any("XYZZY-42" in r.text for r in results), "curated answer was not retrievable"
    finally:
        _cleanup(curated_id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_retire_removes_chunk_and_deactivates_row() -> None:
    from msfea_bot.curation.service import publish_curated_answer, retire_curated_answer
    from msfea_bot.curation.store import get_curated
    from msfea_bot.retrieval.store import search

    question = "What is the zzz-test retire marker question?"
    curated_id = publish_curated_answer(question, "The retire marker is QWOP-99.", "test")
    try:
        assert any("QWOP-99" in r.text for r in search(question, 5)), "should be retrievable before retire"

        assert retire_curated_answer(curated_id) is True
        # Chunk gone -> no longer retrievable; row kept but inactive.
        assert not any("QWOP-99" in r.text for r in search(question, 5))
        row = get_curated(curated_id)
        assert row is not None and row.active is False
        # Retiring again is a no-op (already inactive).
        assert retire_curated_answer(curated_id) is False
    finally:
        _cleanup(curated_id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_curated_eval_case_follows_edit_and_retire() -> None:
    # Proves the derive-at-run-time design: the eval case stays consistent with
    # the dashboard — an edit regenerates it, a retire removes it. No stale copy.
    from eval.curated_cases import curated_eval_items
    from msfea_bot.curation.service import (
        edit_curated_answer,
        publish_curated_answer,
        retire_curated_answer,
    )

    question = "What is the zzz-test eval-sync marker question?"
    curated_id = publish_curated_answer(question, "Sync marker GAMMA-3.", "test")
    try:
        assert f"curated-{curated_id}" in {i.id for i in curated_eval_items()}

        # Edit -> the derived case regenerates with the new expected text.
        edit_curated_answer(curated_id, question, "Sync marker DELTA-4.")
        item = next(i for i in curated_eval_items() if i.id == f"curated-{curated_id}")
        assert item.expected_answer_or_behavior == "Sync marker DELTA-4."

        # Retire -> the case drops out of the eval set automatically.
        retire_curated_answer(curated_id)
        assert f"curated-{curated_id}" not in {i.id for i in curated_eval_items()}
    finally:
        _cleanup(curated_id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_edit_updates_text_and_reindexes() -> None:
    from msfea_bot.curation.service import edit_curated_answer, publish_curated_answer
    from msfea_bot.retrieval.store import search

    question = "What is the zzz-test edit marker question?"
    curated_id = publish_curated_answer(question, "Old marker ALPHA-1.", "test")
    try:
        assert edit_curated_answer(curated_id, question, "New marker BETA-2.") is True
        texts = " ".join(r.text for r in search(question, 5))
        assert "BETA-2" in texts and "ALPHA-1" not in texts, "chunk should be re-indexed with new text"
    finally:
        _cleanup(curated_id)
