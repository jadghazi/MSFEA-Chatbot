"""Tests for the /chat and /health API endpoints.

`generate_answer` is monkeypatched so these run without the DB or a live LLM.
"""

import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as app_module
from msfea_bot.api.app import app
from msfea_bot.generation.answer import Answer

client = TestClient(app)


def test_health_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_returns_structured_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake(question: str) -> Answer:
        return Answer(text="At least 8 weeks.", citations=["doc.md > Duration"], refused=False)

    monkeypatch.setattr(app_module, "generate_answer", fake)
    resp = client.post("/chat", json={"question": "How long is the internship?"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"] == "At least 8 weeks."
    assert body["citations"] == ["doc.md > Duration"]
    assert body["refused"] is False
    assert body["disclaimer"]


def test_chat_degrades_gracefully_on_backend_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(question: str) -> Answer:
        raise RuntimeError("LLM down")

    monkeypatch.setattr(app_module, "generate_answer", boom)
    resp = client.post("/chat", json={"question": "anything"})
    assert resp.status_code == 200
    assert resp.json()["refused"] is True


def test_chat_rejects_empty_question() -> None:
    assert client.post("/chat", json={"question": ""}).status_code == 422
