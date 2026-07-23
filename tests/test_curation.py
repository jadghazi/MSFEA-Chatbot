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


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_published_answer_becomes_retrievable() -> None:
    from msfea_bot.curation.service import publish_curated_answer
    from msfea_bot.retrieval.store import delete_chunks, search

    question = "What is the zzz-test placeholder internship stipend policy?"
    curated_id = publish_curated_answer(question, "The placeholder stipend marker is XYZZY-42.", "test")
    try:
        results = search(question, 5)
        assert any("XYZZY-42" in r.text for r in results), "curated answer was not retrievable"
    finally:
        delete_chunks(f"curated-{curated_id}")
