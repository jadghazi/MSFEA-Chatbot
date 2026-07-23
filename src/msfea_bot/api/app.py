"""FastAPI application — the thin backend the widget calls (CLAUDE.md §5.7).

Endpoints:
- GET  /health  — liveness check.
- POST /chat    — answer a student question through the guarded RAG pipeline.

The widget is served as static files under /widget for easy local demoing;
CORS is enabled so the widget can also be embedded on a different origin (the
real AUB page).
"""

from __future__ import annotations

import hmac
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from msfea_bot.api.security import RateLimiter, sanitize
from msfea_bot.config import settings
from msfea_bot.curation.service import publish_curated_answer
from msfea_bot.generation import generate_answer
from msfea_bot.generation.answer import Answer
from msfea_bot.observability.privacy import anonymize
from msfea_bot.observability.store import (
    feedback_items,
    log_interaction,
    resolve_by_question,
    resolve_interaction,
    set_rating,
    stats,
)

app = FastAPI(title="MSFEA Internship Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

_limiter = RateLimiter(settings.rate_limit_requests, settings.rate_limit_window_seconds)


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


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    citations: list[str]
    refused: bool
    disclaimer: str
    interaction_id: int | None = None


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check — confirms the API is up."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, _rl: None = Depends(rate_limit)) -> ChatResponse:
    """Answer a question via the guarded bot; degrade gracefully on backend errors."""
    # Sanitize, then anonymize once; use the same text for the LLM and the log
    # (CLAUDE.md §7).
    question = anonymize(sanitize(req.question))

    if not question:
        result = Answer(
            text="Please type a question about internships or CDC programs.",
            citations=[],
            refused=True,
        )
    else:
        try:
            result = generate_answer(question)
        except Exception:  # noqa: BLE001 - never 500 at the student; escalate gracefully
            contact = settings.escalation_contact or "the CDC office"
            result = Answer(
                text=f"Sorry, I'm having trouble right now. Please contact {contact}.",
                citations=[],
                refused=True,
            )

    interaction_id = log_interaction(question, result)  # fail-safe; never breaks the response

    return ChatResponse(
        answer=result.text,
        citations=result.citations,
        refused=result.refused,
        disclaimer=result.disclaimer,
        interaction_id=interaction_id,
    )


class RateRequest(BaseModel):
    interaction_id: int
    rating: int  # +1 (helpful) or -1 (not helpful)


@app.post("/rate")
def rate(req: RateRequest, _rl: None = Depends(rate_limit)) -> dict[str, bool]:
    """Record a student's thumbs up/down on an answer."""
    if req.rating not in (1, -1):
        raise HTTPException(status_code=422, detail="rating must be +1 or -1")
    return {"ok": set_rating(req.interaction_id, req.rating)}


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
            retrieved=f.retrieved,
        )
        for f in feedback_items()
    ]


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


class ResolveRequest(BaseModel):
    interaction_id: int


@app.post("/admin/api/resolve")
def admin_resolve(req: ResolveRequest, _: None = Depends(require_admin)) -> dict[str, bool]:
    """Dismiss a feedback item without publishing an answer.

    For cases that don't need new KB content (e.g. a thumbs-down on an answer
    that was actually correct). Removes it from the attention queue.
    """
    return {"ok": resolve_interaction(req.interaction_id)}


# Static frontends: the widget (demo) and the admin dashboard.
_ROOT = Path(__file__).resolve().parents[3]
_WIDGET_DIR = _ROOT / "widget"
if _WIDGET_DIR.is_dir():
    app.mount("/widget", StaticFiles(directory=str(_WIDGET_DIR), html=True), name="widget")
_DASHBOARD_DIR = _ROOT / "dashboard"
if _DASHBOARD_DIR.is_dir():
    app.mount("/dashboard", StaticFiles(directory=str(_DASHBOARD_DIR), html=True), name="dashboard")
