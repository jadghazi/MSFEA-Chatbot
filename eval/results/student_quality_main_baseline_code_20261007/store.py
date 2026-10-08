"""pgvector-backed vector store (AGENTS.md §3).

Stores chunks + embeddings in PostgreSQL and does top-k cosine similarity search.
The store is always rebuilt from source (TRUNCATE + insert), so it stays
reproducible and is never hand-edited.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
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
    get_model,
)
from msfea_bot.retrieval.repair import suggest_query, gains_lexical_support

KB_WRITE_LOCK_ID = 4_771_102_027


class GenerationChanged(RuntimeError):
    """The live KB changed after a rebuild snapshot was taken."""


@dataclass(frozen=True)
class PreparedChunk:
    chunk: Chunk
    vector: list[float]


@dataclass
class RetrievedChunk:
    """A chunk returned by search, with its similarity score (higher = closer)."""

    id: str
    text: str
    source_doc: str
    section: str
    score: float
    metadata: dict[str, str] = field(default_factory=dict)


def _connect(
    autocommit: bool = True,
    ensure_extension: bool = False,
    database_url: str | None = None,
) -> Any:
    """Connect (and register pgvector). Pass autocommit=False for a rebuild, so
    TRUNCATE + inserts land as one transaction instead of leaving a half-built
    index behind on failure."""
    conn = psycopg.connect(
        database_url or settings.database_url, autocommit=autocommit, connect_timeout=5
    )
    if ensure_extension:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def _init_schema(conn: Any, dim: int | None = None) -> None:
    dim = dim if dim is not None else embedding_dim()
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
    conn.execute("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS retrieval_text TEXT NOT NULL DEFAULT ''")
    # Display-only context (e.g. the header row of a split table), deliberately NOT
    # part of `text` so it reaches neither the embedding nor `tsv`. Prepended when a
    # chunk is read back. See Chunk.display_prefix for the measurements.
    conn.execute("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS display_prefix TEXT NOT NULL DEFAULT ''")
    # Chunk frontmatter (last_updated, program, department, ...). Department
    # scope is preserved here and enforced by search(); see ADR-0015/0025.
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
    # speed problem we do not have (AGENTS.md §2: no premature optimization).
    # Revisit if the KB grows past roughly 10k chunks or search latency becomes
    # visible; add the index THEN and re-measure context-recall, since an
    # approximate index can silently lower it.


def initialize_schema(database_url: str | None = None) -> None:
    """Create retrieval tables and execute the first embedding inference."""
    # Resolve the model dimension before holding a database connection through a
    # potentially slow cold model load.
    dim = embedding_dim()
    with _connect(ensure_extension=True, database_url=database_url) as conn:
        _init_schema(conn, dim)


def _generation_hash(chunks: list[Chunk]) -> str:
    payload = [
        {
            "id": chunk.id,
            "text": chunk.text,
            "source_doc": chunk.source_doc,
            "section": chunk.section,
            "metadata": chunk.metadata,
            "display_prefix": chunk.display_prefix,
            **({"retrieval_text": chunk.retrieval_text} if chunk.retrieval_text else {}),
        }
        for chunk in sorted(chunks, key=lambda item: item.id)
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def prepare_chunks(chunks: list[Chunk], reuse_database_url: str | None = None) -> list[PreparedChunk]:
    """Embed chunks before a short database write transaction begins."""
    reusable: dict[tuple[str, str], list[float]] = {}
    if reuse_database_url and indexed_model(reuse_database_url) == model_fingerprint():
        with _connect(database_url=reuse_database_url) as conn:
            rows = conn.execute("SELECT id, COALESCE(NULLIF(retrieval_text,''),text), embedding::real[] FROM chunks").fetchall()
        reusable = {(str(row[0]), str(row[1])): list(row[2]) for row in rows if row[2] is not None}
    missing = [chunk for chunk in chunks if (chunk.id, chunk.retrieval_text or chunk.text) not in reusable]
    vectors = embed_texts([chunk.retrieval_text or chunk.text for chunk in missing]) if missing else []
    reusable.update({(chunk.id, chunk.retrieval_text or chunk.text): vector for chunk, vector in zip(missing, vectors, strict=True)})
    return [PreparedChunk(chunk, reusable[(chunk.id, chunk.retrieval_text or chunk.text)]) for chunk in chunks]


def acquire_kb_write_lock(conn: Any) -> None:
    """Serialize publication, retirement, compensation, and full rebuild commits."""
    conn.execute("SELECT pg_advisory_xact_lock(%s)", (KB_WRITE_LOCK_ID,))


def generation_on_connection(conn: Any) -> str | None:
    row = conn.execute("SELECT value FROM index_meta WHERE key = 'kb_generation'").fetchone()
    return str(row[0]) if row else None


def replace_prepared_chunks(conn: Any, id_prefix: str, prepared: list[PreparedChunk]) -> None:
    """Replace one entry's chunks through the caller-owned transaction."""
    conn.execute("DELETE FROM chunks WHERE id LIKE %s", (id_prefix + "%",))
    with conn.cursor() as cur:
        for item in prepared:
            chunk = item.chunk
            cur.execute(
                "INSERT INTO chunks"
                " (id, text, source_doc, section, embedding, display_prefix, metadata, retrieval_text)"
                " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    chunk.id,
                    chunk.text,
                    chunk.source_doc,
                    chunk.section,
                    item.vector,
                    chunk.display_prefix,
                    Json(chunk.metadata),
                    chunk.retrieval_text,
                ),
            )


