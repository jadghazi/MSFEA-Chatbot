"""Atomic guarded publication, retirement, smoke checks, and compensation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import psycopg
from psycopg.types.json import Json

from eval.metrics import evidence_present
from msfea_bot.config import settings
from msfea_bot.curation.revisions import Revision, list_revisions
from msfea_bot.curation.service import revision_chunks
from msfea_bot.curation.validation import REQUIRED_STEPS, start_validation, validation_fingerprint
from msfea_bot.observability.store import resolve_interaction
from msfea_bot.retrieval.store import (
    acquire_kb_write_lock,
    index_is_ready,
    prepare_chunks,
    refresh_generation,
    replace_prepared_chunks,
    retrieval_depth,
    search,
)

CacheInvalidator = Callable[[], None]
FaultHook = Callable[[str], None]


class PublicationError(ValueError):
    """A publication precondition or post-commit smoke check failed."""


@dataclass(frozen=True)
class PublicationResult:
    attempt_id: str
    revision_id: int
    status: str
    generation: str | None
    idempotent: bool = False


def _connect() -> Any:
    return psycopg.connect(settings.database_url, autocommit=False, connect_timeout=5)


def _revision(revision_id: int) -> Revision:
    revision = next((item for item in list_revisions() if item.id == revision_id), None)
    if revision is None:
        raise PublicationError("revision does not exist")
    return revision


def _project_legacy(conn: Any, revision: Revision | None, entry_id: int) -> None:
    if revision is None:
        conn.execute("UPDATE curated_answers SET active = false WHERE id = %s", (entry_id,))
        return
    conn.execute(
        "INSERT INTO curated_answers (id, question, answer, author, created_at, active)"
        " VALUES (%s, %s, %s, %s, %s, true)"
        " ON CONFLICT (id) DO UPDATE SET question = EXCLUDED.question,"
        " answer = EXCLUDED.answer, author = EXCLUDED.author, active = true",
        (
            entry_id,
            revision.question,
            revision.answer,
            revision.created_by,
            revision.created_at,
        ),
    )
    conn.execute(
        "SELECT setval(pg_get_serial_sequence('curated_answers', 'id'),"
        " COALESCE((SELECT max(id) FROM curated_answers), 1),"
        " EXISTS (SELECT 1 FROM curated_answers))"
    )


def _assert_authorized(
    conn: Any, revision: Revision, run_id: str, expected_fingerprint: str
) -> None:
    row = conn.execute(
        "SELECT r.status, r.fingerprint, s.state, r.candidate_generation"
        " FROM curation_validation_runs r"
        " JOIN curation_revision_state s ON s.revision_id = r.revision_id"
        " WHERE r.id = %s AND r.revision_id = %s FOR UPDATE OF r, s",
        (run_id, revision.id),
    ).fetchone()
    if row is None:
        raise PublicationError("validation run does not match the revision")
    if row[0] != "passed":
        raise PublicationError("validation run has not passed")
    if not row[3]:
        raise PublicationError("validation run has no isolated candidate generation")
    if row[1] != expected_fingerprint or validation_fingerprint(revision) != row[1]:
        raise PublicationError("stale_validation: revision, source, configuration, or KB changed")
    results = conn.execute(
        "SELECT step, status FROM curation_validation_results WHERE run_id = %s", (run_id,)
    ).fetchall()
    statuses = {str(item[0]): str(item[1]) for item in results}
    if set(statuses) != set(REQUIRED_STEPS) or any(
        status != "passed" for status in statuses.values()
    ):
        raise PublicationError("validation results are incomplete or failed")
    review = conn.execute(
        "SELECT decision FROM curation_human_reviews"
        " WHERE revision_id = %s AND validation_run_id = %s AND fingerprint = %s"
        " ORDER BY reviewed_at DESC LIMIT 1",
        (revision.id, run_id, expected_fingerprint),
    ).fetchone()
    if review is None or review[0] == "reject":
        raise PublicationError("mandatory human source/conflict review is missing")
    if row[2] != "ready":
        raise PublicationError(f"revision state is {row[2]!r}, expected 'ready'")


def _smoke(revision: Revision) -> tuple[bool, str]:
    if not index_is_ready():
        return False, "serving index is not ready for the configured embedding model"
    question = revision.representative_question or revision.question
    chunks = search(
        question,
        retrieval_depth(question, settings.top_k),
        department=revision.department if revision.department != "all" else None,
    )
    expected_ids = {chunk.id for chunk in revision_chunks(revision)}
    ids = {chunk.id for chunk in chunks}
    if not expected_ids & ids:
        return False, "published revision was absent from uncached serving retrieval"
    if revision.expected_evidence and not evidence_present(
        [chunk.text for chunk in chunks], revision.expected_evidence
    ):
        return False, "published supporting evidence was absent from serving retrieval"
    return True, "serving retrieval returned the published revision and evidence"


def _record_precommit_failure(
    revision: Revision,
    run_id: str,
    attempt_id: str,
    fingerprint: str,
    error: Exception,
) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO curation_publication_attempts"
            " (id, revision_id, validation_run_id, fingerprint, status, error_code,"
            " error_detail, completed_at) VALUES (%s, %s, %s, %s, 'failed_precommit',"
            " 'precommit_failure', %s, now()) ON CONFLICT (revision_id, validation_run_id)"
            " DO UPDATE SET status = 'failed_precommit', error_code = 'precommit_failure',"
            " error_detail = EXCLUDED.error_detail, completed_at = now()",
            (attempt_id, revision.id, run_id, fingerprint, str(error)),
        )
        conn.execute(
            "UPDATE curation_revision_state SET state = 'blocked', reason = %s,"
            " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
            ("Publication failed before commit; retry requires review: " + str(error), revision.id),
        )
        conn.execute(
            "INSERT INTO curation_events (entry_id, revision_id, validation_run_id,"
            " event_type, actor_type, reason) VALUES (%s, %s, %s,"
            " 'publication_failed_precommit', 'admin', %s)",
            (revision.entry_id, revision.id, run_id, str(error)),
        )


def compensate_publication(
    attempt_id: str,
    reason: str,
    *,
    invalidate_cache: CacheInvalidator = lambda: None,
) -> PublicationResult:
    """Restore the prior active revision only if this attempt is still active."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT revision_id, prior_revision_id, status FROM curation_publication_attempts"
            " WHERE id = %s",
            (attempt_id,),
        ).fetchone()
    if row is None:
        raise PublicationError("publication attempt does not exist")
    if row[2] in {"compensated", "compensation_skipped"}:
        return PublicationResult(attempt_id, int(row[0]), str(row[2]), None, idempotent=True)
    if row[2] not in {"committed", "smoke_failed"}:
        raise PublicationError(f"attempt in state {row[2]!r} cannot be compensated")
    revision = _revision(int(row[0]))
    prior = _revision(int(row[1])) if row[1] is not None else None
    prepared = prepare_chunks(revision_chunks(prior)) if prior is not None else []
    with _connect() as conn:
        acquire_kb_write_lock(conn)
        active = conn.execute(
            "SELECT active_revision_id FROM curated_entries WHERE id = %s FOR UPDATE",
            (revision.entry_id,),
        ).fetchone()
        if active is None:
            raise PublicationError("publication entry does not exist")
        if active[0] != revision.id:
            conn.execute(
                "UPDATE curation_publication_attempts SET status = 'compensation_skipped',"
                " error_code = 'newer_revision_active', error_detail = %s, completed_at = now()"
                " WHERE id = %s",
                (reason, attempt_id),
            )
            conn.execute(
                "INSERT INTO curation_events (entry_id, revision_id, event_type, actor_type, reason)"
                " VALUES (%s, %s, 'compensation_skipped', 'worker', %s)",
                (revision.entry_id, revision.id, reason),
            )
            return PublicationResult(attempt_id, revision.id, "compensation_skipped", None)
        replace_prepared_chunks(conn, f"curated-{revision.entry_id}-", prepared)
        conn.execute(
            "UPDATE curated_entries SET active_revision_id = %s WHERE id = %s",
            (prior.id if prior else None, revision.entry_id),
        )
        conn.execute(
            "UPDATE curation_revision_state SET state = 'blocked', reason = %s,"
            " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
            ("Post-publication smoke failed: " + reason, revision.id),
        )
        if prior is not None:
            conn.execute(
                "UPDATE curation_revision_state SET state = 'active',"
                " reason = 'Restored after successor smoke failure',"
                " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
                (prior.id,),
            )
        _project_legacy(conn, prior, revision.entry_id)
        generation = refresh_generation(conn)
        conn.execute(
            "UPDATE curation_publication_attempts SET status = 'compensated',"
            " error_code = 'smoke_failed', error_detail = %s, completed_at = now() WHERE id = %s",
            (reason, attempt_id),
        )
        conn.execute(
            "INSERT INTO curation_events (entry_id, revision_id, event_type, actor_type,"
            " reason, payload) VALUES (%s, %s, 'publication_compensated', 'worker', %s, %s)",
            (revision.entry_id, revision.id, reason, Json({"generation": generation})),
        )
    invalidate_cache()
    return PublicationResult(attempt_id, revision.id, "compensated", generation)


