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


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_published_answer_becomes_retrievable() -> None:
    from msfea_bot.curation.service import publish_curated_answer
    from msfea_bot.retrieval.store import delete_chunk, search

    question = "What is the zzz-test placeholder internship stipend policy?"
    curated_id = publish_curated_answer(question, "The placeholder stipend marker is XYZZY-42.", "test")
    try:
        results = search(question, 5)
        assert any("XYZZY-42" in r.text for r in results), "curated answer was not retrievable"
    finally:
        # Clean up BOTH the chunk and the row (a dangling row pollutes the KB view).
        delete_chunk(f"curated-{curated_id}")
        _delete_curated_row(curated_id)


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
        _delete_curated_row(curated_id)


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
    from msfea_bot.retrieval.store import delete_chunk

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
        delete_chunk(f"curated-{curated_id}")
        _delete_curated_row(curated_id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_edit_updates_text_and_reindexes() -> None:
    from msfea_bot.curation.service import edit_curated_answer, publish_curated_answer
    from msfea_bot.retrieval.store import delete_chunk, search

    question = "What is the zzz-test edit marker question?"
    curated_id = publish_curated_answer(question, "Old marker ALPHA-1.", "test")
    try:
        assert edit_curated_answer(curated_id, question, "New marker BETA-2.") is True
        texts = " ".join(r.text for r in search(question, 5))
        assert "BETA-2" in texts and "ALPHA-1" not in texts, "chunk should be re-indexed with new text"
    finally:
        delete_chunk(f"curated-{curated_id}")
        _delete_curated_row(curated_id)
