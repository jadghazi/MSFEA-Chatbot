"""FastAPI application — the thin backend the widget calls (CLAUDE.md §5.7).

Endpoints:
- GET  /health  — liveness check.
- POST /chat    — answer a student question through the guarded RAG pipeline.

The standalone pilot frontend is served at /, while the reusable widget assets
remain under /widget for a future AUB-page embed. CORS can allow that embedded
widget to call the API from an explicitly configured origin.
"""

from __future__ import annotations

import hmac
import json
import logging
from time import perf_counter
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, cast

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from msfea_bot import departments
from msfea_bot.api.security import RateLimiter, sanitize
from msfea_bot.api.abuse import BodyLimitMiddleware, RequestGuard, fingerprint, local_reply
from msfea_bot.observability.usage import count, snapshot
from msfea_bot.config import settings
from msfea_bot.curation.service import (
    edit_curated_answer,
    publish_curated_answer,
    retire_curated_answer,
)
from msfea_bot.curation.store import list_curated
from msfea_bot.generation import generate_answer
from msfea_bot.generation.answer import Answer
from msfea_bot.generation.conversation import (
    MAX_HISTORY_MESSAGES,
    MAX_HISTORY_MESSAGE_CHARS,
    ConversationMessage,
    frame_confirmation,
    is_contextual_followup,
)
from msfea_bot.experience import (
    ALLOWED_TAGS,
    initialize_schema as initialize_experience_schema,
    save_feedback as save_experience_feedback,
    summary as experience_summary,
)
from msfea_bot.ingestion.embeddings import warm_embedding_model
from msfea_bot.llm import LLMConfigurationError, LLMRateLimitError, LLMServiceError
from msfea_bot.observability.privacy import anonymize, warm_anonymizer
from msfea_bot.observability.store import (
    feedback_items,
    initialize_schema as initialize_observability_schema,
    log_interaction,
    resolve_by_question,
    resolve_interaction,
    set_rating,
    stats,
)
from msfea_bot.retrieval.store import (
    index_is_ready,
    initialize_schema as initialize_retrieval_schema,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Initialize storage and local inference before accepting pilot traffic."""
    if settings.warm_models_on_startup:
        warm_embedding_model()
        warm_anonymizer()
    initialize_retrieval_schema()
    initialize_observability_schema()
    initialize_experience_schema()
    yield


app = FastAPI(title="MSFEA CDC Chatbot API", lifespan=lifespan)

app.add_middleware(BodyLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_limiter = RateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)
_burst_limiter = RateLimiter(12, 5)
_hour_limiter = RateLimiter(300, 3600)
_session_limiter = RateLimiter(20, 60)
_session_hour_limiter = RateLimiter(80, 3600)
_guard = RequestGuard()
_experience_limiter = RateLimiter(max_requests=5, window_seconds=3600)


def _client_key(request: Request) -> str:
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(request: Request) -> None:
    """Per-client rate-limit dependency; raises 429 when the limit is exceeded."""
    key = _client_key(request)
    if not all(limiter.allow(key) for limiter in (_limiter, _burst_limiter, _hour_limiter)):
        count("rate_limit_hits")
        raise HTTPException(
            status_code=429,
            detail="Too many requests — please slow down and try again shortly.",
            headers={"Retry-After": "60"},
        )


def experience_rate_limit(request: Request) -> None:
    """A separate low-volume abuse bucket; client keys are never persisted."""
    if not _experience_limiter.allow(_client_key(request)):
        raise HTTPException(
            status_code=429, detail="Feedback limit reached. Please try again later."
        )


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_HISTORY_MESSAGE_CHARS)


class ChatRequest(BaseModel):
    session_id: str | None = Field(
        default=None, min_length=16, max_length=64, pattern=r"^[A-Za-z0-9_-]+$"
    )
    question: str = Field(min_length=1, max_length=2000)
    # Optional so existing embeds keep working. Untrusted: `departments.from_code`
    # ignores anything not on the known list, so a bad value degrades to an
    # unscoped answer rather than an error (ADR-0015).
    department: str | None = Field(default=None, max_length=32)
    # Ephemeral and client-owned: never assigned a server-side conversation id or
    # persisted as a profile. The hard bound controls latency/token use (ADR-0018).
    history: list[HistoryMessage] = Field(default_factory=list, max_length=MAX_HISTORY_MESSAGES)


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    refused: bool
    disclaimer: str
    interaction_id: int | None = None
    error_code: str | None = None
    local: bool = False


def _temporary_failure(code: str, department: str | None) -> Answer:
    """Student-safe operational failure, distinct from a missing-KB refusal."""
    dept = departments.from_code(department)
    contact = (
        f"{dept.contact_name} ({dept.contact_email})"
        if dept
        else settings.escalation_contact or "the CDC office"
    )
    if code == "rate_limited":
        text = (
            "The assistant is temporarily busy. Please try again in "
            f"a few minutes. If it is still unavailable later today, contact {contact}."
        )
    else:
        text = f"The assistant is temporarily unavailable. Please try again or contact {contact}."
    return Answer(text=text, citations=[], refused=True, disclaimer="", error_code=code)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check — confirms the API is up."""
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Confirm that the populated KB matches this container's embedding model."""
    try:
        if not index_is_ready():
            raise HTTPException(status_code=503, detail="Knowledge base is not ready.")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Knowledge base is not ready.") from exc
    return {"status": "ready"}


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Do not echo invalid inputs (potential PII or enormous values) in errors.
    count("validation_hits")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Please send a question of 1–2,000 characters with at most four recent "
            "messages of up to 1,200 characters each."
            if request.url.path == "/chat"
            else "Please check the submitted fields."
        },
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request, _rl: None = Depends(rate_limit)) -> ChatResponse:
    """Gate locally before NER, embeddings, database work or generation."""
    started = perf_counter()
    ip = _client_key(request)
    session = fingerprint(ip + ":" + req.session_id) if req.session_id else None
    if session and not all(
        limiter.allow(session) for limiter in (_session_limiter, _session_hour_limiter)
    ):
        count("rate_limit_hits")
        raise HTTPException(
            429, "Please slow down and try again shortly.", headers={"Retry-After": "60"}
        )
    question = sanitize(req.question)
    reply = local_reply(question, has_history=bool(req.history))
    if reply:
        count("local_replies")
        return ChatResponse(
            answer=reply,
            citations=[],
            refused=False,
            disclaimer=Answer(text="").disclaimer,
            local=True,
        )

    dept = departments.from_code(req.department)
    dept_code = dept.code if dept else None
    # Exact sanitized context: do not normalize away punctuation or user facts.
    prior = [ConversationMessage(m.role, sanitize(m.content)) for m in req.history]
    needs_history = (
        is_contextual_followup(question, prior) or frame_confirmation(question, prior) != question
    )
    effective_history = prior if needs_history else []
    key = fingerprint(
        json.dumps(
            [
                _guard.version,
                ip,
                session,
                question,
                dept_code,
                [(m.role, m.content) for m in effective_history],
            ]
        )
    )
    cached = _guard.begin(ip, session, key)
    if cached is not None:
        return cast(ChatResponse, cached).model_copy(deep=True)
    response = None
    try:
        question = anonymize(question)
        history = [
            ConversationMessage(message.role, cleaned)
            for message in req.history
            if (cleaned := anonymize(sanitize(message.content)))
        ]
        try:
            result = generate_answer(question, department=dept_code, history=history)
        except LLMRateLimitError:
            result = _temporary_failure("rate_limited", dept_code)
        except LLMConfigurationError:
            result = _temporary_failure("configuration_error", dept_code)
        except LLMServiceError:
            result = _temporary_failure("service_unavailable", dept_code)
        except Exception as exc:  # noqa: BLE001 - never expose backend details
            count("backend_errors")
            logging.getLogger(__name__).error("chat_backend_failure type=%s", type(exc).__name__)
            result = _temporary_failure("service_unavailable", dept_code)
        interaction_id = log_interaction(question, result)
        response = ChatResponse(
            answer=result.text,
            citations=result.citations,
            refused=result.refused,
            disclaimer=result.disclaimer,
            interaction_id=interaction_id,
            error_code=result.error_code,
        )
        return response
    finally:
        # Retry must make a fresh attempt after a transient failure. Quota failures
        # retain the cooldown; existing rate/concurrency limits still bound retries.
        cacheable = response if response and response.error_code != "service_unavailable" else None
        _guard.finish(ip, session, key, cacheable)
        count("chat_processing_ms", round((perf_counter() - started) * 1000))


