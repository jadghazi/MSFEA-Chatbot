"""Needs Attention selection/context contracts; never call a live provider."""

import os
import uuid
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any

import psycopg
import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as api
import msfea_bot.observability.analytics as reporting
import msfea_bot.observability.store as store
from msfea_bot.generation.answer import Answer
from msfea_bot.generation.conversation import ConversationMessage


@pytest.fixture
def attention_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    url = os.environ.get("DASHBOARD_TEST_DATABASE_URL")
    if not url and os.environ.get("CI"):
        url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("Needs an explicitly configured disposable dashboard test database")
    schema = "attention_test_" + uuid.uuid4().hex
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(f'CREATE SCHEMA "{schema}"')

    def connect() -> Any:
        return psycopg.connect(url, autocommit=True, options=f"-c search_path={schema}")

    monkeypatch.setattr(store, "_connect", connect)
    monkeypatch.setattr(store, "_schema_ready", False)
    monkeypatch.setattr(reporting, "_connect", connect)
    monkeypatch.setattr(reporting, "_ensure_schema", store._ensure_schema)
    try:
        store.initialize_schema()
        yield connect
    finally:
        with psycopg.connect(url, autocommit=True) as conn:
            conn.execute(f'DROP SCHEMA "{schema}" CASCADE')


def test_queue_includes_advisory_signals_but_not_ordinary_answers(attention_db: Any) -> None:
    candidates = [
        ("refusal", Answer(text="Please contact CDC.", refused=True)),
        ("negative", Answer(text="Eight weeks.")),
        ("missing comparison", Answer(text="I can't confirm whether these rules differ. Contact CDC.")),
        ("curly apostrophe", Answer(text="I can’t verify the fee from these sources.")),
        ("partial", Answer(text="The internship is eight weeks. I cannot confirm the fee.")),
        ("source gap", Answer(text="The sources do not contain information about the deadline.")),
        ("ordinary", Answer(text="You normally do it during the summer before your final year.")),
        ("policy negative", Answer(text="You cannot combine these placements without approval.")),
        ("positive verification", Answer(text="I can confirm the documented minimum is eight weeks.")),
        ("outage", Answer(text="I can't answer right now.", refused=True, error_code="quota")),
        ("resolved", Answer(text="I can't verify that.")),
    ]
    ids: dict[str, int] = {}
    for question, answer in candidates:
        interaction_id = store.log_interaction(question, answer)
        assert interaction_id is not None
        ids[question] = interaction_id
    assert store.set_rating(ids["negative"], -1)
    assert store.resolve_interaction(ids["resolved"])
    items = store.feedback_items()
    assert {it.question for it in items} == {
        "refusal", "negative", "missing comparison", "curly apostrophe", "partial", "source gap"
    }
    partial = next(it for it in items if it.question == "partial")
    assert partial.possible_incomplete and not partial.refused
    assert store.stats()["pending"] == len(items) == reporting.analytics(7)["summary"]["pending"]
    assert len(store.feedback_items(limit=2)) == 2
    assert store.resolve_interaction(partial.id)
    assert partial.id not in {it.id for it in store.feedback_items()}


def test_history_bounds_roundtrip_and_older_rows(attention_db: Any) -> None:
    history = [ConversationMessage("user", f"message {i} " + "x" * 1300) for i in range(12)]
    interaction_id = store.log_interaction(
        "and the duration?", Answer(text="I can't confirm that."), history=history, department="ece"
    )
    assert interaction_id is not None
    item = store.feedback_items()[0]
    assert len(item.conversation_history) == 8
    assert item.conversation_history[0]["content"].startswith("message 4 ")
    assert all(len(m["content"]) == 1200 for m in item.conversation_history)
    assert item.department == "ece" and item.history_source == "request"
    with attention_db() as conn:
        conn.execute("INSERT INTO interactions (question,answer,refused) VALUES ('legacy','unknown',true)")
    legacy = next(it for it in store.feedback_items() if it.question == "legacy")
    assert legacy.conversation_history == [] and legacy.history_source is None


def test_chat_logs_the_same_redacted_history_without_changing_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, Any] = {}

    def generate(question: str, **kwargs: Any) -> Answer:
        seen["generation_history"] = kwargs["history"]
        return Answer(text="The existing response.")

    def log(question: str, answer: Answer, **kwargs: Any) -> int:
        seen.update(kwargs)
        return 42

    monkeypatch.setattr(api, "generate_answer", generate)
    monkeypatch.setattr(api, "log_interaction", log)
    monkeypatch.setattr(api, "anonymize", lambda text: text.replace("student@example.com", "[redacted-email]"))
    response = TestClient(api.app).post("/chat", json={
        "question": "and the duration?", "department": "ece",
        "history": [{"role": "user", "content": "contact student@example.com\u0000"}],
    })
    assert response.status_code == 200 and response.json()["answer"] == "The existing response."
    assert seen["history"] == seen["generation_history"]
    assert seen["history"][0].content == "contact [redacted-email]"
    assert seen["department"] == "ece"


def test_admin_context_is_protected_and_labeled(monkeypatch: pytest.MonkeyPatch) -> None:
    item = store.FeedbackItem(
        42, datetime.now(timezone.utc), "is it the same?", "I can't confirm that.", False,
        None, None, [], True, [{"role": "user", "content": "internship timing"}],
        None, "staff_reported",
    )
    monkeypatch.setattr(api.settings, "admin_token", "test-only")
    monkeypatch.setattr(api, "feedback_items", lambda: [item])
    client = TestClient(api.app)
    assert client.get("/admin/api/feedback").status_code == 401
    data = client.get("/admin/api/feedback", headers={"Authorization": "Bearer test-only"}).json()[0]
    assert data["history_source"] == "staff_reported"
    assert data["conversation_history"] == item.conversation_history
    assert data["possible_incomplete"] is True and data["refused"] is False
