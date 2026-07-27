"""pgvector-backed vector store (CLAUDE.md §3).

Stores chunks + embeddings in PostgreSQL and does top-k cosine similarity search.
The store is always rebuilt from source (TRUNCATE + insert), so it stays
reproducible and is never hand-edited.
"""

from __future__ import annotations

import re
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
    # Full-text column for the keyword half of hybrid search (ADR-0011). A STORED
    # generated column stays in sync with `text` automatically; the GIN index makes
    # the keyword query fast.
    conn.execute(
        "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS tsv tsvector"
        " GENERATED ALWAYS AS (to_tsvector('english', text)) STORED"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING GIN (tsv)")


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


def upsert_chunks(chunks: list[Chunk]) -> int:
    """Embed and insert/update specific chunks without wiping the store.

    Used for incremental additions (e.g. a newly curated answer) so we don't have
    to rebuild the whole index. Returns the number upserted.
    """
    if not chunks:
        return 0
    vectors = embed_texts([c.text for c in chunks])
    with _connect() as conn:
        _init_schema(conn)
        with conn.cursor() as cur:
            for chunk, vector in zip(chunks, vectors, strict=True):
                cur.execute(
                    "INSERT INTO chunks (id, text, source_doc, section, embedding)"
                    " VALUES (%s, %s, %s, %s, %s)"
                    " ON CONFLICT (id) DO UPDATE SET"
                    " text = EXCLUDED.text, source_doc = EXCLUDED.source_doc,"
                    " section = EXCLUDED.section, embedding = EXCLUDED.embedding",
                    (chunk.id, chunk.text, chunk.source_doc, chunk.section, vector),
                )
    return len(chunks)


def delete_chunk(chunk_id: str) -> int:
    """Delete a single chunk by exact id (e.g. one retired curated answer).

    Prefer this over `delete_chunks` when removing one known chunk — a prefix like
    "curated-1" would also match "curated-10".
    """
    with _connect() as conn:
        cur = conn.execute("DELETE FROM chunks WHERE id = %s", (chunk_id,))
        return int(cur.rowcount)


def delete_chunks(id_prefix: str) -> int:
    """Delete chunks whose id starts with `id_prefix` (bulk removal by source)."""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM chunks WHERE id LIKE %s", (id_prefix + "%",))
        return int(cur.rowcount)


def _keyword_tsquery(text: str) -> str:
    """Build an OR tsquery ("a | b | c") from a natural-language question.

    Postgres' websearch/plainto_tsquery AND all terms, so a full-sentence question
    matches almost nothing (every word must be present). OR-ing the words instead
    makes keyword search a real recall booster, ranked by ts_rank_cd. Non-word
    characters are stripped so the terms are always valid tsquery input.
    """
    tokens = re.findall(r"[A-Za-z0-9]+", text.lower())
    return " | ".join(tokens)


def reciprocal_rank_fusion(rankings: list[list[str]], c: int = 60) -> list[str]:
    """Fuse several ranked id-lists into one, via Reciprocal Rank Fusion (RRF).

    Each list contributes 1/(c + rank) to an id's score (rank is 1-based), so an
    id ranked well by *either* retriever floats up, and ids ranked by both win.
    `c` damps the influence of very high ranks (60 is the common default). Ties
    keep the order of the first list (our primary/semantic signal).
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (c + rank)
    return sorted(scores, key=lambda i: scores[i], reverse=True)


def search(query: str, k: int = 5, candidates: int = 20) -> list[RetrievedChunk]:
    """Hybrid retrieval: fuse semantic (vector) and keyword (full-text) rankings.

    Pure embeddings blur exact terms (course codes, "8 weeks"); pure keyword misses
    paraphrases. We take the top-`candidates` from each and fuse with RRF, then
    return the top-`k`. Each returned chunk still carries its cosine `score`, so the
    generation similarity-threshold gate is unaffected (ADR-0011).
    """
    qv = embed_query(query)
    with _connect() as conn:
        vec_ids = [
            r[0]
            for r in conn.execute(
                "SELECT id FROM chunks ORDER BY embedding <=> %s::vector LIMIT %s",
                (qv, candidates),
            ).fetchall()
        ]
        kwq = _keyword_tsquery(query)
        kw_ids: list[str] = []
        if kwq:
            try:
                kw_ids = [
                    r[0]
                    for r in conn.execute(
                        "SELECT id FROM chunks WHERE tsv @@ to_tsquery('english', %s)"
                        " ORDER BY ts_rank_cd(tsv, to_tsquery('english', %s)) DESC LIMIT %s",
                        (kwq, kwq, candidates),
                    ).fetchall()
                ]
            except psycopg.errors.Error:
                kw_ids = []  # degrade to vector-only on any tsquery hiccup (autocommit)
        fused = reciprocal_rank_fusion([vec_ids, kw_ids])[:k]
        if not fused:
            return []
        # Fetch content + cosine score for the fused ids in one query.
        rows = conn.execute(
            "SELECT id, text, source_doc, section, 1 - (embedding <=> %s::vector) AS score"
            " FROM chunks WHERE id = ANY(%s)",
            (qv, fused),
        ).fetchall()
    by_id = {r[0]: r for r in rows}
    out: list[RetrievedChunk] = []
    for cid in fused:  # preserve fused (RRF) order
        r = by_id.get(cid)
        if r is not None:
            out.append(
                RetrievedChunk(id=r[0], text=r[1], source_doc=r[2], section=r[3], score=float(r[4]))
            )
    return out
