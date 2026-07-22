"""pgvector-backed vector store (CLAUDE.md §3).

Stores chunks + embeddings in PostgreSQL and does top-k cosine similarity search.
The store is always rebuilt from source (TRUNCATE + insert), so it stays
reproducible and is never hand-edited.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psycopg
from pgvector.psycopg import register_vector

from msfea_bot.config import settings
from msfea_bot.ingestion.chunking import Chunk
from msfea_bot.ingestion.embeddings import embed_query, embed_texts, embedding_dim


@dataclass
class RetrievedChunk:
    """A chunk returned by search, with its similarity score (higher = closer)."""

    id: str
    text: str
    source_doc: str
    section: str
    score: float


def _connect() -> Any:
    conn = psycopg.connect(settings.database_url, autocommit=True)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def _init_schema(conn: Any) -> None:
    dim = embedding_dim()
    conn.execute(
        f"CREATE TABLE IF NOT EXISTS chunks ("
        f"  id TEXT PRIMARY KEY,"
        f"  text TEXT NOT NULL,"
        f"  source_doc TEXT NOT NULL,"
        f"  section TEXT NOT NULL,"
        f"  embedding vector({dim})"
        f")"
    )


def index_chunks(chunks: list[Chunk]) -> int:
    """Embed all chunks and (re)build the store. Returns the number indexed."""
    vectors = embed_texts([c.text for c in chunks])
    with _connect() as conn:
        _init_schema(conn)
        conn.execute("TRUNCATE chunks")
        with conn.cursor() as cur:
            for chunk, vector in zip(chunks, vectors, strict=True):
                cur.execute(
                    "INSERT INTO chunks (id, text, source_doc, section, embedding)"
                    " VALUES (%s, %s, %s, %s, %s)",
                    (chunk.id, chunk.text, chunk.source_doc, chunk.section, vector),
                )
    return len(chunks)


def search(query: str, k: int = 5) -> list[RetrievedChunk]:
    """Return the top-k chunks most similar to the query (cosine similarity)."""
    qv = embed_query(query)
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, text, source_doc, section, 1 - (embedding <=> %s::vector) AS score"
            " FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s",
            (qv, qv, k),
        ).fetchall()
    return [
        RetrievedChunk(id=r[0], text=r[1], source_doc=r[2], section=r[3], score=float(r[4]))
        for r in rows
    ]
