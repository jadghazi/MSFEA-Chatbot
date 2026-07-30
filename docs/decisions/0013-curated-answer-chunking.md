# ADR-0013 — Curated answers go through the same windowing as KB content

**Status:** Accepted
**Date:** 2026-07-30
**Decision owner:** Jad Ghazi

## Context

Admin-curated answers (ADR-0010) were indexed as **one chunk each**:
`_to_chunk` built a single `Chunk` from `f"Q: {question}\nA: {answer}"` and never
touched the windowing path that KB documents go through (ADR-0006).

The checklist audit flagged this as inconsistent. Measuring it showed it is worse
than inconsistent — it is **silent data loss in the retrieval index**:

- `bge-small-en-v1.5` has `max_seq_length = 512` tokens; anything past that is
  dropped at embedding time, without warning.
- `CurateRequest` allows an 8000-char answer (`api/app.py`). Measured: 8000 chars
  tokenizes to **1302 tokens, of which only 512 are embedded — ~39%, about the
  first 3,143 characters**.
- The remaining ~61% was still stored in `curated_answers` and still shown to the
  LLM *if the chunk was retrieved*, but **no query could ever match on it**.

This hits exactly the content staff write to *fix* a known retrieval failure, and it
reintroduces the dilution problem ADR-0006 already solved for KB documents. Nothing
in the eval could catch it: the curated eval case only checks that the answer is
still retrievable by its own question, which matches on the head of the text.

A second defect surfaced while fixing it. `split_windows` splits only on newlines,
so a **run-on paragraph — exactly what the dashboard textarea produces — came back
as a single oversized window** (verified: 5,520 chars in, one window out). Windowing
alone would not have fixed the truncation.

## Options considered

1. **Cap `CurateRequest.answer` below 512 tokens.** Trivial, but pushes the problem
   onto staff and silently forbids thorough answers.
2. **Reuse `chunk_markdown`.** Correct rules, but it generates its own
   `{source_doc}#{n}-{slug}` ids, which breaks the `curated-<id>` linkage that
   edit/retire depend on.
3. **Reuse the windowing primitive with curation's own id scheme.** Chosen.

## Decision

Option 3.

- `_split_windows` is promoted to public **`split_windows`** in
  `ingestion/chunking.py` — one windowing implementation, two callers, no
  duplicated rules. Its docstring now warns that it needs line boundaries.
- `_to_chunks` (plural) windows each curated answer at the KB defaults
  (`DEFAULT_MAX_CHARS=500`, `DEFAULT_OVERLAP=150`) and repeats the question on
  every window, mirroring how KB windows repeat their section heading, so each
  chunk stays self-describing.
- **`_as_lines` normalizes run-on text first**, breaking after sentence endings so
  the windower has boundaries. It never cuts mid-sentence.
- The question header is capped at 300 chars so header + window cannot approach the
  512-token limit even for a pathologically long question. The full question is
  always preserved in the `curated_answers` row.

**Chunk ids become `curated-<id>-<nn>`.** The trailing `-` before the index is
load-bearing: it makes `curated-1-` an unambiguous delete prefix that cannot match
`curated-10-`. That collision is the precise footgun `delete_chunk` was added to
avoid, and multi-chunk answers reintroduce the need for prefix deletes.

**Edit deletes before upserting.** A shorter edit produces fewer windows, and an
upsert alone would leave the surplus windows behind as retrievable stale content.
`_drop_chunks` also clears the pre-ADR-0013 `curated-<id>` id so answers indexed
under the old scheme don't linger after an edit or retire.

## Consequences

- A long curated answer is now fully retrievable. Verified: an 8000-char run-on
  answer produces **17 chunks, max 110 tokens each**, and a marker in the final
  sentence is searchable — where before it was unreachable.
- Short answers (the common case) still produce exactly one chunk, so nothing
  changes for existing content in practice.
- **KB chunking is untouched.** The sentence-normalization step lives in curation,
  not in `split_windows`, deliberately: applying it to KB text could split markdown
  table rows and shift context-recall. KB behaviour is byte-identical, so this
  change needs no re-ingest to be safe.
- **A test-teardown leak was found and fixed as part of this.** The existing
  integration tests tore down with `delete_chunk(f"curated-{id}")`, which no longer
  matches windowed ids — so running them left `curated-<id>-00` chunks live in the
  store. Two such orphans were found in the dev database and removed. Teardowns now
  call the service's own `_drop_chunks`, so there is one cleanup path rather than a
  hand-written copy that can drift. This is the same class of leak that previously
  put `zzz-test` placeholder text into retrievable content.
- The one pre-existing curated row still carries a legacy `curated-<id>` chunk id;
  the next full `skeleton ingest` re-chunks it under the new scheme (the rebuild
  truncates), and `_drop_chunks` handles it correctly in the meantime.