def refresh_generation(conn: Any) -> str:
    """Derive the generation from committed-intent chunk content in this transaction."""
    rows = conn.execute(
        "SELECT id, text, source_doc, section, metadata, display_prefix, retrieval_text"
        " FROM chunks ORDER BY id"
    ).fetchall()
    chunks = [
        Chunk(
            id=str(row[0]),
            text=str(row[1]),
            source_doc=str(row[2]),
            section=str(row[3]),
            metadata=dict(row[4]),
            display_prefix=str(row[5]),
            retrieval_text=str(row[6]),
        )
        for row in rows
    ]
    generation = _generation_hash(chunks)
    conn.execute(
        "INSERT INTO index_meta (key, value) VALUES ('kb_generation', %s)"
        " ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
        (generation,),
    )
    return generation


def index_chunks(
    chunks: list[Chunk],
    database_url: str | None = None,
    *,
    expected_generation: str | None = None,
    reuse_database_url: str | None = None,
) -> int:
    """Embed all chunks and (re)build the store atomically. Returns the number indexed.

    Embedding happens before the connection opens, so the slow part runs while the
    old index is still serving. The TRUNCATE and the inserts then commit as **one
    transaction**: under autocommit the TRUNCATE committed on its own, so a failure
    part-way through the insert loop left the live API answering from an empty or
    half-built index with no way to roll back.
    """
    prepared = prepare_chunks(chunks, reuse_database_url)
    with _connect(
        autocommit=False, ensure_extension=True, database_url=database_url
    ) as conn:
        _init_schema(conn)
        acquire_kb_write_lock(conn)
        if expected_generation is not None:
            actual = generation_on_connection(conn)
            if actual != expected_generation:
                raise GenerationChanged(
                    f"KB generation changed during rebuild (expected {expected_generation}, got {actual})"
                )
        conn.execute("TRUNCATE chunks")
        with conn.cursor() as cur:
            for item in prepared:
                chunk = item.chunk
                cur.execute(
                    "INSERT INTO chunks"
                    " (id, text, source_doc, section, embedding, display_prefix, metadata, retrieval_text)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        chunk.id,
                        chunk.text,
                        chunk.source_doc,
                        chunk.section,
                        item.vector,
                        chunk.display_prefix,
                        Json(chunk.metadata),
                        chunk.retrieval_text,
                    ),
                )
        conn.execute(
            "INSERT INTO index_meta (key, value) VALUES ('embedding_model', %s)"
            " ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
            (model_fingerprint(),),
        )
        conn.execute(
            "INSERT INTO index_meta (key, value) VALUES ('kb_generation', %s)"
            " ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
            (_generation_hash(chunks),),
        )
    return len(chunks)


def indexed_model(database_url: str | None = None) -> str | None:
    """The embedding model recorded for the current index, if any."""
    with _connect(database_url=database_url) as conn:
        row = conn.execute("SELECT value FROM index_meta WHERE key = 'embedding_model'").fetchone()
    return str(row[0]) if row else None