class RateRequest(BaseModel):
    interaction_id: int
    rating: int  # +1 (helpful) or -1 (not helpful)
    reason: str | None = Field(default=None, max_length=64)


@app.post("/rate")
def rate(req: RateRequest, _rl: None = Depends(rate_limit)) -> dict[str, bool]:
    """Record a student's thumbs up/down on an answer."""
    if req.rating not in (1, -1):
        raise HTTPException(status_code=422, detail="rating must be +1 or -1")
    allowed_reasons = {"Incorrect", "Unclear", "Missing information", "Wrong department"}
    if req.reason is not None and (req.rating != -1 or req.reason not in allowed_reasons):
        raise HTTPException(status_code=422, detail="invalid reason for this rating")
    return {"ok": set_rating(req.interaction_id, req.rating, req.reason)}


class ExperienceFeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: int = Field(ge=1, le=5)
    tags: list[str] = Field(default_factory=list, max_length=len(ALLOWED_TAGS))
    comment: str | None = Field(default=None, max_length=500)


@app.post("/experience-feedback", status_code=201)
def experience_feedback(
    req: ExperienceFeedbackRequest, _rl: None = Depends(experience_rate_limit)
) -> dict[str, bool]:
    """Store anonymous overall feedback without chat or client identifiers."""
    if len(set(req.tags)) != len(req.tags) or any(tag not in ALLOWED_TAGS for tag in req.tags):
        raise HTTPException(status_code=422, detail="one or more feedback tags are invalid")
    comment = req.comment.strip() if req.comment else None
    if not save_experience_feedback(req.rating, req.tags, comment):
        raise HTTPException(
            status_code=503, detail="Feedback could not be saved. Please try again."
        )
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Admin (dashboard) — protected by a shared token (ADR-0010). Not a user system.
# --------------------------------------------------------------------------- #