def publish_revision(
    revision_id: int,
    run_id: str,
    *,
    invalidate_cache: CacheInvalidator = lambda: None,
    smoke: Callable[[Revision], tuple[bool, str]] = _smoke,
    fault: FaultHook | None = None,
) -> PublicationResult:
    """Authorize and atomically activate one exact validated revision."""
    revision = _revision(revision_id)
    with _connect() as conn:
        completed = conn.execute(
            "SELECT id, committed_generation FROM curation_publication_attempts"
            " WHERE revision_id = %s AND validation_run_id = %s AND status = 'smoke_passed'",
            (revision.id, run_id),
        ).fetchone()
    if completed is not None:
        return PublicationResult(
            str(completed[0]), revision.id, "active", completed[1], idempotent=True
        )
    fingerprint = validation_fingerprint(revision)
    prepared = prepare_chunks(revision_chunks(revision))
    attempt_id = str(uuid4())
    committed_generation: str | None = None
    try:
        with _connect() as conn:
            acquire_kb_write_lock(conn)
            if fault:
                fault("after_lock")
            existing = conn.execute(
                "SELECT id, status, committed_generation FROM curation_publication_attempts"
                " WHERE revision_id = %s AND validation_run_id = %s FOR UPDATE",
                (revision.id, run_id),
            ).fetchone()
            if existing is not None:
                if existing[1] == "smoke_passed":
                    return PublicationResult(
                        str(existing[0]), revision.id, "active", existing[2], idempotent=True
                    )
                raise PublicationError(
                    f"publication attempt already exists with status {existing[1]!r}"
                )
            _assert_authorized(conn, revision, run_id, fingerprint)
            active = conn.execute(
                "SELECT active_revision_id FROM curated_entries WHERE id = %s FOR UPDATE",
                (revision.entry_id,),
            ).fetchone()
            if active is None:
                raise PublicationError("curated entry does not exist")
            latest = conn.execute(
                "SELECT id FROM curated_revisions WHERE entry_id = %s"
                " ORDER BY revision_number DESC LIMIT 1",
                (revision.entry_id,),
            ).fetchone()
            if latest is None or int(latest[0]) != revision.id:
                raise PublicationError(
                    "a newer successor revision exists; the older reviewed revision cannot publish"
                )
            prior_id = int(active[0]) if active[0] is not None else None
            conn.execute(
                "INSERT INTO curation_publication_attempts"
                " (id, revision_id, validation_run_id, fingerprint, prior_revision_id, status)"
                " VALUES (%s, %s, %s, %s, %s, 'intent')",
                (attempt_id, revision.id, run_id, fingerprint, prior_id),
            )
            conn.execute(
                "UPDATE curation_revision_state SET state = 'publishing',"
                " reason = 'Atomic publication transaction is running',"
                " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
                (revision.id,),
            )
            replace_prepared_chunks(conn, f"curated-{revision.entry_id}-", prepared)
            conn.execute(
                "UPDATE curated_entries SET active_revision_id = %s, retired_at = NULL WHERE id = %s",
                (revision.id, revision.entry_id),
            )
            if prior_id is not None and prior_id != revision.id:
                conn.execute(
                    "UPDATE curation_revision_state SET state = 'retired',"
                    " reason = 'Replaced by a validated successor',"
                    " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
                    (prior_id,),
                )
            conn.execute(
                "UPDATE curation_revision_state SET state = 'active',"
                " reason = 'Published; post-commit smoke pending',"
                " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
                (revision.id,),
            )
            _project_legacy(conn, revision, revision.entry_id)
            committed_generation = refresh_generation(conn)
            conn.execute(
                "UPDATE curation_publication_attempts SET status = 'committed',"
                " committed_generation = %s, committed_at = now() WHERE id = %s",
                (committed_generation, attempt_id),
            )
            conn.execute(
                "INSERT INTO curation_events (entry_id, revision_id, validation_run_id,"
                " event_type, actor_type, reason, payload) VALUES (%s, %s, %s,"
                " 'publication_committed', 'admin', 'Validated revision activated', %s)",
                (
                    revision.entry_id,
                    revision.id,
                    run_id,
                    Json({"attempt_id": attempt_id, "generation": committed_generation}),
                ),
            )
            conn.execute(
                "INSERT INTO curation_outbox (event_type, aggregate_id, payload)"
                " VALUES ('publication_committed', %s, %s)",
                (attempt_id, Json({"attempt_id": attempt_id})),
            )
            if fault:
                fault("before_commit")
        if fault:
            fault("after_commit")
    except PublicationError as exc:
        if str(exc).startswith("stale_validation"):
            try:
                start_validation(revision.id)
            except ValueError:
                pass
        raise
    except Exception as exc:
        # If commit did not land, this leaves the validated revision blocked and
        # auditable. If it did land, the durable attempt drives compensation below.
        with _connect() as conn:
            attempt = conn.execute(
                "SELECT status FROM curation_publication_attempts WHERE id = %s", (attempt_id,)
            ).fetchone()
        if attempt is None:
            _record_precommit_failure(revision, run_id, attempt_id, fingerprint, exc)
            raise PublicationError(f"publication failed before commit: {exc}") from exc
        compensated = compensate_publication(
            attempt_id, f"post-commit execution failed: {exc}", invalidate_cache=invalidate_cache
        )
        raise PublicationError(
            f"publication committed but was {compensated.status}: {exc}"
        ) from exc

    invalidate_cache()
    try:
        if fault:
            fault("before_smoke")
        passed, smoke_detail = smoke(revision)
    except Exception as exc:  # smoke failures must always enter compensation
        passed, smoke_detail = False, f"smoke execution failed: {exc}"
    if not passed:
        with _connect() as conn:
            conn.execute(
                "UPDATE curation_publication_attempts SET status = 'smoke_failed',"
                " error_code = 'smoke_failed', error_detail = %s WHERE id = %s",
                (smoke_detail, attempt_id),
            )
        compensated = compensate_publication(
            attempt_id, smoke_detail, invalidate_cache=invalidate_cache
        )
        raise PublicationError(f"post-publication smoke failed; {compensated.status}")
    with _connect() as conn:
        conn.execute(
            "UPDATE curation_publication_attempts SET status = 'smoke_passed',"
            " completed_at = now() WHERE id = %s",
            (attempt_id,),
        )
        conn.execute(
            "UPDATE curation_revision_state SET reason = 'Published and serving smoke passed',"
            " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
            (revision.id,),
        )
        conn.execute(
            "INSERT INTO curation_events (entry_id, revision_id, validation_run_id,"
            " event_type, actor_type, reason) VALUES (%s, %s, %s,"
            " 'publication_smoke_passed', 'worker', %s)",
            (revision.entry_id, revision.id, run_id, smoke_detail),
        )
    for feedback_id in revision.linked_feedback_ids:
        resolve_interaction(feedback_id)
    return PublicationResult(attempt_id, revision.id, "active", committed_generation)