def indexed_generation(database_url: str | None = None) -> str | None:
    with _connect(database_url=database_url) as conn:
        row = conn.execute("SELECT value FROM index_meta WHERE key = 'kb_generation'").fetchone()
    return str(row[0]) if row else None


def index_is_ready() -> bool:
    """Whether the KB is populated with embeddings from this configured model."""
    with _connect() as conn:
        count_row = conn.execute("SELECT count(*) FROM chunks").fetchone()
        model_row = conn.execute(
            "SELECT value FROM index_meta WHERE key = 'embedding_model'"
        ).fetchone()
    count = int(count_row[0]) if count_row else 0
    indexed = str(model_row[0]) if model_row else None
    return count > 0 and indexed == model_fingerprint()


def upsert_chunks(chunks: list[Chunk]) -> int:
    """Embed and insert/update specific chunks without wiping the store.

    Used for incremental additions (e.g. a newly curated answer) so we don't have
    to rebuild the whole index. Returns the number upserted.
    """
    if not chunks:
        return 0
    prepared = prepare_chunks(chunks)
    with _connect(autocommit=False, ensure_extension=True) as conn:
        _init_schema(conn)
        acquire_kb_write_lock(conn)
        with conn.cursor() as cur:
            for item in prepared:
                chunk = item.chunk
                cur.execute(
                    "INSERT INTO chunks"
                    " (id, text, source_doc, section, embedding, display_prefix, metadata, retrieval_text)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    " ON CONFLICT (id) DO UPDATE SET"
                    " text = EXCLUDED.text, source_doc = EXCLUDED.source_doc,"
                    " section = EXCLUDED.section, embedding = EXCLUDED.embedding,"
                    " display_prefix = EXCLUDED.display_prefix,"
                    " metadata = EXCLUDED.metadata, retrieval_text = EXCLUDED.retrieval_text",
                    (
                        chunk.id,
                        chunk.text,
                        chunk.source_doc,
                        chunk.section,
                        item.vector,
                        chunk.display_prefix,
                        Json(chunk.metadata),
                        chunk.retrieval_text,
                    ),
                )
        refresh_generation(conn)
    return len(chunks)


def delete_chunk(chunk_id: str) -> int:
    """Delete a single chunk by exact id (e.g. one retired curated answer).

    Prefer this over `delete_chunks` when removing one known chunk — a prefix like
    "curated-1" would also match "curated-10".
    """
    with _connect(autocommit=False) as conn:
        acquire_kb_write_lock(conn)
        cur = conn.execute("DELETE FROM chunks WHERE id = %s", (chunk_id,))
        refresh_generation(conn)
        return int(cur.rowcount)


def delete_chunks(id_prefix: str) -> int:
    """Delete chunks whose id starts with `id_prefix` (bulk removal by source)."""
    with _connect(autocommit=False) as conn:
        acquire_kb_write_lock(conn)
        cur = conn.execute("DELETE FROM chunks WHERE id LIKE %s", (id_prefix + "%",))
        refresh_generation(conn)
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


def _normalize_quantity_spacing(query: str) -> str:
    """Separate joined quantities and units without splitting identifiers/course codes.

    Apply before both retrievers and numeric-intent detection so ``6weeks`` gets
    the same evidence as ``6 weeks``. The original student text remains in logs
    and in the generation prompt.
    """
    return re.sub(
        r"\b(\d+(?:\.\d+)?)(weeks?|days?|months?|years?|hours?|credits?|pages?|words?)\b",
        r"\1 \2", query, flags=re.IGNORECASE,
    )


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


def retrieval_depth(question: str, default_k: int) -> int:
    """Give explicit comparisons room for evidence from both sides (synthesis eval).

    Unconditionally raising k recovered the CO-OP waiver but distracted generation
    on a conditional rule. This cue is about question structure, never CDC topics.
    """
    if re.search(r"\b(compare|comparison|difference|versus|vs)\b", question, re.IGNORECASE):
        return max(default_k, 12)
    return default_k


