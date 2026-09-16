"""Fault-injection coverage for atomic KB publication and compensation."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from msfea_bot.config import settings
from msfea_bot.curation.coordination import reconcile
from msfea_bot.curation.migrations import migrate
from msfea_bot.curation.publication import (
    PublicationError,
    compensate_publication,
    execute_publication_intent,
    publish_revision,
    recover_committed_publications,
    request_publication,
    retire_entry,
)
from msfea_bot.curation.revisions import (
    DraftPayload,
    EvidenceReference,
    Revision,
    create_draft,
    create_successor_draft,
    list_revisions,
)
from msfea_bot.curation.validation import REQUIRED_STEPS, validation_fingerprint
from msfea_bot.ingestion.chunking import Chunk
from msfea_bot.retrieval.store import GenerationChanged, index_chunks, indexed_generation


def _db_available() -> bool:
    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
        return True
    except Exception:
        return False


@pytest.fixture
def publication_database(monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    name = f"guard_publish_{uuid4().hex}"
    base = conninfo_to_dict(settings.database_url)
    admin_dsn = make_conninfo(**{**base, "dbname": "postgres"})
    dsn = make_conninfo(**{**base, "dbname": name})
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    try:
        monkeypatch.setattr(settings, "database_url", dsn)
        migrate()
        index_chunks([Chunk("base", "Existing normalized policy.", "base.md", "Base")])
        yield dsn
    finally:
        with psycopg.connect(admin_dsn, autocommit=True) as conn:
            conn.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))


def _payload(answer: str = "For ECE, the Final Report must be at least five pages and 1,500 words.") -> DraftPayload:
    return DraftPayload(
        question="What is the minimum ECE Final Report length?",
        answer=answer,
        department="ece",
        programs=("internship",),
        evidence_refs=(
            EvidenceReference(
                "email-clarifications.md",
                "Final Report requirements (ECE)",
                "at least five pages and 1,500 words",
            ),
        ),
        representative_question="How many pages must my ECE Final Report contain?",
        paraphrase_question="What is the ECE internship Final Report minimum length?",
        expected_evidence="at least five pages and 1,500 words",
        change_reason="Publish a reviewed ECE report-length clarification.",
        linked_feedback_ids=(41,),
    )


def _authorize(revision_id: int) -> str:
    revision = next(item for item in list_revisions() if item.id == revision_id)
    run_id = str(uuid4())
    fingerprint = validation_fingerprint(revision)
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute(
            "INSERT INTO curation_validation_runs"
            " (id, revision_id, fingerprint, status, candidate_generation, completed_at)"
            " VALUES (%s, %s, %s, 'passed', 'candidate:test', now())",
            (run_id, revision_id, fingerprint),
        )
        for step in REQUIRED_STEPS:
            conn.execute(
                "INSERT INTO curation_validation_results"
                " (run_id, step, status, details, started_at, completed_at)"
                " VALUES (%s, %s, 'passed', '{}', now(), now())",
                (run_id, step),
            )
        conn.execute(
            "INSERT INTO curation_human_reviews"
            " (revision_id, validation_run_id, fingerprint, decision, reviewer_label, reason)"
            " VALUES (%s, %s, %s, 'confirm_no_conflict', 'CDC reviewer', 'Sources checked')",
            (revision_id, run_id, fingerprint),
        )
        conn.execute(
            "UPDATE curation_revision_state SET state = 'ready', reason = 'Reviewed'"
            " WHERE revision_id = %s",
            (revision_id,),
        )
    return run_id


def _active_and_chunks(entry_id: int) -> tuple[int | None, list[str]]:
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        active = conn.execute(
            "SELECT active_revision_id FROM curated_entries WHERE id = %s", (entry_id,)
        ).fetchone()
        chunks = conn.execute(
            "SELECT id FROM chunks WHERE id LIKE %s ORDER BY id", (f"curated-{entry_id}-%",)
        ).fetchall()
    return (int(active[0]) if active and active[0] is not None else None, [r[0] for r in chunks])


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_publish_is_atomic_review_bound_and_idempotent(
    publication_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    invalidations: list[str] = []
    resolved: list[int] = []
    monkeypatch.setattr(
        "msfea_bot.curation.publication.resolve_interaction",
        lambda interaction_id: resolved.append(interaction_id) or True,
    )

    result = publish_revision(
        revision_id,
        run_id,
        invalidate_cache=lambda: invalidations.append("invalidate"),
    )
    duplicate = publish_revision(
        revision_id,
        run_id,
        invalidate_cache=lambda: invalidations.append("unexpected"),
        smoke=lambda revision: pytest.fail("idempotent publish must not rerun smoke"),
    )

    active, chunk_ids = _active_and_chunks(entry_id)
    assert active == revision_id
    assert chunk_ids and all(f"curated-{entry_id}-r1-" in item for item in chunk_ids)
    assert result.status == "active" and result.generation == indexed_generation()
    assert duplicate.idempotent and duplicate.attempt_id == result.attempt_id
    assert invalidations == ["invalidate"]
    assert resolved == [41]
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        projection = conn.execute(
            "SELECT answer, active FROM curated_answers WHERE id = %s", (entry_id,)
        ).fetchone()
        attempt = conn.execute(
            "SELECT status FROM curation_publication_attempts WHERE id = %s",
            (result.attempt_id,),
        ).fetchone()
    assert projection == (_payload().answer, True)
    assert attempt == ("smoke_passed",)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_publication_intent_cannot_expose_draft_before_worker_execution(
    publication_database: str,
) -> None:
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    before_generation = indexed_generation()

    intent = request_publication(revision_id, run_id)
    duplicate_intent = request_publication(revision_id, run_id)

    assert intent.status == "intent" and duplicate_intent.idempotent
    assert duplicate_intent.attempt_id == intent.attempt_id
    assert _active_and_chunks(entry_id) == (None, [])
    assert indexed_generation() == before_generation
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        outbox = conn.execute(
            "SELECT count(*) FROM curation_outbox WHERE event_type = 'publication_requested'"
            " AND aggregate_id = %s",
            (intent.attempt_id,),
        ).fetchone()
    assert outbox == (1,)

    with pytest.raises(PublicationError, match="does not exist"):
        execute_publication_intent(str(uuid4()), smoke=lambda _: (True, "unused"))
    assert _active_and_chunks(entry_id) == (None, [])

    result = execute_publication_intent(
        intent.attempt_id, smoke=lambda _: (True, "passed")
    )
    assert result.status == "active"
    assert execute_publication_intent(intent.attempt_id).idempotent
    assert _active_and_chunks(entry_id)[0] == revision_id


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_abandoned_publication_intent_fails_closed(
    publication_database: str,
) -> None:
    entry_id, revision_id = create_draft(_payload())
    intent = request_publication(revision_id, _authorize(revision_id))
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute(
            "UPDATE curation_publication_attempts SET created_at ="
            " now() - interval '2 hours' WHERE id = %s",
            (intent.attempt_id,),
        )

    assert reconcile()["expired_publication_intents"] == 1
    assert _active_and_chunks(entry_id) == (None, [])
    assert next(item for item in list_revisions() if item.id == revision_id).state == "blocked"
    with pytest.raises(PublicationError, match="failed_precommit"):
        execute_publication_intent(intent.attempt_id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_failure_before_commit_rolls_back_every_live_write(
    publication_database: str,
) -> None:
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    before_generation = indexed_generation()

    def fail(point: str) -> None:
        if point == "before_commit":
            raise RuntimeError("injected precommit failure")

    with pytest.raises(PublicationError, match="before commit"):
        publish_revision(
            revision_id, run_id, smoke=lambda revision: (True, "unused"), fault=fail
        )

    assert _active_and_chunks(entry_id) == (None, [])
    assert indexed_generation() == before_generation
    assert next(item for item in list_revisions() if item.id == revision_id).state == "blocked"
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        attempt = conn.execute(
            "SELECT status FROM curation_publication_attempts WHERE revision_id = %s",
            (revision_id,),
        ).fetchone()
    assert attempt == ("failed_precommit",)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_missing_review_or_result_cannot_publish(publication_database: str) -> None:
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute(
            "DELETE FROM curation_human_reviews WHERE validation_run_id = %s", (run_id,)
        )
    with pytest.raises(PublicationError, match="mandatory human"):
        publish_revision(revision_id, run_id, smoke=lambda revision: (True, "unused"))
    assert _active_and_chunks(entry_id) == (None, [])

    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        fingerprint = validation_fingerprint(_revision_by_id(revision_id))
        conn.execute(
            "INSERT INTO curation_human_reviews"
            " (revision_id, validation_run_id, fingerprint, decision, reviewer_label, reason)"
            " VALUES (%s, %s, %s, 'confirm_no_conflict', 'Reviewer', 'Checked')",
            (revision_id, run_id, fingerprint),
        )
        conn.execute(
            "DELETE FROM curation_validation_results WHERE run_id = %s AND step = %s",
            (run_id, REQUIRED_STEPS[-1]),
        )
    with pytest.raises(PublicationError, match="incomplete or failed"):
        publish_revision(revision_id, run_id, smoke=lambda revision: (True, "unused"))
    assert _active_and_chunks(entry_id) == (None, [])


def _revision_by_id(revision_id: int) -> Revision:
    return next(item for item in list_revisions() if item.id == revision_id)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_stale_publish_schedules_fresh_full_validation(
    publication_database: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    entry_id, revision_id = create_draft(_payload())
    old_run = _authorize(revision_id)
    monkeypatch.setattr(settings, "top_k", settings.top_k + 1)

    with pytest.raises(PublicationError, match="stale_validation"):
        publish_revision(revision_id, old_run, smoke=lambda revision: (True, "unused"))

    assert _active_and_chunks(entry_id) == (None, [])
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        runs = conn.execute(
            "SELECT id, status FROM curation_validation_runs"
            " WHERE revision_id = %s ORDER BY created_at",
            (revision_id,),
        ).fetchall()
    assert len(runs) == 2
    assert runs[0] == (old_run, "passed")
    assert runs[1][1] == "pending"
    assert _revision_by_id(revision_id).state == "validating"


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
@pytest.mark.parametrize("failure_point", ["after_commit", "before_smoke", "smoke"])
def test_postcommit_failures_restore_previous_revision(
    publication_database: str,
    failure_point: str,
) -> None:
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    before_generation = indexed_generation()
    invalidations: list[str] = []

    def fail(point: str) -> None:
        if point == failure_point:
            raise RuntimeError(f"injected {point} failure")

    def smoke(_: object) -> tuple[bool, str]:
        return (False, "injected smoke failure") if failure_point == "smoke" else (True, "passed")

    with pytest.raises(PublicationError):
        publish_revision(
            revision_id,
            run_id,
            invalidate_cache=lambda: invalidations.append("invalidate"),
            smoke=smoke,
            fault=fail,
        )

    assert _active_and_chunks(entry_id) == (None, [])
    assert indexed_generation() == before_generation
    assert invalidations
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        attempt = conn.execute(
            "SELECT status FROM curation_publication_attempts"
            " WHERE revision_id = %s AND validation_run_id = %s",
            (revision_id, run_id),
        ).fetchone()
    assert attempt == ("compensated",)


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_failed_postcommit_cache_callback_compensates_before_smoke(
    publication_database: str,
) -> None:
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    before_generation = indexed_generation()
    callbacks: list[str] = []

    def invalidate() -> None:
        callbacks.append("invalidate")
        if len(callbacks) == 1:
            raise ConnectionError("injected callback outage")

    with pytest.raises(PublicationError, match="compensated"):
        publish_revision(
            revision_id,
            run_id,
            invalidate_cache=invalidate,
            smoke=lambda _: pytest.fail("smoke must not run without cache invalidation"),
        )

    assert callbacks == ["invalidate", "invalidate"]
    assert _active_and_chunks(entry_id) == (None, [])
    assert indexed_generation() == before_generation
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        attempt = conn.execute(
            "SELECT status, error_code FROM curation_publication_attempts"
            " WHERE revision_id = %s AND validation_run_id = %s",
            (revision_id, run_id),
        ).fetchone()
    assert attempt == ("compensated", "cache_invalidation_failed")


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_persistent_cache_callback_failure_still_restores_database(
    publication_database: str,
) -> None:
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    before_generation = indexed_generation()

    def unavailable() -> None:
        raise ConnectionError("injected persistent callback outage")

    with pytest.raises(PublicationError, match="requires recovery"):
        publish_revision(
            revision_id,
            run_id,
            invalidate_cache=unavailable,
            smoke=lambda _: pytest.fail("smoke must not run without cache invalidation"),
        )

    assert _active_and_chunks(entry_id) == (None, [])
    assert indexed_generation() == before_generation
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        attempt = conn.execute(
            "SELECT status, error_code FROM curation_publication_attempts"
            " WHERE revision_id = %s AND validation_run_id = %s",
            (revision_id, run_id),
        ).fetchone()
    assert attempt == ("compensated", "cache_invalidation_failed")


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_successor_replaces_predecessor_and_retirement_is_atomic(
    publication_database: str,
) -> None:
    entry_id, first_id = create_draft(_payload())
    first_run = _authorize(first_id)
    publish_revision(first_id, first_run, smoke=lambda revision: (True, "passed"))
    second_id = create_successor_draft(
        entry_id,
        _payload("For ECE, the reviewed minimum is five pages and 1,500 words."),
    )
    assert second_id is not None
    assert _active_and_chunks(entry_id)[0] == first_id
    second_run = _authorize(second_id)
    publish_revision(second_id, second_run, smoke=lambda revision: (True, "passed"))

    active, chunks = _active_and_chunks(entry_id)
    assert active == second_id
    assert chunks and all("-r2-" in item for item in chunks)
    states = {item.id: item.state for item in list_revisions()}
    assert states[first_id] == "retired" and states[second_id] == "active"

    invalidations: list[str] = []
    generation = retire_entry(
        entry_id,
        "Clarification is no longer authoritative.",
        invalidate_cache=lambda: invalidations.append("invalidate"),
    )
    assert _active_and_chunks(entry_id) == (None, [])
    assert generation == indexed_generation()
    assert invalidations == ["invalidate"]


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_failed_successor_smoke_restores_predecessor_content(
    publication_database: str,
) -> None:
    entry_id, first_id = create_draft(_payload())
    publish_revision(first_id, _authorize(first_id), smoke=lambda revision: (True, "passed"))
    before_generation = indexed_generation()
    second_id = create_successor_draft(
        entry_id,
        _payload("For ECE, a proposed replacement says five pages and 1,500 words."),
    )
    assert second_id is not None

    with pytest.raises(PublicationError, match="compensated"):
        publish_revision(
            second_id,
            _authorize(second_id),
            smoke=lambda revision: (False, "candidate missing from serving path"),
        )

    active, chunks = _active_and_chunks(entry_id)
    assert active == first_id
    assert chunks and all("-r1-" in item for item in chunks)
    assert indexed_generation() == before_generation


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_delayed_compensation_cannot_roll_back_newer_publication(
    publication_database: str,
) -> None:
    entry_id, first_id = create_draft(_payload())
    first_run = _authorize(first_id)
    first = publish_revision(first_id, first_run, smoke=lambda revision: (True, "passed"))
    second_id = create_successor_draft(
        entry_id,
        _payload("For ECE, the reviewed minimum remains five pages and 1,500 words."),
    )
    assert second_id is not None
    second_run = _authorize(second_id)
    publish_revision(second_id, second_run, smoke=lambda revision: (True, "passed"))
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute(
            "UPDATE curation_publication_attempts SET status = 'committed' WHERE id = %s",
            (first.attempt_id,),
        )

    delayed = compensate_publication(first.attempt_id, "late smoke callback")

    assert delayed.status == "compensation_skipped"
    assert _active_and_chunks(entry_id)[0] == second_id


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_stale_rebuild_generation_cannot_overwrite_publication(
    publication_database: str,
) -> None:
    stale_generation = indexed_generation()
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    publish_revision(revision_id, run_id, smoke=lambda revision: (True, "passed"))

    with pytest.raises(GenerationChanged):
        index_chunks(
            [Chunk("stale", "Stale rebuild.", "stale.md", "Stale")],
            expected_generation=stale_generation,
        )

    assert _active_and_chunks(entry_id)[0] == revision_id


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_concurrent_successor_creation_prevents_older_revision_publication(
    publication_database: str,
) -> None:
    entry_id, revision_id = create_draft(_payload())
    run_id = _authorize(revision_id)
    successor_ids: list[int] = []

    def create_edit(point: str) -> None:
        if point == "after_lock":
            successor = create_successor_draft(
                entry_id,
                _payload("A newer administrator edit remains an unpublished draft."),
            )
            assert successor is not None
            successor_ids.append(successor)

    with pytest.raises(PublicationError, match="newer successor"):
        publish_revision(
            revision_id,
            run_id,
            smoke=lambda revision: (True, "unused"),
            fault=create_edit,
        )

    assert successor_ids
    assert _active_and_chunks(entry_id) == (None, [])
    states = {item.id: item.state for item in list_revisions()}
    assert states[revision_id] == "blocked"
    assert states[successor_ids[0]] == "draft"


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_recovery_compensates_committed_attempt_left_by_crash(
    publication_database: str,
) -> None:
    entry_id, revision_id = create_draft(_payload())
    result = publish_revision(
        revision_id, _authorize(revision_id), smoke=lambda revision: (True, "passed")
    )
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute(
            "UPDATE curation_publication_attempts SET status = 'committed' WHERE id = %s",
            (result.attempt_id,),
        )

    recovered = recover_committed_publications()

    assert recovered == ["compensated"]
    assert _active_and_chunks(entry_id) == (None, [])
