"""Isolated migration rehearsal for guarded curation."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from msfea_bot.config import settings
from msfea_bot.curation.migrations import migrate, migration_status
from msfea_bot.curation.revisions import (
    DraftPayload,
    EvidenceReference,
    create_draft,
    create_successor_draft,
    list_revisions,
    validate_payload,
)


def _db_available() -> bool:
    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
        return True
    except Exception:
        return False


@pytest.fixture
def isolated_database() -> Iterator[str]:
    """Create a real isolated database; never mutate the shared test index."""
    name = f"curation_migration_{uuid4().hex}"
    base = conninfo_to_dict(settings.database_url)
    admin_dsn = make_conninfo(**{**base, "dbname": "postgres"})
    target_dsn = make_conninfo(**{**base, "dbname": name})
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    try:
        yield target_dsn
    finally:
        with psycopg.connect(admin_dsn, autocommit=True) as conn:
            conn.execute(
                sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name))
            )


def _payload(answer: str = "A source-backed answer.", department: str = "ece") -> DraftPayload:
    return DraftPayload(
        question="What is the reviewed rule?",
        answer=answer,
        department=department,
        programs=("internship",),
        evidence_refs=(
            EvidenceReference(
                "summer-training-guidelines-2026.md",
                "Eligibility",
                "minimum of 90 credits",
            ),
        ),
        representative_question="What is the rule?",
        paraphrase_question="Could you explain the rule?",
        expected_evidence="minimum of 90 credits",
        change_reason="Resolve a reviewed content gap.",
        linked_feedback_ids=(4,),
    )


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_guarded_schema_migrates_legacy_rows_losslessly(
    isolated_database: str,
) -> None:
    with psycopg.connect(isolated_database, autocommit=True) as conn:
        conn.execute(
            "CREATE TABLE curated_answers ("
            " id BIGSERIAL PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL,"
            " author TEXT NOT NULL DEFAULT '', created_at TIMESTAMPTZ NOT NULL DEFAULT now(),"
            " active BOOLEAN NOT NULL DEFAULT true)"
        )
        conn.execute(
            "INSERT INTO curated_answers (id, question, answer, author, active) VALUES"
            " (7, 'Active question?', 'Active answer.', 'legacy-admin', true),"
            " (9, 'Retired question?', 'Retired answer.', '', false)"
        )

    assert migrate(isolated_database) == [1, 2]
    assert migrate(isolated_database) == []

    with psycopg.connect(isolated_database, autocommit=True) as conn:
        legacy = conn.execute(
            "SELECT id, question, answer, author, active FROM curated_answers ORDER BY id"
        ).fetchall()
        migrated = conn.execute(
            "SELECT e.id, e.legacy_curated_id, r.question, r.answer, r.department,"
            " r.programs, r.evidence_refs, r.provenance_status, s.state,"
            " e.active_revision_id = r.id"
            " FROM curated_entries e"
            " JOIN curated_revisions r ON r.entry_id = e.id"
            " JOIN curation_revision_state s ON s.revision_id = r.id"
            " ORDER BY e.id"
        ).fetchall()
        events = conn.execute(
            "SELECT count(*) FROM curation_events WHERE event_type = 'legacy_migrated'"
        ).fetchone()
        next_id = conn.execute(
            "INSERT INTO curated_entries DEFAULT VALUES RETURNING id"
        ).fetchone()

    assert legacy == [
        (7, "Active question?", "Active answer.", "legacy-admin", True),
        (9, "Retired question?", "Retired answer.", "", False),
    ]
    assert [(row[0], row[1], row[8], row[9]) for row in migrated] == [
        (7, 7, "active", True),
        (9, 9, "retired", None),
    ]
    assert all(row[4] is None for row in migrated)
    assert all(row[5] == [] and row[6] == [] for row in migrated)
    assert all(row[7] == "needs_review" for row in migrated)
    assert events is not None and events[0] == 2
    assert next_id is not None and next_id[0] > 9

    status = migration_status(isolated_database)
    assert status["available"] == 2
    assert [item["version"] for item in status["applied"]] == [1, 2]


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_submitted_revision_payload_is_database_immutable(
    isolated_database: str,
) -> None:
    migrate(isolated_database)
    with psycopg.connect(isolated_database, autocommit=True) as conn:
        entry_id = conn.execute(
            "INSERT INTO curated_entries DEFAULT VALUES RETURNING id"
        ).fetchone()[0]
        revision_id = conn.execute(
            "INSERT INTO curated_revisions ("
            " entry_id, revision_number, question, answer, department, programs,"
            " evidence_refs, provenance_status, content_hash)"
            " VALUES (%s, 1, 'Q?', 'A.', 'ece', '[\"internship\"]',"
            " '[]', 'submitted', 'sha256:test') RETURNING id",
            (entry_id,),
        ).fetchone()[0]

        with pytest.raises(psycopg.errors.RaiseException):
            conn.execute(
                "UPDATE curated_revisions SET answer = 'Changed' WHERE id = %s",
                (revision_id,),
            )

        stored = conn.execute(
            "SELECT answer FROM curated_revisions WHERE id = %s", (revision_id,)
        ).fetchone()
    assert stored is not None and stored[0] == "A."


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_draft_and_successor_survive_without_becoming_active(
    isolated_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    migrate(isolated_database)
    monkeypatch.setattr(settings, "database_url", isolated_database)

    entry_id, first_id = create_draft(_payload())
    second_id = create_successor_draft(entry_id, _payload("A corrected draft."))

    assert second_id is not None and second_id != first_id
    revisions = list_revisions()
    assert [(item.revision_number, item.state) for item in revisions] == [
        (2, "draft"),
        (1, "draft"),
    ]
    assert revisions[0].predecessor_revision_id == first_id
    assert revisions[0].predecessor_answer == "A source-backed answer."
    assert not any(item.active for item in revisions)

    with psycopg.connect(isolated_database, autocommit=True) as conn:
        legacy_count = conn.execute("SELECT count(*) FROM curated_answers").fetchone()
        chunks_table = conn.execute("SELECT to_regclass('public.chunks')").fetchone()
    assert legacy_count is not None and legacy_count[0] == 0
    assert chunks_table is not None and chunks_table[0] is None

    # A new connection/process can reconstruct the complete draft from durable rows.
    assert list_revisions()[0].answer == "A corrected draft."
    from msfea_bot.curation.service import curated_chunks

    assert curated_chunks() == [], "a full ingestion must exclude every draft revision"


def test_invalid_or_missing_admin_scope_is_rejected_before_storage() -> None:
    with pytest.raises(ValueError, match="department"):
        validate_payload(_payload(department=""))
    with pytest.raises(ValueError, match="department"):
        validate_payload(_payload(department="architecture"))
