"""FastAPI application — the thin backend the widget calls (CLAUDE.md §5.7).

Endpoints:
- GET  /health  — liveness check.
- POST /chat    — answer a student question through the guarded RAG pipeline.

The widget is served as static files under /widget for easy local demoing;
CORS is enabled so the widget can also be embedded on a different origin (the
real AUB page).
"""

from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from msfea_bot.api.security import RateLimiter, sanitize
from msfea_bot.config import settings
from msfea_bot.generation import generate_answer
from msfea_bot.generation.answer import Answer
from msfea_bot.observability.privacy import anonymize
from msfea_bot.observability.store import log_interaction

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

    log_interaction(question, result)  # fail-safe; never breaks the response

    return ChatResponse(
        answer=result.text,
        citations=result.citations,
        refused=result.refused,
        disclaimer=result.disclaimer,
    )


# Serve the vanilla-JS widget for local demoing (http://localhost:8000/widget/demo.html).
_WIDGET_DIR = Path(__file__).resolve().parents[3] / "widget"
if _WIDGET_DIR.is_dir():
    app.mount("/widget", StaticFiles(directory=str(_WIDGET_DIR), html=True), name="widget")