def retire_entry(
    entry_id: int,
    reason: str,
    *,
    invalidate_cache: CacheInvalidator = lambda: None,
) -> str:
    """Atomically remove an active entry without depending on workflow availability."""
    if not reason.strip():
        raise PublicationError("retirement reason is required")
    with _connect() as conn:
        acquire_kb_write_lock(conn)
        row = conn.execute(
            "SELECT active_revision_id FROM curated_entries WHERE id = %s FOR UPDATE",
            (entry_id,),
        ).fetchone()
        if row is None:
            raise PublicationError("curated entry does not exist")
        if row[0] is None:
            raise PublicationError("curated entry is already retired")
        revision_id = int(row[0])
        replace_prepared_chunks(conn, f"curated-{entry_id}-", [])
        conn.execute(
            "UPDATE curated_entries SET active_revision_id = NULL, retired_at = now() WHERE id = %s",
            (entry_id,),
        )
        conn.execute(
            "UPDATE curation_revision_state SET state = 'retired', reason = %s,"
            " state_version = state_version + 1, updated_at = now() WHERE revision_id = %s",
            (reason.strip(), revision_id),
        )
        _project_legacy(conn, None, entry_id)
        generation = refresh_generation(conn)
        conn.execute(
            "INSERT INTO curation_events (entry_id, revision_id, event_type, actor_type,"
            " reason, payload) VALUES (%s, %s, 'entry_retired', 'admin', %s, %s)",
            (entry_id, revision_id, reason.strip(), Json({"generation": generation})),
        )
    invalidate_cache()
    return generation


def recover_committed_publications(
    *, invalidate_cache: CacheInvalidator = lambda: None
) -> list[str]:
    """Compensate attempts left committed after a process crash before smoke completion."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id FROM curation_publication_attempts WHERE status IN ('committed', 'smoke_failed')"
            " ORDER BY committed_at"
        ).fetchall()
    recovered: list[str] = []
    for row in rows:
        result = compensate_publication(
            str(row[0]), "recovered incomplete post-commit smoke", invalidate_cache=invalidate_cache
        )
        recovered.append(result.status)
    return recovered
