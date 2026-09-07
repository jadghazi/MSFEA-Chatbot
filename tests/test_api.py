"""Tests for the /chat and /health API endpoints.

`generate_answer` is monkeypatched so these run without the DB or a live LLM.
"""

import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as app_module
from msfea_bot.api.app import app
from msfea_bot.generation.answer import Answer
from msfea_bot.llm import LLMRateLimitError

client = TestClient(app)


def test_health_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root_serves_standalone_pilot_directly() -> None:
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 200
    assert "MSFEA Student Assistant" in resp.text

    head = client.head("/")
    assert head.status_code == 200


def test_ready_checks_the_index(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module, "index_is_ready", lambda: True)
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ready"}


def test_ready_rejects_an_empty_or_mismatched_index(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module, "index_is_ready", lambda: False)
    resp = client.get("/ready")
    assert resp.status_code == 503


def test_chat_returns_structured_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    # **kwargs so the stub keeps matching generate_answer's signature as it grows
    # (it now takes `department`); a stale stub raises TypeError, which the
    # endpoint's graceful-degradation handler would silently turn into a refusal.
    def fake(question: str, **kwargs: object) -> Answer:
        return Answer(text="At least 8 weeks.", citations=["doc.md > Duration"], refused=False)

    monkeypatch.setattr(app_module, "generate_answer", fake)
    monkeypatch.setattr(app_module, "log_interaction", lambda q, a: None)
    resp = client.post("/chat", json={"question": "How long is the internship?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "At least 8 weeks."
    assert body["citations"] == ["doc.md > Duration"]
    assert body["refused"] is False
    assert body["disclaimer"]


def test_chat_degrades_gracefully_on_backend_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(question: str, **kwargs: object) -> Answer:
        raise RuntimeError("LLM down")

    monkeypatch.setattr(app_module, "generate_answer", boom)
    monkeypatch.setattr(app_module, "log_interaction", lambda q, a: None)
    resp = client.post("/chat", json={"question": "anything"})
    assert resp.status_code == 200
    assert resp.json()["refused"] is True
    assert resp.json()["error_code"] == "service_unavailable"


def test_chat_returns_actionable_rate_limit_response(monkeypatch: pytest.MonkeyPatch) -> None:
    def limited(question: str, **kwargs: object) -> Answer:
        raise LLMRateLimitError("quota")

    monkeypatch.setattr(app_module, "generate_answer", limited)
    monkeypatch.setattr(app_module, "log_interaction", lambda q, a: None)
    resp = client.post("/chat", json={"question": "anything"})
    assert resp.status_code == 200
    assert resp.json()["error_code"] == "rate_limited"
    assert "try again" in resp.json()["answer"].lower()


def test_chat_sanitizes_and_anonymizes_every_history_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    def fake(question: str, **kwargs: object) -> Answer:
        seen["history"] = kwargs["history"]
        return Answer(text="ok", refused=False)

    monkeypatch.setattr(app_module, "generate_answer", fake)
    monkeypatch.setattr(app_module, "log_interaction", lambda q, a: None)
    resp = client.post(
        "/chat",
        json={
            "question": "Where do I get it?",
            "history": [
                {"role": "user", "content": "Email me at student@example.com\u0000"},
                {"role": "assistant", "content": "Use the form."},
            ],
        },
    )
    assert resp.status_code == 200
    history = seen["history"]
    assert isinstance(history, list)
    assert "[redacted-email]" in history[0].content
    assert "\u0000" not in history[0].content


def test_chat_rejects_empty_question() -> None:
    assert client.post("/chat", json={"question": ""}).status_code == 422


def test_chat_rate_limited(monkeypatch: pytest.MonkeyPatch) -> None:
    from msfea_bot.api.security import RateLimiter

    monkeypatch.setattr(app_module, "_limiter", RateLimiter(max_requests=1, window_seconds=60))
    monkeypatch.setattr(
        app_module, "generate_answer", lambda q, **kw: Answer(text="ok", refused=False)
    )
    monkeypatch.setattr(app_module, "log_interaction", lambda q, a: None)
    assert client.post("/chat", json={"question": "hi"}).status_code == 200
    assert client.post("/chat", json={"question": "hi"}).status_code == 429
