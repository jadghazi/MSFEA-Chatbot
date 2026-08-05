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
from psycopg.types.json import Json

from msfea_bot import departments
from msfea_bot.config import settings
from msfea_bot.ingestion.chunking import Chunk
from msfea_bot.ingestion.embeddings import (
    embed_query,
    embed_texts,
    embedding_dim,
    model_fingerprint,
)


@dataclass
class RetrievedChunk:
    """A chunk returned by search, with its similarity score (higher = closer)."""

    id: str
    text: str
    source_doc: str
    section: str
    score: float


def _connect(autocommit: bool = True) -> Any:
    """Connect (and register pgvector). Pass autocommit=False for a rebuild, so
    TRUNCATE + inserts land as one transaction instead of leaving a half-built
    index behind on failure."""
    conn = psycopg.connect(settings.database_url, autocommit=autocommit)
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
    # Display-only context (e.g. the header row of a split table), deliberately NOT
    # part of `text` so it reaches neither the embedding nor `tsv`. Prepended when a
    # chunk is read back. See Chunk.display_prefix for the measurements.
    conn.execute("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS display_prefix TEXT NOT NULL DEFAULT ''")
    # Chunk frontmatter (last_updated, program, department, ...). Backlog B-2 asks
    # for this slot to be reserved NOW because retrofitting it once the index exists
    # is expensive; department-scoped *filtering* is the v2 feature, not this column.
    conn.execute(
        "ALTER TABLE chunks ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::jsonb"
    )
    # Which embedding model produced these vectors. Without it, querying with a
    # different model than the one indexed is silent — dimensions still match, only
    # the answers get quietly worse.
    conn.execute(
        "CREATE TABLE IF NOT EXISTS index_meta ("
        "  key TEXT PRIMARY KEY,"
        "  value TEXT NOT NULL,"
        "  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()"
        ")"
    )
    # NOTE: there is deliberately NO index on `embedding` (no HNSW/IVFFlat). At this
    # corpus size (~175 chunks) pgvector's exact sequential scan is sub-millisecond
    # and returns 100% recall, whereas HNSW/IVFFlat are approximate — they would
    # trade recall away and add tuning knobs (m, ef_construction, lists) to solve a
    # speed problem we do not have (CLAUDE.md §2: no premature optimization).
    # Revisit if the KB grows past roughly 10k chunks or search latency becomes
    # visible; add the index THEN and re-measure context-recall, since an
    # approximate index can silently lower it.


def index_chunks(chunks: list[Chunk]) -> int:
    """Embed all chunks and (re)build the store atomically. Returns the number indexed.

    Embedding happens before the connection opens, so the slow part runs while the
    old index is still serving. The TRUNCATE and the inserts then commit as **one
    transaction**: under autocommit the TRUNCATE committed on its own, so a failure
    part-way through the insert loop left the live API answering from an empty or
    half-built index with no way to roll back.
    """
    vectors = embed_texts([c.text for c in chunks])
    with _connect(autocommit=False) as conn:
        _init_schema(conn)
        conn.execute("TRUNCATE chunks")
        with conn.cursor() as cur:
            for chunk, vector in zip(chunks, vectors, strict=True):
                cur.execute(
                    "INSERT INTO chunks"
                    " (id, text, source_doc, section, embedding, display_prefix, metadata)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        chunk.id,
                        chunk.text,
                        chunk.source_doc,
                        chunk.section,
                        vector,
                        chunk.display_prefix,
                        Json(chunk.metadata),
                    ),
                )
        conn.execute(
            "INSERT INTO index_meta (key, value) VALUES ('embedding_model', %s)"
            " ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
            (model_fingerprint(),),
        )
    return len(chunks)


def indexed_model() -> str | None:
    """The embedding model recorded for the current index, if any."""
    with _connect() as conn:
        row = conn.execute("SELECT value FROM index_meta WHERE key = 'embedding_model'").fetchone()
    return str(row[0]) if row else None


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
                    "INSERT INTO chunks"
                    " (id, text, source_doc, section, embedding, display_prefix, metadata)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    " ON CONFLICT (id) DO UPDATE SET"
                    " text = EXCLUDED.text, source_doc = EXCLUDED.source_doc,"
                    " section = EXCLUDED.section, embedding = EXCLUDED.embedding,"
                    " display_prefix = EXCLUDED.display_prefix,"
                    " metadata = EXCLUDED.metadata",
                    (
                        chunk.id,
                        chunk.text,
                        chunk.source_doc,
                        chunk.section,
                        vector,
                        chunk.display_prefix,
                        Json(chunk.metadata),
                    ),
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


def _with_display_prefix(text: str, prefix: str) -> str:
    """Re-attach display-only context (a split table's header row) when reading.

    Placed *after* the section heading, not above it: KB chunks start with their
    heading, and a bare table row sitting above it reads as an orphan. Curated
    chunks have no heading, so the prefix goes on top.
    """
    if not prefix:
        return text
    head, newline, rest = text.partition("\n")
    if not head.lstrip().startswith("#"):
        return f"{prefix}\n{text}"
    return f"{head}\n{prefix}\n{rest}" if newline else f"{head}\n{prefix}"


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