# Chunks tagged with a specific department (see ingestion.chunking). Anything else
# — untagged, or the document-level default "all" — applies to every student.
_GENERAL = "(metadata->>'department' IS NULL OR metadata->>'department' = 'all')"
_NUMERIC_DECISION = re.compile(
    r"(?=.*\b\d+(?:\.\d+)?\b)"
    r"(?=.*\b(?:can|eligible|qualif\w*|register|enough|meet|satisfy)\b)",
    re.IGNORECASE,
)


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
    query: str,
    k: int = 5,
    candidates: int = 20,
    department: str | None = None,
    database_url: str | None = None,
    score_query: str | None = None,
    prefer_overview: bool = False,
    attribute_terms: tuple[str, ...] = (),
    topic_query: str = "",
    recover_typos: bool = True,
    excluded_stages: tuple[str, ...] = (),
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
    # Numeric rule-application questions need a wider *candidate* pool, not more
    # prompt chunks. Measured on the frozen sets: 40 recovers the previously passing
    # credit-threshold case with zero lost golden/synthesis/follow-up/scope cases.
    # The cue is question structure, not a hard-coded CDC topic or policy value.
    query = _normalize_quantity_spacing(query)
    if candidates == 20 and _NUMERIC_DECISION.search(query):
        candidates = 40
    # For a paired literal/contextual search, rank contextual candidates using
    # their resolved query but score every candidate against the CURRENT question.
    # Otherwise a high cosine to an unrelated earlier topic wins by construction.
    qv = embed_query(_normalize_quantity_spacing(score_query) if score_query else query)
    dept = departments.from_code(department)
    # The selected department is useful retrieval context, not just a filter.
    # Keep the original query vector for the calibrated similarity gate: adding
    # a department must not make an unrelated question appear in scope.
    ranking_vector = (
        embed_query(f"{query}\nDepartment: {dept.abbr}") if dept
        else embed_query(query) if score_query else qv
    )
    # Untrusted input: an unknown code degrades to no scoping rather than an error.
    #
    # Note: with NO department we deliberately leave department chunks in. Excluding
    # them was tried and measured worse — the golden case `dept-split-internship`
    # expects an unplaced student to still learn that the rule *depends* on their
    # department, and exclusion removes the only content that can say so.
    params: dict[str, Any] = {"qv": ranking_vector, "cand": candidates}
    if dept is None:
        scope = ""
    else:
        scope = f" WHERE ({_GENERAL} OR metadata->>'department' = %(dept)s)"
        params["dept"] = dept.code

    if excluded_stages:
        scope += (" AND " if scope else " WHERE ") + (
            "COALESCE(metadata->>'process_stage', '') <> ALL(%(excluded_stages)s)"
        )
        params["excluded_stages"] = list(excluded_stages)

    with _connect(database_url=database_url) as conn:
        vec_ids = [
            r[0]
            for r in conn.execute(
                f"SELECT id FROM chunks{scope}"
                " ORDER BY embedding <=> %(qv)s::vector, id LIMIT %(cand)s",
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
                        ", id"
                        " LIMIT %(cand)s",
                        {**params, "kwq": kwq},
                    ).fetchall()
                ]
            except psycopg.errors.Error:
                kw_ids = []  # degrade to vector-only on any tsquery hiccup (autocommit)
        rankings = [vec_ids, kw_ids]
        if attribute_terms and topic_query:
            # A conjunctive topic/attribute path complements broad OR recall.
            # Synonyms describe question attributes, never policy values/topics.
            attribute_tsquery = (
                f"({_keyword_tsquery(topic_query)}) & "
                f"({' | '.join(attribute_terms)})"
            )
            attribute_ids = [row[0] for row in conn.execute(
                "SELECT id FROM chunks WHERE tsv @@ to_tsquery('english', %(aq)s)"
                + (scope.replace(" WHERE ", " AND ") if scope else "")
                + " ORDER BY ts_rank_cd(tsv, to_tsquery('english', %(aq)s)) DESC, id"
                + " LIMIT %(cand)s", {**params, "aq": attribute_tsquery},
            ).fetchall()]
            if attribute_ids:
                rankings.append(attribute_ids)
        fused = reciprocal_rank_fusion(rankings)
        if not fused:
            return []
        # Keep the hybrid ranking as the backbone, but inspect its candidate pool
        # before truncating to k. A strong semantic match can otherwise land just
        # outside the prompt because broad OR keyword matches crowd the top slots.
        # Inspect at most 20 fused candidates; the prompt still receives k.
        pool = fused[:max(k, 20)] if dept is not None or prefer_overview else fused[:k]
        if prefer_overview:
            overview_scope = scope + " AND " if scope else " WHERE "
            overview_ids = [row[0] for row in conn.execute(
                "SELECT id FROM chunks" + overview_scope
                + "metadata->>'content_role' = 'overview'"
                + " ORDER BY embedding <=> %(qv)s::vector, id LIMIT 3", params,
            ).fetchall()]
            pool = list(dict.fromkeys(pool + overview_ids))
        rows = conn.execute(
            "SELECT id, text, source_doc, section,"
            " 1 - (embedding <=> %s::vector) AS score, display_prefix, metadata"
            " FROM chunks WHERE id = ANY(%s)",
            (qv, pool),
        ).fetchall()
        by_id = {r[0]: r for r in rows}
        if dept is not None:
            strongest = sorted(pool, key=lambda cid: float(by_id[cid][4]), reverse=True)[:min(2, k)]
            selected = fused[:k]
            additions = [cid for cid in strongest if cid not in selected]
            selected = selected[:k - len(additions)] + additions
            selected = _reserve_department_slot(
                conn, selected, vec_ids, kw_ids, dept.code, k
            )
            # The reserved department chunk can sit outside the fused pool.
            missing = [cid for cid in selected if cid not in by_id]
            if missing:
                extra = conn.execute(
                    "SELECT id, text, source_doc, section,"
                    " 1 - (embedding <=> %s::vector) AS score, display_prefix, metadata"
                    " FROM chunks WHERE id = ANY(%s)",
                    (qv, missing),
                ).fetchall()
                by_id.update({r[0]: r for r in extra})
        else:
            selected = fused[:k]
        if prefer_overview:
            # Broad orientation needs ordinary topic context alongside detailed
            # facts. Only reserve a reviewed overview already found by retrieval,
            # close to the strongest semantic hit; never force a topic allowlist.
            strongest_score = max((float(row[4]) for row in by_id.values()), default=0.0)
            overviews = [cid for cid in pool
                         if by_id[cid][6].get("content_role") == "overview"
                         and float(by_id[cid][4]) >= settings.similarity_threshold
                         and float(by_id[cid][4]) >= strongest_score - 0.10]
            if overviews:
                overview = max(overviews, key=lambda cid: float(by_id[cid][4]))
                selected = [overview] + [cid for cid in selected if cid != overview]
                selected = selected[:k]
                if dept is not None:
                    selected = _reserve_department_slot(conn, selected, vec_ids, kw_ids, dept.code, k)
    out: list[RetrievedChunk] = []
    for cid in selected:
        r = by_id.get(cid)
        if r is not None:
            text = _with_display_prefix(r[1], r[5])
            out.append(
                RetrievedChunk(
                    id=r[0],
                    text=text,
                    source_doc=r[2],
                    section=r[3],
                    score=float(r[4]),
                    metadata=dict(r[6]),
                )
            )
    if recover_typos and score_query is None and out:
        corrected = suggest_query(query, _source_vocabulary(
            database_url, indexed_generation(database_url), dept.code if dept else None,
        ), _known_word_tokens())
        if corrected:
            repaired = search(
                corrected, k, candidates, department, database_url,
                prefer_overview=prefer_overview, recover_typos=False,
                attribute_terms=attribute_terms, topic_query=topic_query,
                excluded_stages=excluded_stages,
            )
            best = max((chunk.score for chunk in repaired), default=0.0)
            lexical_gain = gains_lexical_support(
                query, corrected, [chunk.text for chunk in out], [chunk.text for chunk in repaired],
            )
            if (best >= settings.similarity_threshold
                    and (best >= max(chunk.score for chunk in out) + 0.06 or lexical_gain)):
                for chunk in repaired:
                    chunk.metadata = {**chunk.metadata, "query_correction": corrected,
                                      "original_query": query}
                return repaired
            if max(chunk.score for chunk in out) >= settings.similarity_threshold and k > 1:
                # A typo can produce a confident but wrong semantic match. Keep
                # the original gate/ranking backbone and add at most two canonical
                # passages supporting every unique one-edit correction. This is
                # query expansion, not a weaker threshold or silent intent rewrite.
                existing = {chunk.id for chunk in out}
                spelling_additions = [chunk for chunk in sorted(repaired, key=lambda c: c.score, reverse=True)
                             if chunk.id not in existing and gains_lexical_support(
                                 query, corrected, [], [chunk.text])][:min(2, k - 1)]
                if spelling_additions:
                    kept_chunks = out[:k - len(spelling_additions)]
                    strongest_chunk = max(out, key=lambda chunk: chunk.score)
                    if strongest_chunk.id not in {chunk.id for chunk in kept_chunks}:
                        kept_chunks[-1] = strongest_chunk
                    for chunk in spelling_additions:
                        chunk.metadata = {**chunk.metadata, "query_correction": corrected,
                                          "original_query": query,
                                          "retrieval_role": "spelling_candidate"}
                    return kept_chunks + spelling_additions
    return out


