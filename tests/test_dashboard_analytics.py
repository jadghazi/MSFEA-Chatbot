"""Reporting contracts plus optional integration tests against a disposable PostgreSQL DB."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import psycopg
import pytest
from fastapi.testclient import TestClient

import msfea_bot.api.app as api
import msfea_bot.observability.analytics as reporting
from msfea_bot.observability.store import _init_schema


def test_analytics_auth_and_range(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(api.settings, "admin_token", "test-admin")
    monkeypatch.setattr(api, "analytics", lambda days: {"days": days})
    client = TestClient(api.app)
    assert client.get("/admin/api/analytics").status_code == 401
    headers = {"Authorization": "Bearer test-admin"}
    for days in (7, 30, 90):
        response = client.get(f"/admin/api/analytics?days={days}", headers=headers)
        assert response.json() == {"days": days}
    assert client.get("/admin/api/analytics?days=365", headers=headers).status_code == 422
    assert client.get("/admin/api/analytics", headers=headers).json() == {"days": 30}
    monkeypatch.setattr(api.settings, "admin_token", "")
    assert client.get("/admin/api/analytics", headers=headers).status_code == 403


@pytest.fixture
def reporting_db(monkeypatch: pytest.MonkeyPatch) -> Any:
    url = os.environ.get("DASHBOARD_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set DASHBOARD_TEST_DATABASE_URL to a disposable PostgreSQL database")
    # Temporary schema protects other data even if a developer uses a shared test database.
    import uuid

    schema = "dashboard_test_" + uuid.uuid4().hex
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(f'CREATE SCHEMA "{schema}"')

    def connect() -> Any:
        conn = psycopg.connect(url, autocommit=True, options=f"-c search_path={schema}")
        return conn

    with connect() as conn:
        _init_schema(conn)
    monkeypatch.setattr(reporting, "_connect", connect)
    monkeypatch.setattr(reporting, "_ensure_schema", lambda conn: None)
    fixed = datetime(2026, 9, 27, 12, tzinfo=timezone.utc)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz: Any = None) -> datetime:
            return fixed

    monkeypatch.setattr(reporting, "datetime", FixedDateTime)
    try:
        yield connect, fixed
    finally:
        with psycopg.connect(url, autocommit=True) as conn:
            conn.execute(f'DROP SCHEMA "{schema}" CASCADE')


def test_empty_period_has_no_invented_measurements(reporting_db: Any) -> None:
    data = reporting.analytics(7)
    assert data["summary"]["total"] == 0
    assert data["summary"]["avg_llm_latency_ms"] is None
    assert data["summary"]["llm_input_tokens"] is None
    assert len(data["daily"]) == 7
    assert all(day["total"] == 0 for day in data["daily"])
    assert data["unanswered"] == data["sources"] == data["negative_reasons"] == []


def test_reporting_boundaries_outcomes_and_denominators(reporting_db: Any) -> None:
    connect, now = reporting_db
    start = now.replace(hour=0) - timedelta(days=6)
    with connect() as conn:
        for ts, question, refused, error, rating, resolved, citations, latency, tokens in [
            (start, "answered", False, None, 1, None, ["rules > A", "rules > A"], 1000, 100),
            (now, "gap", True, None, -1, None, [], 3000, 200),
            (now, "gap", True, None, None, None, [], None, None),
            (now, "fixed gap", True, None, None, now, [], None, None),
            (now, "outage", True, "quota", -1, None, [], None, None),
            (now, "answered without citation", False, None, None, None, [], None, None),
            (start - timedelta(microseconds=1), "older", False, None, 1, None, [], 9000, 999),
            (now + timedelta(seconds=1), "future", False, None, None, None, [], 9000, 999),
        ]:
            conn.execute(
                "INSERT INTO interactions (ts,question,answer,refused,error_code,rating,"
                "resolved_at,citations,llm_latency_ms,llm_input_tokens,llm_output_tokens)"
                " VALUES (%s,%s,'fixture',%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    ts,
                    question,
                    refused,
                    error,
                    rating,
                    resolved,
                    citations,
                    latency,
                    tokens,
                    tokens,
                ),
            )
    data = reporting.analytics(7)
    summary = data["summary"]
    assert summary["total"] == 6
    assert (summary["answered"], summary["refused"], summary["temporary_errors"]) == (2, 3, 1)
    assert summary["pending"] == 2
    assert summary["thumbs_up"] == 1 and summary["thumbs_down"] == 2
    assert summary["answers_with_citations"] == 1
    assert summary["latency_samples"] == summary["token_samples"] == 2
    assert summary["avg_llm_latency_ms"] == 2000
    assert summary["p95_llm_latency_ms"] == 2900
    assert summary["llm_input_tokens"] == summary["llm_output_tokens"] == 300
    assert sum(day["total"] for day in data["daily"]) == 6
    assert data["daily"][0]["total"] == 1
    assert data["daily"][-1]["total"] == 5
    assert data["sources"] == [{"source": "rules > A", "count": 1}]
    assert len(data["unanswered"]) == 1
    assert data["unanswered"][0]["question"] == "gap"
    assert data["unanswered"][0]["count"] == 2
    assert data["negative_reasons"] == [{"reason": "No reason given", "count": 2}]
    assert reporting.analytics(30)["summary"]["total"] == 7
