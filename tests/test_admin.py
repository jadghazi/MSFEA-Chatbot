"""Tests for rating + admin endpoints (hermetic — no DB, backend monkeypatched)."""

import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as app_module
from msfea_bot.api.app import app
from msfea_bot.api.security import RateLimiter

client = TestClient(app)


def _fresh_limiter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module, "_limiter", RateLimiter(max_requests=100, window_seconds=60))


def test_rate_records(monkeypatch: pytest.MonkeyPatch) -> None:
    _fresh_limiter(monkeypatch)
    monkeypatch.setattr(app_module, "set_rating", lambda i, r: True)
    resp = client.post("/rate", json={"interaction_id": 1, "rating": -1})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_rate_rejects_bad_value(monkeypatch: pytest.MonkeyPatch) -> None:
    _fresh_limiter(monkeypatch)
    monkeypatch.setattr(app_module, "set_rating", lambda i, r: True)
    assert client.post("/rate", json={"interaction_id": 1, "rating": 5}).status_code == 422


def test_admin_disabled_without_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "")
    assert client.get("/admin/api/feedback").status_code == 403


def test_admin_rejects_wrong_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    resp = client.get("/admin/api/feedback", headers={"Authorization": "Bearer nope"})
    assert resp.status_code == 401


def test_admin_feedback_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "feedback_items", lambda: [])
    resp = client.get("/admin/api/feedback", headers={"Authorization": "Bearer secret"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_admin_curate_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "publish_curated_answer", lambda q, a, author="admin": 7)
    monkeypatch.setattr(app_module, "resolve_by_question", lambda q: 2)
    resp = client.post(
        "/admin/api/curate",
        headers={"Authorization": "Bearer secret"},
        json={"question": "q", "answer": "a"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["curated_id"] == 7
    # Publishing clears the queue for that question (ADR-0010 / B-3a resolution).
    assert body["resolved"] == 2


def test_admin_curated_lists_published(monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import datetime

    from msfea_bot.curation.store import CuratedAnswer

    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(
        app_module,
        "list_curated",
        lambda active_only=True: [
            CuratedAnswer(3, "How long?", "8 weeks.", "admin", datetime(2026, 7, 23), True)
        ],
    )
    resp = client.get("/admin/api/curated", headers={"Authorization": "Bearer secret"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["question"] == "How long?"
    assert body[0]["answer"] == "8 weeks."
    assert "active" not in body[0]  # internal field not exposed


def test_admin_resolve_dismisses_item(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "resolve_interaction", lambda i: True)
    resp = client.post(
        "/admin/api/resolve",
        headers={"Authorization": "Bearer secret"},
        json={"interaction_id": 42},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_admin_resolve_rejects_wrong_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    resp = client.post(
        "/admin/api/resolve", headers={"Authorization": "Bearer nope"}, json={"interaction_id": 1}
    )
    assert resp.status_code == 401
