# ADR-0011 — Hybrid retrieval (semantic + keyword, RRF)

**Status:** Accepted
**Date:** 2026-07-27
**Decision owner:** Jad Ghazi

## Context

Retrieval was pure vector (cosine over pgvector). A real student question —
"what's the difference between an internship and a co-op?" — produced a correct
but *incomplete* answer: it covered co-op's duration/pay but missed that the
internship is a **graduation requirement** and co-op is **optional**. Diagnosis
(retrieval-before-generation, CLAUDE.md §2): the internship-side evidence chunk
sat at **vector rank ~40** for that query — both the question and the top chunks
were co-op-dominated, so the internship side was never retrieved. Pure embeddings
also blur exact tokens (course codes like `FEAA 500A`, "8 weeks").

A second, humbling finding: the golden set had **no cross-topic/comparison
cases**, so retrieval metrics read a false **100%** context-recall. The metric was
green because the test was incomplete, not because retrieval was perfect (§4).
This is Phase 5 (retrieval tuning), whose enhancements CLAUDE.md gates on a
*measured* need — which had now appeared.

## Decisions

**1. Fix the ruler first.** Added cross-topic/comparison + exact-term questions to
`golden_set.jsonl` (e.g. `internship-vs-coop`, `feaa500a`), with evidence aimed at
the *under-retrieved* side. Honest baseline then showed context-recall@5 = 97%
(one miss) instead of a fake 100%.

**2. Hybrid search — vector + Postgres full-text, fused with RRF.** Kept entirely
inside Postgres (no new service, fits the locked stack §3):
- A `tsv` STORED generated column (`to_tsvector('english', text)`) + GIN index,
  created idempotently in `_init_schema` (migrates existing tables).
- `search()` takes top-N from each retriever and fuses with **Reciprocal Rank
  Fusion** (c=60), returning top-k. Each returned chunk keeps its **cosine**
  `score`, so the generation similarity-threshold gate is unaffected.
- **Keyword uses OR semantics** (`to_tsquery('a | b | …')`), not AND. Postgres'
  `websearch/plainto_tsquery` AND every term, so a full-sentence question matched
  almost nothing (1 hit); OR-ing the words makes keyword a real recall booster.
  Query text is reduced to word tokens so the tsquery is always valid; any FTS
  error degrades to vector-only.

**3. Reranker — considered and declined (for now).** A cross-encoder could rerank
a wider candidate pool, but for a KB this small it adds a model download,
per-query latency, and Docker-image weight to rescue essentially one comparison
question. Not worth the cost at current scope. Revisit if the KB grows or
comparison questions become common.

**4. Query decomposition — backlogged (B-5).** The comparison question is hard
because one side is both semantically distant *and* lexically dominated; the
robust fix is to split such a question and retrieve each side separately. Deferred
until a measured need justifies the extra per-query LLM call.

## Consequences

- **Measured (expanded golden set, 29 answerable):** context-recall@1 **79% → 90%**,
  doc-recall@1 **83% → 90%**; context-recall@5 unchanged at **97%**; @3 dipped
  97% → 93% (some evidence chunks reordered within top-5, still retrieved by k=5).
  Net: markedly better top-rank precision, same top-5 coverage.
- The `internship-vs-coop` comparison **remains the one known miss** — kept in the
  golden set as an honest, tracked regression tripwire for when decomposition lands.
  Its failure mode is *incomplete*, not *wrong* (no hallucination).
- Retrieval stays reproducible and in-stack; the fusion function is pure and
  unit-tested; a DB-gated test proves keyword recall surfaces an exact token that
  embeddings rank poorly.
