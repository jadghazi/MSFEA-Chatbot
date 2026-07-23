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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

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
def chat(req: ChatRequest) -> ChatResponse:
    """Answer a question via the guarded bot; degrade gracefully on backend errors."""
    # Anonymize once, then use the same text for the LLM and the log (CLAUDE.md §7).
    question = anonymize(req.question)
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
