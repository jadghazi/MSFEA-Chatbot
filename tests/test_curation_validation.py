"""End-to-end deterministic publication validation on isolated databases."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from msfea_bot.config import settings
from msfea_bot.curation.migrations import migrate
from msfea_bot.curation.revisions import (
    DraftPayload,
    EvidenceReference,
    create_draft,
    list_revisions,
)
from msfea_bot.curation.validation import (
    REQUIRED_STEPS,
    execute_step,
    record_human_review,
    start_validation,
    validation_runs,
)
from msfea_bot.ingestion.chunking import Chunk, chunk_normalized_dir
from msfea_bot.retrieval.store import index_chunks


def _db_available() -> bool:
    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
        return True
    except Exception:
        return False


@pytest.fixture
def isolated_pair() -> Iterator[tuple[str, str]]:
    names = [f"guard_prod_{uuid4().hex}", f"guard_validation_{uuid4().hex}"]
    base = conninfo_to_dict(settings.database_url)
    admin_dsn = make_conninfo(**{**base, "dbname": "postgres"})
    dsns = [make_conninfo(**{**base, "dbname": name}) for name in names]
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        for name in names:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    try:
        yield dsns[0], dsns[1]
    finally:
        with psycopg.connect(admin_dsn, autocommit=True) as conn:
            for name in names:
                conn.execute(
                    sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name))
                )


def _payload(excerpt: str = "at least five pages and 1,500 words") -> DraftPayload:
    return DraftPayload(
        question="What is the minimum ECE Final Report length?",
        answer="For ECE, the Final Report must be at least five pages and 1,500 words.",
        department="ece",
        programs=("internship",),
        evidence_refs=(
            EvidenceReference(
                "email-clarifications.md",
                "Final Report requirements (ECE)",
                excerpt,
            ),
        ),
        representative_question="How many pages must my ECE Final Report contain?",
        paraphrase_question="What is the ECE internship Final Report minimum length?",
        expected_evidence="at least five pages and 1,500 words",
        change_reason="Add a source-backed ECE report-length clarification.",
    )


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_full_validation_is_isolated_complete_and_human_gated(
    isolated_pair: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    production_dsn, validation_dsn = isolated_pair
    monkeypatch.setattr(settings, "database_url", production_dsn)
    monkeypatch.setattr(settings, "validation_database_url", validation_dsn)
    migrate()
    index_chunks(chunk_normalized_dir())
    with psycopg.connect(production_dsn, autocommit=True) as conn:
        production_before = conn.execute(
            "SELECT id, text, metadata FROM chunks ORDER BY id"
        ).fetchall()
    entry_id, revision_id = create_draft(_payload())
    run_id = start_validation(revision_id)

    with pytest.raises(ValueError, match="all validation steps"):
        record_human_review(run_id, "Reviewer", "confirm_no_conflict", "Checked sources.")

    for step in REQUIRED_STEPS:
        execute_step(run_id, step)

    with psycopg.connect(production_dsn, autocommit=True) as conn:
        production_ids = [row[0] for row in conn.execute("SELECT id FROM chunks").fetchall()]
    with psycopg.connect(validation_dsn, autocommit=True) as conn:
        validation_ids = [row[0] for row in conn.execute("SELECT id FROM chunks").fetchall()]
    with psycopg.connect(production_dsn, autocommit=True) as conn:
        production_after = conn.execute(
            "SELECT id, text, metadata FROM chunks ORDER BY id"
        ).fetchall()
    assert production_ids
    assert production_after == production_before
    assert any(item.startswith(f"candidate-{entry_id}-") for item in validation_ids)

    run = validation_runs()[0]
    assert {result["step"] for result in run["results"]} == set(REQUIRED_STEPS)
    failures = [result for result in run["results"] if result["status"] != "passed"]
    assert not failures, failures
    assert list_revisions()[0].state in {"blocked", "ready"}

    review_id = record_human_review(
        run_id,
        "CDC reviewer",
        "confirm_no_conflict",
        "Verified the source, applicability, and related passages.",
    )
    assert review_id > 0
    assert list_revisions()[0].state == "ready"
    assert validation_runs()[0]["reviews"][0]["reviewer_label"] == "CDC reviewer"


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_bad_evidence_blocks_immediately_with_precise_result(
    isolated_pair: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    production_dsn, validation_dsn = isolated_pair
    monkeypatch.setattr(settings, "database_url", production_dsn)
    monkeypatch.setattr(settings, "validation_database_url", validation_dsn)
    migrate()
    index_chunks([Chunk("p", "Production.", "p.md", "P")])
    _, revision_id = create_draft(_payload("fabricated evidence phrase"))
    run_id = start_validation(revision_id)

    execute_step(run_id, "schema_source")

    run = validation_runs()[0]
    assert run["status"] == "failed"
    assert run["error_code"] == "schema_source_failed"
    assert "Evidence excerpt not found" in run["results"][0]["details"]["errors"][0]
    assert list_revisions()[0].state == "blocked"
    with pytest.raises(ValueError, match="all validation steps"):
        record_human_review(
            run_id, "Reviewer", "confirm_no_conflict", "I want to override the failure."
        )


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_changed_fingerprint_marks_run_stale(
    isolated_pair: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    production_dsn, validation_dsn = isolated_pair
    monkeypatch.setattr(settings, "database_url", production_dsn)
    monkeypatch.setattr(settings, "validation_database_url", validation_dsn)
    migrate()
    index_chunks([Chunk("p", "Production.", "p.md", "P")])
    _, revision_id = create_draft(_payload())
    run_id = start_validation(revision_id)
    monkeypatch.setattr(settings, "top_k", settings.top_k + 1)

    execute_step(run_id, "schema_source")

    assert validation_runs()[0]["status"] == "stale"
    assert list_revisions()[0].state == "blocked"
