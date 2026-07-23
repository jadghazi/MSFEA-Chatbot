"""Interaction logging in PostgreSQL (CLAUDE.md §5.9).

One row per interaction: the (already anonymized) question, whether the bot
refused, the answer, its citations, and the chunks retrieved. Logging is
**fail-safe** — if it errors, the chat still succeeds (logging must never break
the student's answer).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg

from msfea_bot.config import settings
from msfea_bot.generation.answer import Answer


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
        "  retrieved TEXT[] NOT NULL DEFAULT '{}'"
        ")"
    )


def log_interaction(question: str, answer: Answer) -> None:
    """Persist one interaction. Never raises — a logging failure must not break chat.

    `question` must already be anonymized (see observability.privacy).
    """
    try:
        with _connect() as conn:
            _init_schema(conn)
            conn.execute(
                "INSERT INTO interactions (question, refused, answer, citations, retrieved)"
                " VALUES (%s, %s, %s, %s, %s)",
                (question, answer.refused, answer.text, answer.citations, answer.retrieved),
            )
    except Exception as exc:  # noqa: BLE001 - fail-safe by design
        print(f"[observability] failed to log interaction: {exc}")


def recent_unanswered(limit: int = 50) -> list[tuple[datetime, str]]:
    """Recent escalated/refused questions — the roadmap for what KB content to add."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT ts, question FROM interactions WHERE refused ORDER BY ts DESC LIMIT %s",
            (limit,),
        ).fetchall()
    return [(row[0], row[1]) for row in rows]