def require_admin(authorization: str = Header(default="")) -> None:
    """Guard admin endpoints with the ADMIN_TOKEN (constant-time comparison)."""
    if not settings.admin_token:
        raise HTTPException(status_code=403, detail="Admin is disabled (no ADMIN_TOKEN set).")
    if not hmac.compare_digest(authorization, f"Bearer {settings.admin_token}"):
        raise HTTPException(status_code=401, detail="Invalid admin token.")


class FeedbackOut(BaseModel):
    id: int
    ts: str
    question: str
    answer: str
    refused: bool
    rating: int | None
    rating_reason: str | None
    retrieved: list[str]


@app.get("/admin/api/stats")
def admin_stats(_: None = Depends(require_admin)) -> dict[str, int]:
    return stats()


@app.get("/admin/api/usage")
def admin_usage(_: None = Depends(require_admin)) -> dict[str, int]:
    """Content-free operational counters for this worker since startup."""
    return snapshot()


@app.get("/admin/api/feedback")
def admin_feedback(_: None = Depends(require_admin)) -> list[FeedbackOut]:
    """Questions needing attention: the bot refused, or a student thumbs-downed."""
    return [
        FeedbackOut(
            id=f.id,
            ts=f.ts.isoformat(),
            question=f.question,
            answer=f.answer,
            refused=f.refused,
            rating=f.rating,
            rating_reason=f.rating_reason,
            retrieved=f.retrieved,
        )
        for f in feedback_items()
    ]


class ExperienceCommentOut(BaseModel):
    ts: str
    rating: int
    comment: str


