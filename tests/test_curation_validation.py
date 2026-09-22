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
    expected_evidence_present,
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


def _admin_payload() -> DraftPayload:
    return DraftPayload(
        question="When is the weekly CDC advising window?",
        answer="The weekly CDC advising window is Thursday from 2 to 4 p.m.",
        department="all",
        programs=("internship",),
        evidence_refs=(),
        representative_question="When can I attend weekly CDC advising?",
        paraphrase_question="What time is the CDC advising window?",
        expected_evidence="Thursday from 2 to 4 p.m.",
        change_reason="Add a new focused CDC clarification.",
        source_kind="admin_authored",
        document_title="Weekly CDC advising window",
        authority_label="MSFEA CDC",
        effective_date="2026-09-19",
        supporting_reference="CDC operations meeting approval.",
    )


def test_expected_evidence_phrase_ignores_punctuation_but_not_meaning() -> None:
    chunks = ["A: The internship counts towards 6 credits in the engineering program."]

    assert expected_evidence_present(chunks, "6 credits.")
    assert expected_evidence_present(chunks, "6 credits")
    assert not expected_evidence_present(chunks, "9 credits")
    assert not expected_evidence_present(chunks, "six credits")


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
    conflict = next(result for result in run["results"] if result["step"] == "conflict_review")
    assert conflict["details"]["flags"], "the source-backed duplicate must be surfaced"

    review_id = record_human_review(
        run_id,
        "CDC reviewer",
        "valid_scoped_exception",
        "Verified this is an authorized clarification of the cited rule and not a new conflict.",
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
def test_admin_authored_source_validates_without_fake_official_evidence(
    isolated_pair: tuple[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    production_dsn, validation_dsn = isolated_pair
    monkeypatch.setattr(settings, "database_url", production_dsn)
    monkeypatch.setattr(settings, "validation_database_url", validation_dsn)
    migrate()
    index_chunks([Chunk("baseline", "Existing CDC guidance.", "baseline.md", "General")])
    _, revision_id = create_draft(_admin_payload(), actor="Nadia CDC")
    run_id = start_validation(revision_id)

    execute_step(run_id, "schema_source")
    execute_step(run_id, "candidate_index")
    execute_step(run_id, "department_isolation")
    execute_step(run_id, "unknown_department")

    results = {result["step"]: result for result in validation_runs()[0]["results"]}
    result = results["schema_source"]
    assert result["status"] == "passed"
    resolved = result["details"]["resolved_evidence"][0]
    assert resolved["source_doc"].startswith("CDC Knowledge KB-")
    assert resolved["authority"] == "MSFEA CDC"
    assert resolved["source_hash"].startswith("sha256:")
    assert results["department_isolation"]["status"] == "passed"
    assert results["department_isolation"]["details"][
        "candidate_returned_by_department"
    ] == {"mech": True, "ece": True, "chem": True, "iem": True, "cee": True}
    assert results["unknown_department"]["status"] == "passed"
    assert results["unknown_department"]["details"]["labeled"] is True


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
