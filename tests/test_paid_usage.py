"""Paid admission tested against an isolated schema, with no hosted LLM calls."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from typing import Any
import uuid

import psycopg
import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as api
from msfea_bot.config import settings
from msfea_bot.llm import budget
from msfea_bot.llm.base import LLMAdmissionError

admit_chat = budget.admit_chat


@pytest.fixture
def paid_db(monkeypatch: pytest.MonkeyPatch) -> Any:
    schema = "paid_test_" + uuid.uuid4().hex
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute(f'CREATE SCHEMA "{schema}"')

    def connect() -> Any:
        return psycopg.connect(settings.database_url, options=f"-c search_path={schema}")

    with connect() as conn:
        conn.execute(Path("src/msfea_bot/curation/migrations/0008_paid_usage_guard.sql").read_text())
    monkeypatch.setattr(budget, "_connect", connect)
    for name, value in dict(llm_model="student", curation_llm_model="staff", llm_calls_enabled=True,
                            llm_daily_cost_limit_usd=0.5, llm_daily_request_limit=100,
                            llm_daily_token_limit=500000, llm_global_concurrency=8,
                            admin_token="test-admin", ip_daily_request_limit=3,
                            session_question_limit=2).items():
        monkeypatch.setattr(settings, name, value)
    try:
        yield connect
    finally:
        with psycopg.connect(settings.database_url, autocommit=True) as conn:
            conn.execute(f'DROP SCHEMA "{schema}" CASCADE')


def reserve(model: str = "student", purpose: str = "") -> int:
    return budget.reserve("Source-grounded question", model, 4096, purpose)


@pytest.mark.parametrize("field,value", [("llm_daily_request_limit", 1),
                                         ("llm_daily_token_limit", 6000),
                                         ("llm_daily_cost_limit_usd", 0.025)])
def test_concurrent_admission_cannot_overrun_a_ceiling(paid_db: Any, monkeypatch: pytest.MonkeyPatch,
                                                     field: str, value: Any) -> None:
    monkeypatch.setattr(settings, field, value)
    def call(_: int) -> bool:
        try:
            reserve()
            return True
        except LLMAdmissionError:
            return False
    with ThreadPoolExecutor(max_workers=6) as pool:
        assert sum(pool.map(call, range(12))) == 1
    report = budget.report()
    assert report["usage"][0]["requests"] == 1


def test_usage_settles_reasoning_and_is_idempotent(paid_db: Any) -> None:
    ticket = reserve()
    usage = SimpleNamespace(prompt_token_count=1000, candidates_token_count=100, total_token_count=1900)
    budget.settle(ticket, usage)
    budget.settle(ticket, usage)
    row = budget.report()["usage"][0]
    assert (row["input_tokens"], row["visible_output_tokens"], row["reasoning_tokens"]) == (1000, 100, 800)
    assert row["charged_usd"] == pytest.approx(0.004125)
    assert row["charged_tokens"] == 1900 and row["requests"] == 1


def test_uncertain_usage_and_failures_keep_reservations(paid_db: Any) -> None:
    first, second = reserve(), reserve("staff", "curation_")
    before = sum(row["charged_usd"] for row in budget.report()["usage"])
    budget.settle(first, None)
    budget.failed(second, TimeoutError())
    after = budget.report()
    assert sum(row["charged_usd"] for row in after["usage"]) == before
    assert sum(row["uncertain_attempts"] for row in after["usage"]) == 2


def test_durable_kill_switch_covers_all_purposes_and_environment(paid_db: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    budget.set_enabled(False)
    for model, purpose in [("student", ""), ("student", "curation_preview_"), ("staff", "curation_")]:
        with pytest.raises(LLMAdmissionError):
            reserve(model, purpose)
    assert budget.report()["usage"] == []
    # Fresh connections all see the same state; no process-local toggle/cache.
    budget.set_enabled(True)
    reserve()
    monkeypatch.setattr(settings, "llm_calls_enabled", False)
    budget.set_enabled(True)
    with pytest.raises(LLMAdmissionError):
        reserve()


def test_provider_errors_trip_a_cooldown(paid_db: Any) -> None:
    for _ in range(5):
        budget.failed(reserve(), TimeoutError())
    assert budget.report()["circuit_until"]
    with pytest.raises(LLMAdmissionError):
        reserve()
    with paid_db() as conn:
        conn.execute("UPDATE llm_control SET circuit_until=now()-interval '1 second' WHERE id=1")
    reserve()


def test_budget_expires_and_utc_rollover_preserves_operator_pause(paid_db: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import date
    monkeypatch.setattr(settings, "llm_daily_request_limit", 1)
    ticket = reserve()
    with paid_db() as conn:
        conn.execute("UPDATE llm_attempts SET day=day-1,outcome='failed' WHERE id=%s", (ticket,))
    reserve()
    budget.set_enabled(False)
    with pytest.raises(LLMAdmissionError):
        reserve()
    budget.set_enabled(True)
    monkeypatch.setattr(settings, "llm_price_valid_until", date(2020, 1, 1))
    with pytest.raises(LLMAdmissionError):
        reserve()


def test_unexpected_usage_fails_closed(paid_db: Any) -> None:
    ticket = reserve()
    budget.settle(ticket, SimpleNamespace(prompt_token_count=100000, candidates_token_count=500, total_token_count=102000))
    assert not budget.report()["enabled"]
    with pytest.raises(LLMAdmissionError):
        reserve()


def test_server_side_ip_chat_limits_survive_rotated_sessions(paid_db: Any) -> None:
    assert admit_chat("192.0.2.1", "chat1") is None
    assert admit_chat("192.0.2.1", "chat1") is None
    assert admit_chat("192.0.2.1", "chat1") == "session"
    assert admit_chat("192.0.2.1", "chat2") is None
    assert admit_chat("192.0.2.1", "chat3") == "ip"
    assert admit_chat("192.0.2.2", "chat1") == "session"
    assert admit_chat("192.0.2.2", "chat4") is None
    with paid_db() as conn:
        keys = conn.execute("SELECT key FROM abuse_counts").fetchall()
    assert all(len(r[0]) == 64 and "192.0.2" not in r[0] for r in keys)


def test_admin_control_is_authenticated_strict_and_does_not_reset_usage(paid_db: Any) -> None:
    reserve()
    client = TestClient(api.app)
    assert client.get("/admin/api/llm-usage").status_code == 401
    assert client.post("/admin/api/llm-control", json={"enabled": False}).status_code == 401
    headers = {"Authorization": "Bearer test-admin"}
    assert client.post("/admin/api/llm-control", headers=headers, json={"enabled": "false"}).status_code == 422
    assert client.post("/admin/api/llm-control", headers=headers, json={"enabled": False, "reset": True}).status_code == 422
    assert client.post("/admin/api/llm-control", headers=headers, json={"enabled": False}).status_code == 200
    response = client.get("/admin/api/llm-usage", headers=headers).json()
    assert not response["enabled"] and response["usage"][0]["requests"] == 1


@pytest.mark.parametrize("extra", ["model", "max_output_tokens", "prompt", "top_k"])
def test_clients_cannot_supply_expensive_controls(extra: str) -> None:
    response = TestClient(api.app).post("/chat", json={"question": "Hi", extra: "unexpected"})
    assert response.status_code == 422


def test_accounting_failure_never_contacts_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("google.genai")
    from google import genai
    from msfea_bot.llm.gemini import GeminiProvider
    def unavailable() -> Any:
        raise psycopg.OperationalError("offline")
    def unexpected(**kwargs: Any) -> Any:
        pytest.fail("The SDK was contacted without accounting")
    monkeypatch.setattr(budget, "_connect", unavailable)
    monkeypatch.setattr(settings, "llm_api_key", "fake-key")
    monkeypatch.setattr(settings, "llm_model", "student")
    monkeypatch.setattr(genai, "Client", lambda **kwargs: SimpleNamespace(models=SimpleNamespace(generate_content=unexpected)))
    with pytest.raises(LLMAdmissionError):
        GeminiProvider().generate("Question")


def test_global_concurrency_is_shared_with_staff(paid_db: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_global_concurrency", 1)
    ticket = reserve("staff", "curation_")
    with pytest.raises(LLMAdmissionError):
        reserve("student", "curation_preview_")
    budget.settle(ticket, SimpleNamespace(prompt_token_count=5, candidates_token_count=5, total_token_count=10))
    reserve()


def test_daily_chat_admission_runs_before_local_reply_or_cache(paid_db: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(budget, "admit_chat", admit_chat)
    client = TestClient(api.app)
    payload = {"question": "Hi", "session_id": "test-session-0001"}
    assert client.post("/chat", json=payload).status_code == 200
    assert client.post("/chat", json=payload).status_code == 200
    assert client.post("/chat", json=payload).status_code == 429
    assert budget.report()["usage"] == []


def test_retry_is_charged_and_pause_blocks_the_actual_sdk(paid_db: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("google.genai")
    from google import genai
    from msfea_bot.llm.gemini import GeminiProvider
    calls: list[str] = []
    def generate_content(**kwargs: Any) -> Any:
        calls.append(kwargs["model"])
        if len(calls) == 1:
            raise TimeoutError()
        return SimpleNamespace(text="ok", candidates=[], usage_metadata=SimpleNamespace(
            prompt_token_count=10, candidates_token_count=5, total_token_count=25))
    monkeypatch.setattr(genai, "Client", lambda **kwargs: SimpleNamespace(models=SimpleNamespace(generate_content=generate_content)))
    monkeypatch.setattr(settings, "llm_api_key", "fake-key")
    assert GeminiProvider().generate("Question").text == "ok"
    assert budget.report()["usage"][0]["requests"] == 2
    budget.set_enabled(False)
    for model, purpose in [("student", ""), ("student", "curation_preview_"), ("staff", "curation_")]:
        with pytest.raises(LLMAdmissionError):
            GeminiProvider(model=model, purpose=purpose).generate("Question")
    assert len(calls) == 2


def test_failed_accounting_does_not_release_a_reservation(paid_db: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    ticket = reserve()
    old_cost = budget.report()["usage"][0]["charged_usd"]
    def offline() -> Any:
        raise psycopg.OperationalError("offline")
    with monkeypatch.context() as patch:
        patch.setattr(budget, "_connect", offline)
        with pytest.raises(psycopg.Error):
            budget.settle(ticket, SimpleNamespace(prompt_token_count=1, candidates_token_count=1, total_token_count=2))
    assert budget.report()["usage"][0]["charged_usd"] == old_cost
