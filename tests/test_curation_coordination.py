"""Outbox outage, replay, and worker authorization checks on an isolated DB."""

from __future__ import annotations

from collections.abc import Iterator
from urllib.error import URLError
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from msfea_bot.config import settings
from msfea_bot.curation.coordination import dispatch_once, reconcile
from msfea_bot.curation.migrations import migrate
from msfea_bot.curation.revisions import DraftPayload, EvidenceReference, create_draft, list_revisions
from msfea_bot.curation.validation import start_validation
from msfea_bot.curation.worker_api import app as worker_app
from msfea_bot.ingestion.chunking import Chunk
from msfea_bot.retrieval.store import index_chunks, indexed_generation


def _db_available() -> bool:
    try:
        psycopg.connect(settings.database_url, connect_timeout=2).close()
        return True
    except Exception:
        return False


@pytest.fixture
def coordination_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    name = f"guard_coord_{uuid4().hex}"
    base = conninfo_to_dict(settings.database_url)
    admin_dsn = make_conninfo(**{**base, "dbname": "postgres"})
    dsn = make_conninfo(**{**base, "dbname": name})
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    try:
        monkeypatch.setattr(settings, "database_url", dsn)
        monkeypatch.setattr(settings, "curation_worker_token", "isolated-worker-token")
        monkeypatch.setattr(settings, "n8n_webhook_secret", "isolated-webhook-secret")
        migrate()
        index_chunks([Chunk("base", "Existing official policy.", "base.md", "Base")])
        yield dsn
    finally:
        with psycopg.connect(admin_dsn, autocommit=True) as conn:
            conn.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))


def _draft() -> int:
    _, revision_id = create_draft(
        DraftPayload(
            question="What is the ECE Final Report minimum?",
            answer="For ECE, the Final Report is at least five pages and 1,500 words.",
            department="ece",
            programs=("internship",),
            evidence_refs=(EvidenceReference(
                "email-clarifications.md", "Final Report requirements (ECE)",
                "at least five pages and 1,500 words",
            ),),
            representative_question="How long is the ECE report?",
            paraphrase_question="What is the ECE report length?",
            expected_evidence="at least five pages and 1,500 words",
            change_reason="Reviewed clarification.",
        )
    )
    return revision_id


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_n8n_outage_retains_work_without_changing_student_index(
    coordination_db: str,
) -> None:
    revision_id = _draft()
    generation = indexed_generation()
    run_id = start_validation(revision_id)

    def outage(*_: object, **__: object) -> None:
        raise URLError("n8n unavailable")

    assert dispatch_once(opener=outage)
    with psycopg.connect(coordination_db, autocommit=True) as conn:
        row = conn.execute(
            "SELECT status, attempts, last_error FROM curation_outbox"
            " WHERE event_type = 'validation_requested' AND aggregate_id = %s",
            (run_id,),
        ).fetchone()
        live_ids = [r[0] for r in conn.execute("SELECT id FROM chunks").fetchall()]
    assert row == ("failed", 1, "URLError")
    assert live_ids == ["base"]
    assert indexed_generation() == generation
    assert list_revisions()[0].state == "validating"

    with psycopg.connect(coordination_db, autocommit=True) as conn:
        conn.execute(
            "UPDATE curation_outbox SET available_at = now() WHERE aggregate_id = %s",
            (run_id,),
        )

    class Accepted:
        status = 200

        def __enter__(self) -> Accepted:
            return self

        def __exit__(self, *_: object) -> None:
            pass

    delivered: list[str] = []

    def accept(request: object, **_: object) -> Accepted:
        delivered.append(getattr(request, "full_url"))
        return Accepted()

    assert dispatch_once(opener=accept)
    assert delivered == [settings.n8n_base_url + "/webhook/kb-validation"]
    with psycopg.connect(coordination_db, autocommit=True) as conn:
        status = conn.execute(
            "SELECT status, attempts FROM curation_outbox WHERE aggregate_id = %s",
            (run_id,),
        ).fetchone()
    assert status == ("delivered", 2)
    assert indexed_generation() == generation


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_expired_worker_lease_requeues_then_exhausts(
    coordination_db: str,
) -> None:
    run_id = start_validation(_draft())
    with psycopg.connect(coordination_db, autocommit=True) as conn:
        conn.execute(
            "UPDATE curation_jobs SET status = 'leased', attempts = 2,"
            " lease_expires_at = now() - interval '1 minute'"
            " WHERE validation_run_id = %s AND step = 'schema_source'",
            (run_id,),
        )
    assert reconcile()["retry_jobs"] == 1
    with psycopg.connect(coordination_db, autocommit=True) as conn:
        conn.execute(
            "UPDATE curation_jobs SET status = 'leased', attempts = 3,"
            " lease_expires_at = now() - interval '1 minute'"
            " WHERE validation_run_id = %s AND step = 'schema_source'",
            (run_id,),
        )
    assert reconcile()["timed_out_jobs"] == 1
    assert list_revisions()[0].state == "blocked"


@pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")
def test_worker_requires_own_token_and_cannot_invent_publication_intent(
    coordination_db: str,
) -> None:
    client = TestClient(worker_app)
    path = "/internal/publication/execute"
    payload = {"attempt_id": str(uuid4())}
    assert client.post(path, json=payload).status_code == 401
    assert client.post(
        path, json=payload,
        headers={"X-Curation-Worker-Token": settings.curation_worker_token,
                 "X-Idempotency-Key": "wrong"},
    ).status_code == 409
    response = client.post(
        path, json=payload,
        headers={"X-Curation-Worker-Token": settings.curation_worker_token,
                 "X-Idempotency-Key": "publication:" + payload["attempt_id"]},
    )
    assert response.status_code == 409
    assert "does not exist" in response.json()["detail"]
