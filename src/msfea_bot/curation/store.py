"""Storage for admin-curated answers (Postgres — ADR-0010).

Chosen over a markdown file because a live deployment's container filesystem is
ephemeral; Postgres has a persistent volume, is transactional, and is safe under
concurrent admin edits. This table is an ingestion *source*: the vector store is
rebuilt from the normalized markdown files PLUS these rows.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg

from msfea_bot.config import settings


@dataclass
class CuratedAnswer:
    id: int
    question: str
    answer: str
    author: str
    created_at: datetime
    active: bool


def _connect() -> Any:
    return psycopg.connect(settings.database_url, autocommit=True)


def _init_schema(conn: Any) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS curated_answers ("
        "  id BIGSERIAL PRIMARY KEY,"
        "  question TEXT NOT NULL,"
        "  answer TEXT NOT NULL,"
        "  author TEXT NOT NULL DEFAULT '',"
        "  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),"
        "  active BOOLEAN NOT NULL DEFAULT true"
        ")"
    )


def add_curated_answer(question: str, answer: str, author: str = "") -> int:
    with _connect() as conn:
        _init_schema(conn)
        row = conn.execute(
            "INSERT INTO curated_answers (question, answer, author)"
            " VALUES (%s, %s, %s) RETURNING id",
            (question, answer, author),
        ).fetchone()
    return int(row[0])


def list_curated(active_only: bool = True) -> list[CuratedAnswer]:
    where = "WHERE active" if active_only else ""
    with _connect() as conn:
        _init_schema(conn)
        rows = conn.execute(
            f"SELECT id, question, answer, author, created_at, active"
            f" FROM curated_answers {where} ORDER BY created_at DESC"
        ).fetchall()
    return [CuratedAnswer(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]
