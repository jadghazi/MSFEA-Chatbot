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
    monkeypatch.setattr(app_module, "set_rating", lambda i, r, reason=None: True)
    resp = client.post("/rate", json={"interaction_id": 1, "rating": -1})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_rate_rejects_bad_value(monkeypatch: pytest.MonkeyPatch) -> None:
    _fresh_limiter(monkeypatch)
    monkeypatch.setattr(app_module, "set_rating", lambda i, r, reason=None: True)
    assert client.post("/rate", json={"interaction_id": 1, "rating": 5}).status_code == 422


def test_rate_records_allowed_negative_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    _fresh_limiter(monkeypatch)
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        app_module,
        "set_rating",
        lambda i, r, reason=None: seen.update(id=i, rating=r, reason=reason) or True,
    )
    resp = client.post(
        "/rate",
        json={"interaction_id": 8, "rating": -1, "reason": "Missing information"},
    )
    assert resp.status_code == 200
    assert seen == {"id": 8, "rating": -1, "reason": "Missing information"}


@pytest.mark.parametrize("reason", ["Other", "", "Technical problem"])
def test_rate_rejects_invalid_negative_reason(
    monkeypatch: pytest.MonkeyPatch, reason: str
) -> None:
    _fresh_limiter(monkeypatch)
    monkeypatch.setattr(app_module, "set_rating", lambda i, r, reason=None: True)
    resp = client.post("/rate", json={"interaction_id": 1, "rating": -1, "reason": reason})
    assert resp.status_code == 422


def test_rate_rejects_reason_on_thumbs_up(monkeypatch: pytest.MonkeyPatch) -> None:
    _fresh_limiter(monkeypatch)
    monkeypatch.setattr(app_module, "set_rating", lambda i, r, reason=None: True)
    resp = client.post(
        "/rate", json={"interaction_id": 1, "rating": 1, "reason": "Incorrect"}
    )
    assert resp.status_code == 422


def test_experience_feedback_accepts_only_anonymous_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        app_module, "_experience_limiter", RateLimiter(max_requests=100, window_seconds=60)
    )
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        app_module,
        "save_experience_feedback",
        lambda rating, tags, comment: seen.update(rating=rating, tags=tags, comment=comment) or True,
    )
    resp = client.post(
        "/experience-feedback",
        json={"rating": 5, "tags": ["Easy to use"], "comment": "  Clear and quick.  "},
    )
    assert resp.status_code == 201
    assert seen == {"rating": 5, "tags": ["Easy to use"], "comment": "Clear and quick."}
    assert set(resp.json()) == {"ok"}


@pytest.mark.parametrize(
    "payload",
    [
        {"rating": 0},
        {"rating": 6},
        {"rating": 4, "tags": ["Unknown"]},
        {"rating": 4, "tags": ["Easy to use", "Easy to use"]},
        {"rating": 4, "comment": "x" * 501},
        {"rating": 4, "name": "Student Name"},
    ],
)
def test_experience_feedback_rejects_invalid_payload(
    monkeypatch: pytest.MonkeyPatch, payload: dict[str, object]
) -> None:
    monkeypatch.setattr(
        app_module, "_experience_limiter", RateLimiter(max_requests=100, window_seconds=60)
    )
    monkeypatch.setattr(app_module, "save_experience_feedback", lambda *args: True)
    assert client.post("/experience-feedback", json=payload).status_code == 422


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


def test_admin_experience_feedback_is_protected_and_returns_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from datetime import datetime

    from msfea_bot.experience import ExperienceComment

    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(
        app_module,
        "experience_summary",
        lambda: {
            "total": 2,
            "average_rating": 4.5,
            "rating_distribution": {str(i): int(i == 4 or i == 5) for i in range(1, 6)},
            "tag_counts": {"Easy to use": 2},
            "recent_comments": [ExperienceComment(datetime(2026, 9, 8), 5, "Useful")],
        },
    )
    assert client.get("/admin/api/experience-feedback").status_code == 401
    resp = client.get(
        "/admin/api/experience-feedback", headers={"Authorization": "Bearer secret"}
    )
    assert resp.status_code == 200
    assert resp.json()["average_rating"] == 4.5
    assert resp.json()["recent_comments"][0]["comment"] == "Useful"


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


def test_admin_curated_edit_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    seen = {}
    monkeypatch.setattr(
        app_module,
        "edit_curated_answer",
        lambda i, q, a: seen.update(id=i, q=q, a=a) or True,
    )
    resp = client.post(
        "/admin/api/curated/edit",
        headers={"Authorization": "Bearer secret"},
        json={"id": 5, "question": "new q", "answer": "new a"},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert seen == {"id": 5, "q": "new q", "a": "new a"}


def test_admin_curated_edit_missing_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "edit_curated_answer", lambda i, q, a: False)
    resp = client.post(
        "/admin/api/curated/edit",
        headers={"Authorization": "Bearer secret"},
        json={"id": 999, "question": "q", "answer": "a"},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


def test_admin_curated_retire_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "retire_curated_answer", lambda i: True)
    resp = client.post(
        "/admin/api/curated/retire",
        headers={"Authorization": "Bearer secret"},
        json={"id": 5},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_admin_curated_retire_requires_token() -> None:
    # Wrong/absent auth is rejected (admin is enabled via .env in this env).
    assert client.post("/admin/api/curated/retire", json={"id": 1}).status_code in (401, 403)


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
