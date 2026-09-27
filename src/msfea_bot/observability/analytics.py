"""Read-only dashboard aggregates over existing, anonymized interaction logs."""

from datetime import datetime, timedelta, timezone
from typing import Any

from msfea_bot.observability.store import _connect, _ensure_schema


def analytics(days: int = 30) -> dict[str, Any]:
    """Include today and the preceding days in UTC; no new student tracking."""
    if days not in (7, 30, 90):
        raise ValueError("days must be 7, 30 or 90")
    end = datetime.now(timezone.utc)
    start = end.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days - 1)
    bounds = (start, end)
    where = " WHERE ts >= %s AND ts <= %s"
    with _connect() as conn:
        _ensure_schema(conn)
        with conn.transaction():
            conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY")
            row = conn.execute(
                "SELECT count(*),"
                " count(*) FILTER (WHERE NOT refused AND error_code IS NULL),"
                " count(*) FILTER (WHERE refused AND error_code IS NULL),"
                " count(*) FILTER (WHERE error_code IS NOT NULL),"
                " count(*) FILTER (WHERE rating = 1),"
                " count(*) FILTER (WHERE rating = -1),"
                " count(*) FILTER (WHERE (refused OR rating = -1)"
                " AND error_code IS NULL AND resolved_at IS NULL),"
                " count(llm_latency_ms), avg(llm_latency_ms),"
                " percentile_cont(0.95) WITHIN GROUP (ORDER BY llm_latency_ms),"
                " count(*) FILTER (WHERE llm_input_tokens IS NOT NULL"
                " AND llm_output_tokens IS NOT NULL),"
                " sum(llm_input_tokens), sum(llm_output_tokens),"
                " count(*) FILTER (WHERE NOT refused AND error_code IS NULL"
                " AND cardinality(citations) > 0)"
                " FROM interactions" + where,
                bounds,
            ).fetchone()
            daily = conn.execute(
                "SELECT (ts AT TIME ZONE 'UTC')::date, count(*),"
                " count(*) FILTER (WHERE NOT refused AND error_code IS NULL),"
                " count(*) FILTER (WHERE refused AND error_code IS NULL),"
                " count(*) FILTER (WHERE error_code IS NOT NULL)"
                " FROM interactions" + where + " GROUP BY 1 ORDER BY 1",
                bounds,
            ).fetchall()
            gaps = conn.execute(
                "SELECT question, count(*), min(ts) FROM interactions"
                + where
                + " AND refused AND error_code IS NULL AND resolved_at IS NULL"
                " GROUP BY question ORDER BY count(*) DESC, min(ts), question LIMIT 5",
                bounds,
            ).fetchall()
            sources = conn.execute(
                "SELECT source, count(*) FROM ("
                " SELECT DISTINCT id, unnest(citations) AS source FROM interactions"
                + where
                + " AND NOT refused AND error_code IS NULL) AS cited"
                " GROUP BY source ORDER BY count(*) DESC, source LIMIT 5",
                bounds,
            ).fetchall()
            reasons = conn.execute(
                "SELECT coalesce(rating_reason, 'No reason given'), count(*)"
                " FROM interactions"
                + where
                + " AND rating = -1 GROUP BY 1 ORDER BY count(*) DESC, 1",
                bounds,
            ).fetchall()
    assert row is not None
    fields = (
        "total",
        "answered",
        "refused",
        "temporary_errors",
        "thumbs_up",
        "thumbs_down",
        "pending",
        "latency_samples",
        "avg_llm_latency_ms",
        "p95_llm_latency_ms",
        "token_samples",
        "llm_input_tokens",
        "llm_output_tokens",
        "answers_with_citations",
    )
    summary = {key: round(value) if value is not None else None for key, value in zip(fields, row)}
    by_day = {r[0]: r[1:] for r in daily}
    return {
        "days": days,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "timezone": "UTC",
        "summary": summary,
        "daily": [
            dict(
                zip(
                    ("date", "total", "answered", "refused", "temporary_errors"),
                    (day.isoformat(), *by_day.get(day, (0, 0, 0, 0))),
                )
            )
            for day in (start.date() + timedelta(days=i) for i in range(days))
        ],
        "unanswered": [{"question": q, "count": n, "oldest": ts.isoformat()} for q, n, ts in gaps],
        "sources": [{"source": source, "count": n} for source, n in sources],
        "negative_reasons": [{"reason": reason, "count": n} for reason, n in reasons],
    }
