"""FastAPI application — the thin backend the widget calls.

Only a health check exists so far. The real ``/chat`` endpoint arrives with the
walking skeleton (CLAUDE.md §5.3), once retrieval + generation exist.
"""

from fastapi import FastAPI

app = FastAPI(title="MSFEA Internship Chatbot API")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check — confirms the API scaffold stands up."""
    return {"status": "ok"}