@lru_cache(maxsize=1)
def _known_word_tokens() -> frozenset[str]:
    """Protect common whole-word tokens in the existing pinned tokenizer.

    A tokenizer vocabulary is not a complete dictionary. This conservative guard
    prevents converting recognized words such as 'employed' into 'employer'.
    """
    return frozenset(word for word in get_model().tokenizer.get_vocab()
                     if re.fullmatch(r"[a-z]{5,}", word))


@lru_cache(maxsize=4)
def _source_vocabulary(
    database_url: str | None, generation: str | None, department: str | None,
) -> frozenset[str]:
    """Cache approved source words by index generation and department scope."""
    with _connect(database_url=database_url) as conn:
        scope = f" WHERE ({_GENERAL} OR metadata->>'department' = %s)" if department else ""
        rows = conn.execute("SELECT text FROM chunks" + scope,
                            (department,) if department else ()).fetchall()
    return frozenset(word.lower() for row in rows for word in re.findall(r"\b[A-Za-z]+\b", row[0]))


def expand_evidence_links(
    chunks: list[RetrievedChunk], query: str, department: str | None,
    database_url: str | None = None,
    excluded_stages: tuple[str, ...] = (),
) -> list[RetrievedChunk]:
    """Restore reviewed controlling context without replacing the retrieval seeds.

    Links refer to canonical source sections, not topic guesses or vector IDs.
    Expansion is one hop and department scoped. Companion scores cannot authorize
    generation; the caller still gates on the original retrieval seeds. Oversized
    complete bundles are handled by the existing context-size guard.
    """
    seeds = [chunk for chunk in chunks if chunk.metadata.get("retrieval_role") != "companion"]
    targets = {tuple(target.strip().split(" > ", 1)) for chunk in seeds
               for target in chunk.metadata.get("evidence_links", "").split(" | ") if target}
    targets = {target for target in targets if len(target) == 2}
    # A linked policy section is a coherent bundle. Its retrieved window may
    # contain a procedure while another window holds the actual restriction.
    # Restore its own canonical windows as well as its reviewed scoped links.
    targets.update((chunk.source_doc, chunk.section) for chunk in seeds
                   if chunk.metadata.get("evidence_links"))
    if not targets:
        return chunks
    dept = departments.from_code(department)
    # Relative heading paths omit the document title, which is display context.
    # Use an exact suffix boundary, not a substring or wildcard topic match.
    where = " OR ".join(
        "(source_doc = %s AND (section = %s OR right(section, length(%s) + 3) = ' > ' || %s))"
        for _ in targets
    )
    args: list[Any] = [embed_query(query)]
    for source, section in sorted(targets):
        args.extend((source, section, section, section))
    scope = f" AND ({_GENERAL} OR metadata->>'department' = %s)" if dept else ""
    if dept:
        args.append(dept.code)
    if excluded_stages:
        scope += " AND COALESCE(metadata->>'process_stage', '') <> ALL(%s)"
        args.append(list(excluded_stages))
    with _connect(database_url=database_url) as conn:
        rows = conn.execute(
            "SELECT id, text, source_doc, section, 1 - (embedding <=> %s::vector), "
            "display_prefix, metadata FROM chunks WHERE (" + where + ")" + scope
            + " ORDER BY source_doc, section, id", args,
        ).fetchall()
    seen = {chunk.id for chunk in chunks}
    companions = [RetrievedChunk(
        id=row[0], text=_with_display_prefix(row[1], row[5]), source_doc=row[2],
        section=row[3], score=float(row[4]),
        metadata={**row[6], "retrieval_role": "companion"},
    ) for row in rows if row[0] not in seen]
    return chunks + companions
