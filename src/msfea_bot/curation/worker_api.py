"""Private worker API used only by the n8n publication-guard workflow."""

from __future__ import annotations

import asyncio
import hmac
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from msfea_bot.config import settings
from msfea_bot.curation.coordination import dispatch_once, invalidate_app_cache, reconcile
from msfea_bot.curation.migrations import migrate
from msfea_bot.curation.publication import (
    PublicationError,
    execute_publication_intent,
    recover_committed_publications,
)
from msfea_bot.curation.validation import REQUIRED_STEPS, execute_step_idempotent

_LOG = logging.getLogger(__name__)


def require_worker_token(x_curation_worker_token: str = Header(default="")) -> None:
    if not settings.curation_worker_token:
        raise HTTPException(status_code=503, detail="worker token is not configured")
    if not hmac.compare_digest(x_curation_worker_token, settings.curation_worker_token):
        raise HTTPException(status_code=401, detail="invalid worker token")


async def _coordination_loop() -> None:
    ticks = 0
    while True:
        try:
            delivered = await asyncio.to_thread(dispatch_once)
            ticks += 1
            if ticks % 15 == 0:
                await asyncio.to_thread(reconcile)
            await asyncio.sleep(0.25 if delivered else 2.0)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # durable state makes retry after logging safe
            _LOG.error("curation_coordination_failure type=%s", type(exc).__name__)
            await asyncio.sleep(5.0)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    migrate()
    reconcile()
    coordination_enabled = bool(
        settings.curation_worker_token and settings.n8n_webhook_secret
    )
    if coordination_enabled:
        try:
            recover_committed_publications(invalidate_cache=invalidate_app_cache)
        except Exception as exc:  # reconciliation loop/operator can retry safely
            _LOG.error("publication_recovery_failure type=%s", type(exc).__name__)
    task = asyncio.create_task(_coordination_loop()) if coordination_enabled else None
    try:
        yield
    finally:
        if task is not None:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task


app = FastAPI(title="MSFEA Curation Worker", lifespan=lifespan)


class ValidationStepRequest(BaseModel):
    run_id: str = Field(min_length=1, max_length=64)
    step: str = Field(min_length=1, max_length=64)


@app.get("/internal/health")
def health(_: None = Depends(require_worker_token)) -> dict[str, str]:
    if not settings.n8n_webhook_secret:
        raise HTTPException(status_code=503, detail="n8n webhook secret is not configured")
    return {"status": "ok"}


@app.post("/internal/validation/execute")
def execute_validation(
    request: ValidationStepRequest,
    _: None = Depends(require_worker_token),
    x_idempotency_key: str = Header(default=""),
    x_workflow_execution_id: str = Header(default=""),
) -> dict[str, object]:
    if request.step not in REQUIRED_STEPS:
        raise HTTPException(status_code=422, detail="unknown validation step")
    try:
        result = execute_step_idempotent(
            request.run_id,
            request.step,
            x_idempotency_key,
            x_workflow_execution_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if result["status"] != "passed":
        raise HTTPException(status_code=409, detail=f"validation failed: {request.step}")
    return result


class PublicationIntentRequest(BaseModel):
    attempt_id: str = Field(min_length=1, max_length=64)


@app.post("/internal/publication/execute")
def execute_publication(
    request: PublicationIntentRequest,
    _: None = Depends(require_worker_token),
    x_idempotency_key: str = Header(default=""),
    x_workflow_execution_id: str = Header(default=""),
) -> dict[str, object]:
    if x_idempotency_key != f"publication:{request.attempt_id}":
        raise HTTPException(status_code=409, detail="publication idempotency key mismatch")
    with psycopg.connect(
        settings.database_url, autocommit=True, connect_timeout=5
    ) as conn:
        conn.execute(
            "UPDATE curation_publication_attempts SET workflow_execution_id = %s"
            " WHERE id = %s AND (workflow_execution_id IS NULL OR workflow_execution_id = %s)",
            (x_workflow_execution_id or None, request.attempt_id, x_workflow_execution_id or None),
        )
    try:
        result = execute_publication_intent(
            request.attempt_id, invalidate_cache=invalidate_app_cache
        )
    except PublicationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "attempt_id": result.attempt_id,
        "revision_id": result.revision_id,
        "status": result.status,
        "generation": result.generation,
        "idempotent": result.idempotent,
    }
