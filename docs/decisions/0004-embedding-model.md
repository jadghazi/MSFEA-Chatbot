# ADR-0004 — Embedding model: local `bge-small-en-v1.5`

**Status:** Accepted
**Date:** 2026-07-22
**Decision owner:** Jad Ghazi

## Context

The RAG pipeline needs an embedding model to turn chunks (and queries) into
vectors for similarity search. CLAUDE.md §3 defaults to a local/open model so
there is no per-token cost and nothing external is required. The project is a
solo student's, optimized for low cost and modest hardware.

## Options considered

1. **Local `sentence-transformers`, `BAAI/bge-small-en-v1.5`.** Free, offline,
   no API key, 384-dim, small and CPU-friendly, strong quality-for-size. Cost:
   pulls in `torch` (a heavy dependency).
2. **Paid embedding API** (e.g. OpenAI `text-embedding-3-small`). Slightly
   better quality, trivial to call, but per-token cost + an external dependency +
   an API key — against the §3 default.
3. **Bigger local model** (`bge-base`/`bge-large`, `e5-large`). Higher quality
   but slower and heavier on RAM/CPU; overkill for a small KB on modest hardware.

## Decision

Option 1 — **`BAAI/bge-small-en-v1.5`** via `sentence-transformers`. Free,
private, no key, fast on CPU; the quality/size trade-off is right for this KB.
It is swappable behind the ingestion/retrieval code.

## Consequences

- Adds `sentence-transformers` (+ `torch`) — a large dependency, acceptable for a
  RAG project.
- Embeddings are **384-dimensional**; the pgvector column dimension must match.
- If retrieval recall on the eval set is weak, swap to `bge-base`/`e5` and
  **re-measure** — don't switch on a hunch (CLAUDE.md §2). Changing the model
  means re-embedding the KB (one ingestion rebuild).
- Everything runs locally; no student data leaves the machine at embedding time.
