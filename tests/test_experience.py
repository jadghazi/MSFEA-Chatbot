"""Database-backed checks for anonymous experience feedback storage."""

import psycopg

from msfea_bot.config import settings
from msfea_bot.experience import initialize_schema, save_feedback, summary


def test_experience_feedback_persists_without_linkable_fields() -> None:
    initialize_schema()
    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute("TRUNCATE experience_feedback RESTART IDENTITY")
        columns = {
            row[0]
            for row in conn.execute(
                "SELECT column_name FROM information_schema.columns"
                " WHERE table_name = 'experience_feedback'"
            ).fetchall()
        }

    assert columns == {"id", "ts", "rating", "tags", "comment"}
    assert save_feedback(5, ["Answers were helpful", "Easy to use"], "Clear and useful.")
    data = summary()
    assert data["total"] == 1
    assert data["average_rating"] == 5.0
    assert data["rating_distribution"]["5"] == 1
    assert data["tag_counts"]["Easy to use"] == 1
    assert data["recent_comments"][0].comment == "Clear and useful."

    with psycopg.connect(settings.database_url, autocommit=True) as conn:
        conn.execute("TRUNCATE experience_feedback RESTART IDENTITY")
