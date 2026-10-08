"""Durable, shared admission for every paid provider attempt, including retries.

Reserve a conservative text-input bound plus the full output ceiling atomically.
Settle complete SDK usage (including reasoning); retain uncertain charges after
timeouts, missing usage or crashes. Neither restart nor changing sessions resets it.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
import hashlib
import hmac
import json
import logging
from typing import Any, Iterator

import psycopg

from msfea_bot.config import settings
from msfea_bot.llm.base import LLMAdmissionError

_LOG = logging.getLogger(__name__)


def _connect() -> Any:
    return psycopg.connect(settings.database_url, connect_timeout=5)


def _cost(inputs: int, outputs: int, input_rate: float, output_rate: float) -> int:
    dollars = Decimal(inputs) * Decimal(str(input_rate)) + Decimal(outputs) * Decimal(str(output_rate))
    return int((dollars * 1000).to_integral_value(rounding=ROUND_CEILING))


def _event(conn: Any, reason: str) -> None:
    conn.execute(
        "INSERT INTO llm_guard_events (reason) VALUES (%s) ON CONFLICT (day,reason)"
        " DO UPDATE SET count=llm_guard_events.count+1", (reason,),
    )


def reserve(prompt: str, model: str, max_output: int, purpose: str, schema: Any = None) -> int:
    # A UTF-8 byte bound avoids an extra hosted tokenizer call. The allowance
    # also covers SDK/schema framing. Actual-bound violations trip the circuit.
    inputs = len(prompt.encode()) + len(json.dumps(schema).encode()) + 1024
    if inputs > 65536 or not 1 <= max_output <= 8192:
        raise LLMAdmissionError("Provider request exceeds the server allowance")
    if model == settings.llm_model:
        rates = (settings.llm_input_price_per_million, settings.llm_output_price_per_million)
    elif model == settings.curation_llm_model:
        rates = (settings.curation_input_price_per_million, settings.curation_output_price_per_million)
    else:
        raise LLMAdmissionError("No approved cost profile for this model")
    cost = _cost(inputs, max_output, *rates)
    tokens = inputs + max_output
    reason = ""
    try:
        with _connect() as conn:
            control = conn.execute("SELECT enabled,circuit_until FROM llm_control WHERE id=1 FOR UPDATE").fetchone()
            now = conn.execute("SELECT now(), (now() AT TIME ZONE 'UTC')::date").fetchone()
            if not settings.llm_calls_enabled or not control or not control[0]:
                reason = "paused"
            elif now[1] > settings.llm_price_valid_until:
                reason = "price_expired"
            elif control[1] and control[1] > now[0]:
                reason = "circuit_open"
            totals = conn.execute(
                "SELECT count(*),coalesce(sum(charged_tokens),0),coalesce(sum(charged_nano_usd),0)"
                " FROM llm_attempts WHERE day=%s", (now[1],),
            ).fetchone()
            active = conn.execute(
                "SELECT count(*) FROM llm_attempts WHERE outcome='reserved'"
                " AND started_at > now()-interval '120 seconds'"
            ).fetchone()[0]
            if not reason:
                if totals[0] >= settings.llm_daily_request_limit:
                    reason = "daily_requests"
                elif totals[1] + tokens > settings.llm_daily_token_limit:
                    reason = "daily_tokens"
                elif totals[2] + cost > int(Decimal(str(settings.llm_daily_cost_limit_usd)) * 10**9):
                    reason = "daily_cost"
                elif active >= settings.llm_global_concurrency:
                    reason = "concurrency"
            if reason:
                _event(conn, reason)
            else:
                row = conn.execute(
                    "INSERT INTO llm_attempts (model,purpose,charged_tokens,charged_nano_usd,"
                    " reserved_tokens,reserved_nano_usd,input_rate,output_rate)"
                    " VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    (model, purpose or "student", tokens, cost, tokens, cost, *rates),
                ).fetchone()
                if (totals[2] + cost >= settings.llm_daily_cost_limit_usd * 10**9 * 0.8
                        or totals[1] + tokens >= settings.llm_daily_token_limit * 0.8
                        or totals[0] + 1 >= settings.llm_daily_request_limit * 0.8):
                    _event(conn, "budget_near_limit")
                    _LOG.warning("paid_llm_budget_near_limit")
                return int(row[0])
        _LOG.warning("paid_llm_blocked reason=%s", reason)
        raise LLMAdmissionError("Paid answer service is paused or has reached its allowance")
    except psycopg.Error as exc:
        raise LLMAdmissionError("Paid-call accounting is unavailable") from exc


def settle(ticket: int, usage: Any) -> None:
    values: list[Any] = [getattr(usage, field, None) for field in
              ("prompt_token_count", "candidates_token_count", "total_token_count")]
    with _connect() as conn:
        conn.execute("SELECT id FROM llm_control WHERE id=1 FOR UPDATE")
        row = conn.execute(
            "SELECT reserved_tokens,reserved_nano_usd,input_rate,output_rate,finished_at"
            " FROM llm_attempts WHERE id=%s FOR UPDATE", (ticket,),
        ).fetchone()
        if not row or row[4]:
            return
        if any(value is None or not isinstance(value, int) or value < 0 for value in values):
            conn.execute("UPDATE llm_attempts SET outcome='unmeasured',finished_at=now() WHERE id=%s", (ticket,))
            return
        inputs, visible, total = (int(value) for value in values)
        if total < inputs + visible:
            conn.execute("UPDATE llm_attempts SET outcome='unmeasured',finished_at=now() WHERE id=%s", (ticket,))
            return
        reasoning = total - inputs - visible
        cost = _cost(inputs, visible + reasoning, float(row[2]), float(row[3]))
        conn.execute(
            "UPDATE llm_attempts SET outcome='completed',input_tokens=%s,visible_output_tokens=%s,"
            " reasoning_tokens=%s,charged_tokens=%s,charged_nano_usd=%s,finished_at=now() WHERE id=%s",
            (inputs, visible, reasoning, total, cost, ticket),
        )
        if total > row[0] or cost > row[1]:
            conn.execute("UPDATE llm_control SET enabled=false,reason='reservation_exceeded',changed_at=now() WHERE id=1")
            _event(conn, "reservation_exceeded")
            _LOG.error("paid_llm_reservation_exceeded")


def failed(ticket: int, error: BaseException) -> None:
    code = getattr(error, "code", None)
    reason = ("quota" if code == 429 else "payment" if code == 402
              else "configuration" if code in (401, 403, 404) else "provider_failure")
    with _connect() as conn:
        conn.execute("SELECT id FROM llm_control WHERE id=1 FOR UPDATE")
        conn.execute(
            "UPDATE llm_attempts SET outcome='failed',finished_at=now(),error_code=%s"
            " WHERE id=%s AND finished_at IS NULL", (reason, ticket),
        )
        failures = conn.execute(
            "SELECT count(*) FROM llm_attempts WHERE outcome='failed'"
            " AND started_at > now()-interval '120 seconds'"
        ).fetchone()[0]
        if code in (401, 402, 403, 404, 429) or failures >= 5:
            conn.execute("UPDATE llm_control SET circuit_until=now()+interval '120 seconds',reason=%s WHERE id=1", (reason,))
            _event(conn, "circuit_open")
            _LOG.warning("paid_llm_circuit_open reason=%s", reason)


@contextmanager
def attempt(prompt: str, model: str, max_output: int, purpose: str, schema: Any) -> Iterator[int]:
    ticket = reserve(prompt, model, max_output, purpose, schema)
    try:
        yield ticket
    except BaseException as exc:
        try:
            failed(ticket, exc)
        except psycopg.Error:
            # The original exception survives; its reservation stays charged.
            _LOG.error("paid_llm_failure_accounting_unavailable")
        raise


def set_enabled(enabled: bool) -> None:
    with _connect() as conn:
        conn.execute("UPDATE llm_control SET enabled=%s,changed_at=now(),reason='operator' WHERE id=1", (enabled,))
        _event(conn, "operator_resumed" if enabled else "operator_paused")
    _LOG.warning("paid_llm_operator_enabled=%s", enabled)


def admit_chat(ip: str, session: str | None) -> str | None:
    """Daily IP allowance and rolling 24-hour chat allowance; HMAC keys, no raw IPs."""
    secret = settings.admin_token or settings.llm_api_key
    checks = [("ip", ip, settings.ip_daily_request_limit)]
    if session:
        checks.append(("session", session, settings.session_question_limit))
    with _connect() as conn:
        conn.execute("SELECT id FROM llm_control WHERE id=1 FOR UPDATE")
        conn.execute("DELETE FROM abuse_counts WHERE expires_at <= now()")
        for kind, value, limit in checks:
            key = hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()
            row = conn.execute("SELECT count FROM abuse_counts WHERE kind=%s AND key=%s", (kind, key)).fetchone()
            if row and row[0] >= limit:
                _event(conn, kind + "_limit")
                return kind
        for kind, value, limit in checks:
            key = hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()
            expiry = "((now() AT TIME ZONE 'UTC')::date+1)::timestamp AT TIME ZONE 'UTC'" if kind == "ip" else "now()+interval '24 hours'"
            conn.execute(
                "INSERT INTO abuse_counts (kind,key,count,expires_at) VALUES (%s,%s,1," + expiry + ")"
                " ON CONFLICT (kind,key) DO UPDATE SET count=abuse_counts.count+1", (kind, key),
            )
    return None


def report() -> dict[str, Any]:
    """Operator-only aggregate metrics; never return prompts, keys or IP hashes."""
    with _connect() as conn:
        control = conn.execute("SELECT enabled,changed_at,circuit_until,reason FROM llm_control WHERE id=1").fetchone()
        rows = conn.execute(
            "SELECT day,model,purpose,count(*),coalesce(sum(input_tokens),0),"
            " coalesce(sum(visible_output_tokens),0),coalesce(sum(reasoning_tokens),0),"
            " sum(charged_tokens),sum(charged_nano_usd),count(*) FILTER (WHERE outcome<>'completed')"
            " FROM llm_attempts WHERE day >= (now() AT TIME ZONE 'UTC')::date-6"
            " GROUP BY day,model,purpose ORDER BY day DESC,model,purpose"
        ).fetchall()
        events = conn.execute(
            "SELECT day,reason,count FROM llm_guard_events WHERE day >= (now() AT TIME ZONE 'UTC')::date-6 ORDER BY day DESC,reason"
        ).fetchall()
    today = datetime.now(timezone.utc).date().isoformat()
    usage = [dict(day=r[0].isoformat(), model=r[1], purpose=r[2], requests=r[3], input_tokens=r[4],
                  visible_output_tokens=r[5], reasoning_tokens=r[6], charged_tokens=r[7],
                  charged_usd=float(r[8]) / 10**9, uncertain_attempts=r[9]) for r in rows]
    limits = dict(requests=settings.llm_daily_request_limit, tokens=settings.llm_daily_token_limit,
                  cost_usd=settings.llm_daily_cost_limit_usd, ip_requests=settings.ip_daily_request_limit,
                  chat_questions=settings.session_question_limit, concurrency=settings.llm_global_concurrency)
    return dict(day=today, enabled=bool(control and control[0] and settings.llm_calls_enabled),
                environment_enabled=settings.llm_calls_enabled, changed_at=control[1].isoformat(),
                circuit_until=control[2].isoformat() if control[2] else None, reason=control[3],
                price_valid_until=settings.llm_price_valid_until.isoformat(), limits=limits, usage=usage,
                events=[dict(day=r[0].isoformat(),reason=r[1],count=r[2]) for r in events])
