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
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from msfea_bot import departments
from msfea_bot.api.security import RateLimiter, sanitize
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_limiter = RateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)
_experience_limiter = RateLimiter(max_requests=5, window_seconds=3600)


def _client_key(request: Request) -> str:
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(request: Request) -> None:
    """Per-client rate-limit dependency; raises 429 when the limit is exceeded."""
    if not _limiter.allow(_client_key(request)):
        raise HTTPException(
            status_code=429,
            detail="Too many requests — please slow down and try again shortly.",
        )


def experience_rate_limit(request: Request) -> None:
    """A separate low-volume abuse bucket; client keys are never persisted."""
    if not _experience_limiter.allow(_client_key(request)):
        raise HTTPException(status_code=429, detail="Feedback limit reached. Please try again later.")


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_HISTORY_MESSAGE_CHARS)


class ChatRequest(BaseModel):
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
            "The assistant has reached its current usage limit. Please try again in "
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


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, _rl: None = Depends(rate_limit)) -> ChatResponse:
    """Answer a question via the guarded bot; degrade gracefully on backend errors."""
    # Sanitize, then anonymize once; use the same text for the LLM and the log
    # (CLAUDE.md §7).
    question = anonymize(sanitize(req.question))
    history = [
        ConversationMessage(message.role, cleaned)
        for message in req.history
        if (cleaned := anonymize(sanitize(message.content)))
    ]
    # Normalised here so an unknown value is dropped once, at the edge, rather than
    # being passed down and re-validated in retrieval, generation and logging.
    dept = departments.from_code(req.department)
    dept_code = dept.code if dept else None

    if not question:
        result = Answer(
            text="Please type a question about internships or CDC programs.",
            citations=[],
            refused=True,
        )
    else:
        try:
            result = generate_answer(question, department=dept_code, history=history)
        except LLMRateLimitError:
            result = _temporary_failure("rate_limited", dept_code)
        except LLMConfigurationError:
            result = _temporary_failure("configuration_error", dept_code)
        except LLMServiceError:
            result = _temporary_failure("service_unavailable", dept_code)
        except Exception:  # noqa: BLE001 - never expose an internal 500 to a student
            result = _temporary_failure("service_unavailable", dept_code)

    interaction_id = log_interaction(question, result)  # fail-safe; never breaks the response

    return ChatResponse(
        answer=result.text,
        citations=result.citations,
        refused=result.refused,
        disclaimer=result.disclaimer,
        interaction_id=interaction_id,
        error_code=result.error_code,
    )


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
        raise HTTPException(status_code=503, detail="Feedback could not be saved. Please try again.")
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
    return {"ok": edit_curated_answer(req.id, req.question, req.answer)}


class RetireCuratedRequest(BaseModel):
    id: int


@app.post("/admin/api/curated/retire")
def admin_curated_retire(
    req: RetireCuratedRequest, _: None = Depends(require_admin)
) -> dict[str, bool]:
    """Retire a published answer so the bot stops using it (row kept for history)."""
    return {"ok": retire_curated_answer(req.id)}


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
