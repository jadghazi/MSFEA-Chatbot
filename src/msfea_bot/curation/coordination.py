"""Durable n8n outbox dispatch, reconciliation, and fixed internal callbacks."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import psycopg
from psycopg.types.json import Json

from msfea_bot.config import settings

UrlOpen = Callable[..., Any]
_ROUTES = {
    "validation_requested": "/webhook/kb-validation",
    "publication_requested": "/webhook/kb-publication",
}


def _connect() -> Any:
    return psycopg.connect(settings.database_url, autocommit=False, connect_timeout=5)


def _require_coordination_secrets() -> None:
    if not settings.curation_worker_token or not settings.n8n_webhook_secret:
        raise RuntimeError("curation worker and n8n webhook secrets must be configured")


def dispatch_once(opener: UrlOpen = urlopen) -> bool:
    """Lease and deliver one fixed-destination outbox event."""
    _require_coordination_secrets()
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, event_type, aggregate_id, payload, attempts"
            " FROM curation_outbox WHERE status IN ('pending', 'failed')"
            " AND available_at <= now() AND attempts < %s"
            " ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1",
            (settings.curation_outbox_max_attempts,),
        ).fetchone()
        if row is None:
            return False
        event_id = int(row[0])
        event_type = str(row[1])
        route = _ROUTES.get(event_type)
        if route is None:
            conn.execute(
                "UPDATE curation_outbox SET status = 'failed', attempts = attempts + 1,"
                " last_error = 'unsupported_event_type', available_at = 'infinity'"
                " WHERE id = %s",
                (event_id,),
            )
            return True
        attempts = int(row[4]) + 1
        conn.execute(
            "UPDATE curation_outbox SET status = 'delivering', attempts = %s,"
            " lease_expires_at = now() + interval '2 minutes', last_error = NULL"
            " WHERE id = %s",
            (attempts, event_id),
        )
    body = json.dumps(
        {
            "event_id": event_id,
            "event_type": event_type,
            "aggregate_id": str(row[2]),
            **dict(row[3]),
        },
        separators=(",", ":"),
    ).encode()
    request = Request(
        settings.n8n_base_url.rstrip("/") + route,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Secret": settings.n8n_webhook_secret,
            "X-Idempotency-Key": f"outbox:{event_id}",
        },
    )
    error: str | None = None
    try:
        with opener(request, timeout=10) as response:
            if not 200 <= int(response.status) < 300:
                error = f"http_{response.status}"
    except HTTPError as exc:
        error = f"http_{exc.code}"
    except (URLError, TimeoutError, OSError) as exc:
        error = type(exc).__name__
    with _connect() as conn:
        if error is None:
            conn.execute(
                "UPDATE curation_outbox SET status = 'delivered', delivered_at = now(),"
                " lease_expires_at = NULL WHERE id = %s AND status = 'delivering'",
                (event_id,),
            )
        else:
            delay = min(300, 2**attempts)
            conn.execute(
                "UPDATE curation_outbox SET status = 'failed', lease_expires_at = NULL,"
                " available_at = now() + (%s * interval '1 second'), last_error = %s"
                " WHERE id = %s AND status = 'delivering'",
                (delay, error, event_id),
            )
    return True


def reconcile() -> dict[str, int]:
    """Recover expired leases and fail closed on abandoned validation runs."""
    with _connect() as conn:
        # A webhook acknowledges receipt before n8n finishes. If the execution
        # disappears, replay the same IDs; worker endpoints are idempotent.
        conn.execute(
            "UPDATE curation_outbox o SET status = 'failed', available_at = now(),"
            " last_error = 'uncompleted_workflow', delivered_at = NULL"
            " WHERE o.status = 'delivered' AND o.attempts < %s"
            " AND o.delivered_at < now() - interval '20 minutes'"
            " AND ((o.event_type = 'validation_requested' AND EXISTS ("
            "   SELECT 1 FROM curation_validation_runs r"
            "   WHERE r.id = o.aggregate_id AND r.status IN ('pending', 'running')"
            " )) OR (o.event_type = 'publication_requested' AND EXISTS ("
            "   SELECT 1 FROM curation_publication_attempts a"
            "   WHERE a.id = o.aggregate_id AND a.status = 'intent'"
            " )))",
            (settings.curation_outbox_max_attempts,),
        )
        outbox = conn.execute(
            "UPDATE curation_outbox SET status = 'failed', lease_expires_at = NULL,"
            " available_at = now(), last_error = 'expired_delivery_lease'"
            " WHERE status = 'delivering' AND lease_expires_at < now()"
        ).rowcount
        retry_jobs = conn.execute(
            "UPDATE curation_jobs SET status = 'pending', lease_expires_at = NULL,"
            " available_at = now(), last_error = 'expired_worker_lease', updated_at = now()"
            " WHERE status = 'leased' AND lease_expires_at < now() AND attempts < 3"
        ).rowcount
        timed_jobs = conn.execute(
            "UPDATE curation_jobs SET status = 'timed_out', lease_expires_at = NULL,"
            " last_error = 'retry_budget_exhausted', updated_at = now()"
            " WHERE status = 'leased' AND lease_expires_at < now() AND attempts >= 3"
            " RETURNING validation_run_id, step"
        ).fetchall()
        for run_id, step in timed_jobs:
            conn.execute(
                "INSERT INTO curation_validation_results"
                " (run_id, step, status, details, started_at, completed_at)"
                " VALUES (%s, %s, 'timed_out', %s, now(), now())"
                " ON CONFLICT (run_id, step) DO NOTHING",
                (run_id, step, Json({"error": "worker retry budget exhausted"})),
            )
            revision = conn.execute(
                "UPDATE curation_validation_runs SET status = 'timed_out',"
                " error_code = 'worker_retry_exhausted', completed_at = now()"
                " WHERE id = %s RETURNING revision_id",
                (run_id,),
            ).fetchone()
            if revision:
                conn.execute(
                    "UPDATE curation_revision_state SET state = 'blocked',"
                    " reason = 'Validation worker retry budget exhausted',"
                    " state_version = state_version + 1, updated_at = now()"
                    " WHERE revision_id = %s",
                    (revision[0],),
                )
                conn.execute(
                    "UPDATE curation_jobs SET status = 'cancelled', updated_at = now()"
                    " WHERE validation_run_id = %s AND status = 'pending'",
                    (run_id,),
                )
        cutoff = datetime.now(timezone.utc).timestamp() - (
            settings.curation_validation_timeout_minutes * 60
        )
        abandoned = conn.execute(
            "SELECT id, revision_id FROM curation_validation_runs"
            " WHERE status IN ('pending', 'running') AND extract(epoch FROM created_at) < %s"
            " FOR UPDATE",
            (cutoff,),
        ).fetchall()
        for run_id, revision_id in abandoned:
            conn.execute(
                "UPDATE curation_validation_runs SET status = 'timed_out',"
                " error_code = 'validation_timeout', completed_at = now() WHERE id = %s",
                (run_id,),
            )
            conn.execute(
                "UPDATE curation_jobs SET status = 'timed_out', updated_at = now()"
                " WHERE validation_run_id = %s AND status IN ('pending', 'leased')",
                (run_id,),
            )
            conn.execute(
                "UPDATE curation_revision_state SET state = 'blocked',"
                " reason = 'Validation workflow timed out',"
                " state_version = state_version + 1, updated_at = now()"
                " WHERE revision_id = %s",
                (revision_id,),
            )
        expired_intents = conn.execute(
            "UPDATE curation_publication_attempts SET status = 'failed_precommit',"
            " error_code = 'publication_timeout',"
            " error_detail = 'Publication workflow did not complete before deadline',"
            " completed_at = now()"
            " WHERE status = 'intent' AND created_at < now() -"
            " (%s * interval '1 minute') RETURNING id, revision_id, validation_run_id",
            (settings.curation_publication_timeout_minutes,),
        ).fetchall()
        for attempt_id, revision_id, run_id in expired_intents:
            conn.execute(
                "UPDATE curation_revision_state SET state = 'blocked',"
                " reason = 'Publication workflow timed out before activation',"
                " state_version = state_version + 1, updated_at = now()"
                " WHERE revision_id = %s AND state = 'publishing'",
                (revision_id,),
            )
            conn.execute(
                "INSERT INTO curation_events (entry_id, revision_id, validation_run_id,"
                " event_type, actor_type, reason, payload)"
                " SELECT entry_id, %s, %s, 'publication_timed_out', 'worker',"
                " 'No student-serving activation occurred', %s"
                " FROM curated_revisions WHERE id = %s",
                (revision_id, run_id, Json({"attempt_id": attempt_id}), revision_id),
            )
    return {
        "outbox_leases": int(outbox),
        "retry_jobs": int(retry_jobs),
        "timed_out_jobs": len(timed_jobs),
        "abandoned_runs": len(abandoned),
        "expired_publication_intents": len(expired_intents),
    }


def invalidate_app_cache(opener: UrlOpen = urlopen) -> None:
    """Notify the serving process after worker-side publication or compensation."""
    if not settings.curation_worker_token:
        raise RuntimeError("CURATION_WORKER_TOKEN is required")
    request = Request(
        settings.app_internal_url.rstrip("/") + "/internal/cache/invalidate",
        data=b"{}",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Curation-Worker-Token": settings.curation_worker_token,
        },
    )
    with opener(request, timeout=10) as response:
        if not 200 <= int(response.status) < 300:
            raise RuntimeError(f"cache invalidation callback returned HTTP {response.status}")