# Chunks tagged with a specific department (see ingestion.chunking). Anything else
# — untagged, or the document-level default "all" — applies to every student.
_GENERAL = "(metadata->>'department' IS NULL OR metadata->>'department' = 'all')"


def _reserve_department_slot(
    conn: Any,
    fused: list[str],
    vec_ids: list[str],
    kw_ids: list[str],
    dept_code: str,
    k: int,
) -> list[str]:
    """Ensure the student's own department rule is present, if it is relevant at all.

    Only promotes a chunk that already reached the candidate pool, so an irrelevant
    department rule is never forced in: relevance is still decided by retrieval, this
    just stops a relevant one being crowded out of the last slot by general content.
    Costs at most one of `k` slots.
    """
    pool = list(dict.fromkeys(vec_ids + kw_ids))  # candidate ids, best vector rank first
    if not pool:
        return fused
    rows = conn.execute(
        "SELECT id FROM chunks WHERE id = ANY(%s) AND metadata->>'department' = %s",
        (pool, dept_code),
    ).fetchall()
    dept_ids = {r[0] for r in rows}
    if not dept_ids or any(cid in dept_ids for cid in fused):
        return fused  # nothing relevant, or already represented
    best = next(cid for cid in pool if cid in dept_ids)
    return fused[: k - 1] + [best]


def search(
    query: str, k: int = 5, candidates: int = 20, department: str | None = None
) -> list[RetrievedChunk]:
    """Hybrid retrieval: fuse semantic (vector) and keyword (full-text) rankings.

    Pure embeddings blur exact terms (course codes, "8 weeks"); pure keyword misses
    paraphrases. We take the top-`candidates` from each and fuse with RRF, then
    return the top-`k`. Each returned chunk still carries its cosine `score`, so the
    generation similarity-threshold gate is unaffected (ADR-0011).

    `department` scopes the result to one student (ADR-0015). Two things happen:

    1. **Other departments are excluded.** MECH's rules can never be the right answer
       for a CEE student, and leaving them in actively misleads — measured on the real
       KB, "can I split my internship into two 4-week periods?" returns four different
       departments' contradictory rules in the top-5.
    2. **One slot is reserved for the student's own department**, when a rule of theirs
       is relevant enough to reach the candidate pool but not the top-k. This is the
       case exclusion alone does not fix: for "do I need to give a final presentation?"
       the IEM chunk — which says presentations are generally *not* required — sits at
       vector rank 8, so an IEM student would otherwise be told the general rule, which
       is wrong for them. Bounded to a single slot so it can displace at most one
       general chunk.
    """
    qv = embed_query(query)
    dept = departments.from_code(department)
    # Untrusted input: an unknown code degrades to no scoping rather than an error.
    #
    # Note: with NO department we deliberately leave department chunks in. Excluding
    # them was tried and measured worse — the golden case `dept-split-internship`
    # expects an unplaced student to still learn that the rule *depends* on their
    # department, and exclusion removes the only content that can say so.
    params: dict[str, Any] = {"qv": qv, "cand": candidates}
    if dept is None:
        scope = ""
    else:
        scope = f" WHERE ({_GENERAL} OR metadata->>'department' = %(dept)s)"
        params["dept"] = dept.code

    with _connect() as conn:
        vec_ids = [
            r[0]
            for r in conn.execute(
                f"SELECT id FROM chunks{scope}"
                " ORDER BY embedding <=> %(qv)s::vector LIMIT %(cand)s",
                params,
            ).fetchall()
        ]
        kwq = _keyword_tsquery(query)
        kw_ids: list[str] = []
        if kwq:
            try:
                kw_scope = scope.replace(" WHERE ", " AND ") if scope else ""
                kw_ids = [
                    r[0]
                    for r in conn.execute(
                        "SELECT id FROM chunks"
                        " WHERE tsv @@ to_tsquery('english', %(kwq)s)" + kw_scope +
                        " ORDER BY ts_rank_cd(tsv, to_tsquery('english', %(kwq)s)) DESC"
                        " LIMIT %(cand)s",
                        {**params, "kwq": kwq},
                    ).fetchall()
                ]
            except psycopg.errors.Error:
                kw_ids = []  # degrade to vector-only on any tsquery hiccup (autocommit)
        fused = reciprocal_rank_fusion([vec_ids, kw_ids])[:k]
        if dept is not None:
            fused = _reserve_department_slot(conn, fused, vec_ids, kw_ids, dept.code, k)
        if not fused:
            return []
        # Fetch content + cosine score for the fused ids in one query.
        rows = conn.execute(
            "SELECT id, text, source_doc, section,"
            " 1 - (embedding <=> %s::vector) AS score, display_prefix"
            " FROM chunks WHERE id = ANY(%s)",
            (qv, fused),
        ).fetchall()
    by_id = {r[0]: r for r in rows}
    out: list[RetrievedChunk] = []
    for cid in fused:  # preserve fused (RRF) order
        r = by_id.get(cid)
        if r is not None:
            text = _with_display_prefix(r[1], r[5])
            out.append(
                RetrievedChunk(
                    id=r[0], text=text, source_doc=r[2], section=r[3], score=float(r[4])
                )
            )
    return out
