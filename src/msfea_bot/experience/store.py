"""PostgreSQL storage for anonymous, conversation-independent experience feedback."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Any, TypedDict

import psycopg

from msfea_bot.config import settings

ALLOWED_TAGS = (
    "Answers were helpful",
    "Easy to use",
    "Information was unclear",
    "Could not find my answer",
    "Technical problem",
)


@dataclass(frozen=True)
class ExperienceComment:
    ts: datetime
    rating: int
    comment: str


class ExperienceSummary(TypedDict):
    total: int
    average_rating: float | None
    rating_distribution: dict[str, int]
    tag_counts: dict[str, int]
    recent_comments: list[ExperienceComment]


def _connect() -> Any:
    return psycopg.connect(settings.database_url, autocommit=True, connect_timeout=5)


_schema_ready = False
_schema_lock = Lock()


def _ensure_schema(conn: Any) -> None:
    global _schema_ready
    if _schema_ready:
        return
    with _schema_lock:
        if _schema_ready:
            return
        conn.execute(
            "CREATE TABLE IF NOT EXISTS experience_feedback ("
            " id BIGSERIAL PRIMARY KEY,"
            " ts TIMESTAMPTZ NOT NULL DEFAULT now(),"
            " rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),"
            " tags TEXT[] NOT NULL DEFAULT '{}',"
            " comment TEXT CHECK (char_length(comment) <= 500)"
            ")"
        )
        _schema_ready = True


def initialize_schema() -> None:
    """Create the additive feedback table during application startup."""
    if _schema_ready:
        return
    with _connect() as conn:
        _ensure_schema(conn)


def save_feedback(rating: int, tags: list[str], comment: str | None) -> bool:
    """Persist only explicitly anonymous fields; return False on a storage failure."""
    try:
        with _connect() as conn:
            _ensure_schema(conn)
            conn.execute(
                "INSERT INTO experience_feedback (rating, tags, comment) VALUES (%s, %s, %s)",
                (rating, tags, comment or None),
            )
        return True
    except Exception as exc:  # noqa: BLE001 - feedback must never affect chat availability
        print(f"[experience-feedback] failed to save: {exc}")
        return False


def summary(comment_limit: int = 20) -> ExperienceSummary:
    """Return concise pilot aggregates plus recent non-empty comments."""
    with _connect() as conn:
        _ensure_schema(conn)
        aggregate = conn.execute(
            "SELECT count(*), avg(rating),"
            " count(*) FILTER (WHERE rating = 1),"
            " count(*) FILTER (WHERE rating = 2),"
            " count(*) FILTER (WHERE rating = 3),"
            " count(*) FILTER (WHERE rating = 4),"
            " count(*) FILTER (WHERE rating = 5)"
            " FROM experience_feedback"
        ).fetchone()
        tag_rows = conn.execute(
            "SELECT tag, count(*) FROM experience_feedback, unnest(tags) AS tag"
            " GROUP BY tag"
        ).fetchall()
        comment_rows = conn.execute(
            "SELECT ts, rating, comment FROM experience_feedback"
            " WHERE comment IS NOT NULL AND btrim(comment) <> ''"
            " ORDER BY ts DESC LIMIT %s",
            (comment_limit,),
        ).fetchall()

    values = aggregate or (0, None, 0, 0, 0, 0, 0)
    return ExperienceSummary(
        total=int(values[0]),
        average_rating=round(float(values[1]), 2) if values[1] is not None else None,
        rating_distribution={str(i): int(values[i + 1] or 0) for i in range(1, 6)},
        tag_counts={tag: int(dict(tag_rows).get(tag, 0) or 0) for tag in ALLOWED_TAGS},
        recent_comments=[
            ExperienceComment(ts=row[0], rating=int(row[1]), comment=str(row[2]))
            for row in comment_rows
        ],
    )
