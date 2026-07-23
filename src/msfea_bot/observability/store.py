"""Interaction logging in PostgreSQL (CLAUDE.md §5.9).

One row per interaction: the (already anonymized) question, whether the bot
refused, the answer, its citations, the chunks retrieved, and an optional
student rating (+1 / -1). Logging is **fail-safe** — if it errors, the chat still
succeeds (logging must never break the student's answer).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg

from msfea_bot.config import settings
from msfea_bot.generation.answer import Answer


@dataclass
class FeedbackItem:
    """An interaction that needs admin attention: refused or thumbs-down."""

    id: int
    ts: datetime
    question: str
    answer: str
    refused: bool
    rating: int | None
    retrieved: list[str]


def _connect() -> Any:
    return psycopg.connect(settings.database_url, autocommit=True)


def _init_schema(conn: Any) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS interactions ("
        "  id BIGSERIAL PRIMARY KEY,"
        "  ts TIMESTAMPTZ NOT NULL DEFAULT now(),"
        "  question TEXT NOT NULL,"
        "  refused BOOLEAN NOT NULL,"
        "  answer TEXT NOT NULL,"
        "  citations TEXT[] NOT NULL DEFAULT '{}',"
        "  retrieved TEXT[] NOT NULL DEFAULT '{}',"
        "  rating SMALLINT"
        ")"
    )
    # Migration for tables created before the rating column existed.
    conn.execute("ALTER TABLE interactions ADD COLUMN IF NOT EXISTS rating SMALLINT")


def log_interaction(question: str, answer: Answer) -> int | None:
    """Persist one interaction and return its id. Never raises (fail-safe).

    `question` must already be anonymized (see observability.privacy).
    """
    try:
        with _connect() as conn:
            _init_schema(conn)
            row = conn.execute(
                "INSERT INTO interactions (question, refused, answer, citations, retrieved)"
                " VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (question, answer.refused, answer.text, answer.citations, answer.retrieved),
            ).fetchone()
        return int(row[0]) if row else None
    except Exception as exc:  # noqa: BLE001 - fail-safe by design
        print(f"[observability] failed to log interaction: {exc}")
        return None


def set_rating(interaction_id: int, rating: int) -> bool:
    """Record a +1/-1 rating for an interaction. Returns True if a row was updated."""
    if rating not in (1, -1):
        raise ValueError("rating must be +1 or -1")
    try:
        with _connect() as conn:
            _init_schema(conn)
            cur = conn.execute(
                "UPDATE interactions SET rating = %s WHERE id = %s", (rating, interaction_id)
            )
            return bool(cur.rowcount > 0)
    except Exception as exc:  # noqa: BLE001 - non-critical; don't break the widget
        print(f"[observability] failed to set rating: {exc}")
        return False


def recent_unanswered(limit: int = 50) -> list[tuple[datetime, str]]:
    """Recent escalated/refused questions — the roadmap for what KB content to add."""
    with _connect() as conn:
        _init_schema(conn)
        rows = conn.execute(
            "SELECT ts, question FROM interactions WHERE refused ORDER BY ts DESC LIMIT %s",
            (limit,),
        ).fetchall()
    return [(row[0], row[1]) for row in rows]


def stats() -> dict[str, int]:
    """Aggregate usage counts for the admin dashboard (no student-identifying data)."""
    with _connect() as conn:
        _init_schema(conn)
        row = conn.execute(
            "SELECT count(*),"
            " count(*) FILTER (WHERE refused),"
            " count(*) FILTER (WHERE rating = 1),"
            " count(*) FILTER (WHERE rating = -1)"
            " FROM interactions"
        ).fetchone()
    vals = row or (0, 0, 0, 0)
    total, refused, up, down = int(vals[0]), int(vals[1]), int(vals[2]), int(vals[3])
    return {
        "total": total,
        "answered": total - refused,
        "refused": refused,
        "thumbs_up": up,
        "thumbs_down": down,
    }


def feedback_items(limit: int = 100) -> list[FeedbackItem]:
    """Interactions that need admin attention: refused OR thumbs-down."""
    with _connect() as conn:
        _init_schema(conn)
        rows = conn.execute(
            "SELECT id, ts, question, answer, refused, rating, retrieved"
            " FROM interactions WHERE refused OR rating = -1"
            " ORDER BY ts DESC LIMIT %s",
            (limit,),
        ).fetchall()
    return [FeedbackItem(r[0], r[1], r[2], r[3], r[4], r[5], list(r[6])) for r in rows]
