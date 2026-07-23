# ADR-0006 — Chunking: section-aware with size-bounded overlapping windows

**Status:** Accepted
**Date:** 2026-07-22
**Decision owner:** Jad Ghazi

## Context

The walking skeleton used a crude chunker that split only at Markdown headings.
Measured against the golden set, that left **context-recall@5 = 90%**: two facts
("75%" quiz score, "formal petition") were buried inside large section chunks
(the deliverables table, the requirements section), so their embeddings were
diluted and the answer-bearing chunk didn't reach the top-5. This caused two
false refusals in the answer eval (the bot correctly refused rather than
hallucinate — a *retrieval* failure, not a generation one).

## Options considered

1. **Section-only chunking (status quo).** Simple, but large sections bury
   specific facts → 90% context-recall@5.
2. **Fixed-size windows only (ignore structure).** Uniform sizes, but loses
   section boundaries/headings that make chunks self-describing.
3. **Section-aware + size-bounded windows with overlap.** Split at headings,
   then window any oversized section into <=`max_chars` pieces with overlap, each
   prefixed with its section heading. Chosen.

## Decision

Option 3. Window size chosen **empirically** by sweeping `max_chars` and measuring
context-recall (no LLM needed):

| max_chars | chunks | context-recall@3 | context-recall@5 |
|-----------|--------|------------------|------------------|
| ∞ (section-only) | 86 | 90% | 90% |
| 1000 | 98 | 90% | 90% |
| 700 | 113 | 95% | 95% |
| **500** | 144 | 95% | **100%** |
| 400 | 174 | 100% | 100% |

Default = **`max_chars=500`, `overlap=150`**: the *largest* window (most context
per chunk, least fragmentation) that still reaches 100% context-recall@5. 400
also reaches 100% but fragments more without operational benefit at k=5.

## Consequences

- Chunk count 86 → 144. **context-recall@5: 90% → 100%.** The two false refusals
  are fixed (confirmed end-to-end: both questions now answer correctly).
- Overlap (150) reduces the chance a fact is split across a window boundary.
- Every window keeps its section heading, so chunks stay self-describing (good
  for citations and for the LLM's context).
- Changing chunking requires re-embedding the KB (one ingestion rebuild).
- **Metric to watch:** context-recall (free, no LLM) is the tuning signal; it
  predicted the LLM false-refusals exactly, so we tune on it and confirm with an
  occasional answer eval. Defaults are tunable constants, not hard-coded.
