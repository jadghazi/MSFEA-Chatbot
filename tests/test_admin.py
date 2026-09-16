"""Tests for rating + admin endpoints (hermetic — no DB, backend monkeypatched)."""

import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as app_module
from msfea_bot.api.app import app
from msfea_bot.api.security import RateLimiter
from msfea_bot.config import settings

client = TestClient(app)

DRAFT = {
    "question": "q",
    "answer": "a",
    "department": "all",
    "programs": ["internship"],
    "evidence_refs": [
        {"source_doc": "rules.md", "locator": "Eligibility", "excerpt": "source words"}
    ],
    "representative_question": "q",
    "paraphrase_question": "Could you explain q?",
    "expected_evidence": "source words",
    "change_reason": "Address reviewed feedback.",
}


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


def test_admin_curate_saves_draft_without_invalidating_chat(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "create_draft", lambda payload, actor="admin": (7, 11))
    monkeypatch.setattr(
        app_module._guard,
        "invalidate",
        lambda: pytest.fail("saving a draft must not invalidate student answer cache"),
    )
    resp = client.post(
        "/admin/api/curate",
        headers={"Authorization": "Bearer secret"},
        json=DRAFT,
    )
    assert resp.status_code == 200
    assert resp.json() == {"entry_id": 7, "revision_id": 11, "state": "draft"}


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
        "create_successor_draft",
        lambda i, payload, actor="admin": seen.update(id=i, payload=payload) or 12,
    )
    resp = client.post(
        "/admin/api/curated/edit",
        headers={"Authorization": "Bearer secret"},
        json={"id": 5, "draft": DRAFT},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert resp.json()["revision_id"] == 12
    assert seen["id"] == 5
    assert seen["payload"].department == "all"


def test_admin_curated_edit_missing_returns_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "create_successor_draft", lambda *args, **kwargs: None)
    resp = client.post(
        "/admin/api/curated/edit",
        headers={"Authorization": "Bearer secret"},
        json={"id": 999, "draft": DRAFT},
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is False


def test_admin_curated_retire_is_atomic_and_invalidates_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        app_module,
        "retire_entry",
        lambda entry_id, reason, invalidate_cache: (
            seen.update(entry_id=entry_id, reason=reason),
            invalidate_cache(),
            "sha256:retired",
        )[-1],
    )
    invalidations: list[str] = []
    monkeypatch.setattr(app_module._guard, "invalidate", lambda: invalidations.append("yes"))
    resp = client.post(
        "/admin/api/curated/retire",
        headers={"Authorization": "Bearer secret"},
        json={"id": 5, "reason": "Policy withdrawn."},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "generation": "sha256:retired"}
    assert seen == {"entry_id": 5, "reason": "Policy withdrawn."}
    assert invalidations == ["yes"]


def test_admin_curated_retire_requires_token() -> None:
    # Wrong/absent auth is rejected (admin is enabled via .env in this env).
    assert client.post("/admin/api/curated/retire", json={"id": 1}).status_code in (401, 403)


def test_admin_curation_options_are_server_populated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "program_registry", lambda: ("co-op", "internship"))
    monkeypatch.setattr(app_module, "source_registry", lambda: ("rules.md",))

    resp = client.get(
        "/admin/api/curation-options", headers={"Authorization": "Bearer secret"}
    )

    assert resp.status_code == 200
    assert resp.json()["programs"] == ["co-op", "internship"]
    assert resp.json()["sources"] == ["rules.md"]
    assert {item["code"] for item in resp.json()["departments"]} == {
        "all",
        "mech",
        "ece",
        "chem",
        "iem",
        "cee",
    }


def test_admin_draft_rejects_unscoped_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    payload = {**DRAFT, "department": ""}

    resp = client.post(
        "/admin/api/curate",
        headers={"Authorization": "Bearer secret"},
        json=payload,
    )

    assert resp.status_code == 422


def test_admin_validation_endpoints_are_authenticated_and_delegate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(app_module, "start_validation", lambda revision_id: f"run-{revision_id}")
    monkeypatch.setattr(
        app_module,
        "validation_runs",
        lambda: [{"id": "run-9", "revision_id": 9, "status": "pending"}],
    )
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        app_module,
        "record_human_review",
        lambda run_id, reviewer, decision, reason: seen.update(
            run_id=run_id, reviewer=reviewer, decision=decision, reason=reason
        )
        or 17,
    )

    assert client.get("/admin/api/validation-runs").status_code == 401
    started = client.post(
        "/admin/api/revisions/validate",
        headers={"Authorization": "Bearer secret"},
        json={"revision_id": 9},
    )
    listed = client.get(
        "/admin/api/validation-runs", headers={"Authorization": "Bearer secret"}
    )
    reviewed = client.post(
        "/admin/api/revisions/review",
        headers={"Authorization": "Bearer secret"},
        json={
            "run_id": "run-9",
            "reviewer_label": "CDC reviewer",
            "decision": "confirm_no_conflict",
            "reason": "Checked the authoritative source and related passages.",
        },
    )

    assert started.json() == {"run_id": "run-9", "status": "pending"}
    assert listed.json()[0]["revision_id"] == 9
    assert reviewed.json() == {"review_id": 17}
    assert seen == {
        "run_id": "run-9",
        "reviewer": "CDC reviewer",
        "decision": "confirm_no_conflict",
        "reason": "Checked the authoritative source and related passages.",
    }


def test_admin_validation_conflicts_are_specific(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    monkeypatch.setattr(
        app_module,
        "start_validation",
        lambda revision_id: (_ for _ in ()).throw(ValueError("revision state changed")),
    )

    response = client.post(
        "/admin/api/revisions/validate",
        headers={"Authorization": "Bearer secret"},
        json={"revision_id": 9},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "revision state changed"


def test_admin_publish_requires_exact_revision_and_run(monkeypatch: pytest.MonkeyPatch) -> None:
    from msfea_bot.curation.publication import PublicationResult

    monkeypatch.setattr(app_module.settings, "admin_token", "secret")
    seen: dict[str, object] = {}
    monkeypatch.setattr(
        app_module,
        "request_publication",
        lambda revision_id, run_id: seen.update(
            revision_id=revision_id, run_id=run_id
        )
        or PublicationResult("attempt-1", revision_id, "intent", None),
    )

    response = client.post(
        "/admin/api/revisions/publish",
        headers={"Authorization": "Bearer secret"},
        json={"revision_id": 12, "run_id": "run-12"},
    )

    assert response.status_code == 200
    assert response.json()["attempt_id"] == "attempt-1"
    assert response.json()["generation"] is None
    assert response.json()["status"] == "intent"
    assert seen == {"revision_id": 12, "run_id": "run-12"}


def test_internal_cache_invalidation_requires_independent_worker_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "curation_worker_token", "private-worker-token")
    before = app_module._guard.version
    assert client.post("/internal/cache/invalidate").status_code == 401
    assert client.post(
        "/internal/cache/invalidate",
        headers={"Authorization": f"Bearer {settings.admin_token}"},
    ).status_code == 401
    response = client.post(
        "/internal/cache/invalidate",
        headers={"X-Curation-Worker-Token": "private-worker-token"},
    )
    assert response.status_code == 200
    assert response.json()["cache_version"] == before + 1


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
