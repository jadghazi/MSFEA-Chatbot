# ADR-0014 — Split-table headers are display context, not retrieval text

**Status:** Accepted
**Date:** 2026-07-30
**Decision owner:** Jad Ghazi

## Context

The checklist audit found that windowing splits markdown tables and carries only
the *section heading* forward, not the table's header row. Measured: **14 of 174
chunks (8%) contained table rows with no column labels.** The clearest case is the
internship deliverables timeline, where a chunk read:

```
| By the end of Week 4 | Progress Report | Submit a short report… | Moodle |
```

Nothing in that chunk says column 1 is a deadline and column 4 is where to submit.
The rubric tables in `internship-report-templates-and-rubrics.md` lose their
criterion/level headers the same way. Answers had been correct, so this was a
latent readability risk rather than a live bug — but "when is the progress report
due?" is exactly the kind of question a student asks.

## Options considered, with measurements

Baseline before any change: doc-recall @1/@3/@5 = 90/97/97%;
context-recall @1/@3/@5 = **90/93/97%**; one known miss (`internship-vs-coop`).

1. **Prepend header + `| --- |` separator into the chunk text.**
   → context-recall@5 **97% → 93%**. A *new* miss appeared: `int-skills-quiz`
   ("75%"), which is the very miss ADR-0006's windowing was built to fix. Repeating
   the same boilerplate in every window of a table makes those windows look alike
   and competes with the facts. **Rejected.**
2. **Prepend the header row only** (drop the separator as pure formatting noise).
   → context-recall@5 still **93%**, with a different new miss (`coop-pay`).
   Confirms the mechanism is dilution, not the separator. **Rejected.**
3. **Embed the raw window, store the header in `text` for display.**
   → context-recall@5 back to 97%, but **@1 90% → 83%**. Cause: the `tsv` full-text
   column is generated *from* `text`, so header words entered the keyword index and
   shifted RRF ranks. **Rejected.**
4. **Keep the header out of `text` entirely; store it in its own column and
   re-attach when reading.** Chosen.

## Decision

Option 4. `Chunk` gains `display_prefix`, persisted in a new
`chunks.display_prefix` column (added idempotently with `ADD COLUMN IF NOT EXISTS`,
matching the `tsv`/`rating` migration style).

- `text` remains the single **retrieval text** — it is what gets embedded *and*
  what `tsv` is generated from. It is byte-identical to the pre-change baseline,
  so retrieval behaviour is unchanged by construction rather than by luck.
- `search()` re-attaches the prefix via `_with_display_prefix`, placing it **after**
  the section heading (a bare table row above the heading reads as an orphan) and
  on top for curated chunks, which have no heading.

## Consequences

- **Zero retrieval cost, verified:** every metric is identical to baseline —
  doc-recall 90/97/97%, context-recall 90/93/97%, same single known miss. The
  readability fix is free.
- All 14 header-less chunks now present their column labels to the LLM.
- The generalisable rule: *presentational context that helps a reader is not
  automatically good retrieval text.* Anything added to `text` competes with the
  facts in the embedding and in the keyword index. Future additions of this kind
  (breadcrumbs, document titles, "context" preambles) should go through
  `display_prefix` and be measured, not assumed.
- Cost: one column, and a second place where chunk text is assembled. Accepted
  because options 1–3 all measurably degraded retrieval.
- The `internship-vs-coop` miss is untouched — still the tracked B-5 tripwire.