class ExperienceSummaryOut(BaseModel):
    total: int
    average_rating: float | None
    rating_distribution: dict[str, int]
    tag_counts: dict[str, int]
    recent_comments: list[ExperienceCommentOut]


@app.get("/admin/api/experience-feedback", response_model=ExperienceSummaryOut)
def admin_experience_feedback(_: None = Depends(require_admin)) -> ExperienceSummaryOut:
    data = experience_summary()
    return ExperienceSummaryOut(
        total=data["total"],
        average_rating=data["average_rating"],
        rating_distribution=data["rating_distribution"],
        tag_counts=data["tag_counts"],
        recent_comments=[
            ExperienceCommentOut(ts=item.ts.isoformat(), rating=item.rating, comment=item.comment)
            for item in data["recent_comments"]
        ],
    )


class CurateRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    answer: str = Field(min_length=1, max_length=8000)


@app.post("/admin/api/curate")
def admin_curate(req: CurateRequest, _: None = Depends(require_admin)) -> dict[str, int]:
    """Publish an admin-written answer into the KB (indexed immediately).

    Publishing also clears the queue: any open feedback item asking this exact
    question is marked resolved, so it stops re-appearing after a refresh.
    """
    curated_id = publish_curated_answer(req.question, req.answer, author="admin")
    _guard.invalidate()
    resolved = resolve_by_question(req.question)
    return {"curated_id": curated_id, "resolved": resolved}


class CuratedOut(BaseModel):
    id: int
    question: str
    answer: str
    author: str
    created_at: str


@app.get("/admin/api/curated")
def admin_curated(_: None = Depends(require_admin)) -> list[CuratedOut]:
    """List the answers admins have published into the KB (a readable view of the
    `curated_answers` table, so staff don't need database access)."""
    return [
        CuratedOut(
            id=c.id,
            question=c.question,
            answer=c.answer,
            author=c.author,
            created_at=c.created_at.isoformat(),
        )
        for c in list_curated(active_only=True)
    ]


class EditCuratedRequest(BaseModel):
    id: int
    question: str = Field(min_length=1, max_length=2000)
    answer: str = Field(min_length=1, max_length=8000)


@app.post("/admin/api/curated/edit")
def admin_curated_edit(
    req: EditCuratedRequest, _: None = Depends(require_admin)
) -> dict[str, bool]:
    """Update a published answer's text and re-index it. False if it's gone/retired."""
    updated = edit_curated_answer(req.id, req.question, req.answer)
    if updated:
        _guard.invalidate()
    return {"ok": updated}


class RetireCuratedRequest(BaseModel):
    id: int


@app.post("/admin/api/curated/retire")
def admin_curated_retire(
    req: RetireCuratedRequest, _: None = Depends(require_admin)
) -> dict[str, bool]:
    """Retire a published answer so the bot stops using it (row kept for history)."""
    retired = retire_curated_answer(req.id)
    if retired:
        _guard.invalidate()
    return {"ok": retired}


class ResolveRequest(BaseModel):
    interaction_id: int


@app.post("/admin/api/resolve")
def admin_resolve(req: ResolveRequest, _: None = Depends(require_admin)) -> dict[str, bool]:
    """Dismiss a feedback item without publishing an answer.

    For cases that don't need new KB content (e.g. a thumbs-down on an answer
    that was actually correct). Removes it from the attention queue.
    """
    return {"ok": resolve_interaction(req.interaction_id)}


# Static frontends. Keep the root mount last so API, widget, and dashboard routes
# remain more specific; `/` is the standalone pilot product, not a demo redirect.
_ROOT = Path(__file__).resolve().parents[3]
_WIDGET_DIR = _ROOT / "widget"
if _WIDGET_DIR.is_dir():
    app.mount("/widget", StaticFiles(directory=str(_WIDGET_DIR), html=True), name="widget")
_DASHBOARD_DIR = _ROOT / "dashboard"
if _DASHBOARD_DIR.is_dir():
    app.mount("/dashboard", StaticFiles(directory=str(_DASHBOARD_DIR), html=True), name="dashboard")
_FRONTEND_DIR = _ROOT / "frontend"
if _FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")
