# ADR-0017 — Tables are atomic chunks

**Status:** Accepted
**Date:** 2026-08-05
**Decision owner:** Jad Ghazi

Supersedes the table-header half of **ADR-0014** (split-table headers carried as
`display_prefix`), which treated the symptom rather than the cause.

## Context

Asked "what are the deliverables", the bot listed 6 of the 9 rows in the internship
deliverables table. It was not trimming to be brief and it was not hallucinating:
**the missing rows were never retrieved.**

The chunker split that 9-row table into **6 windows** of ~500 chars. All six carry
the same heading, so they are near-identical to the retriever and compete with each
other for the same top-k slots. Measured for that question at k=7:

- 3 slots went to CO-OP content
- 4 slots went to internship table fragments
- the fragment holding **Progress Report** ranked **18th**

Retrieval cannot reassemble a table it has already torn apart. Windowing also caused
the earlier defect ADR-0014 patched: a window starting mid-table shows unlabelled
columns, so the header had to be carried separately as display-only context.

## Decision

**A window boundary may never fall inside a markdown table.** `_unbreakable_lines`
marks every line after a table's header row as un-cuttable; `_window_spans` skips
those cut points and lets the window run past `max_chars` until the table ends. The
overlap step-back is likewise forbidden from landing mid-table.

Cutting *at* a header row stays legal — that begins a fresh table.

## Consequences

Measured on the real KB:

| | Before | After |
|---|---|---|
| Deliverables table | 6 chunks | **1 chunk, all 9 rows** |
| Chunks with table rows but no header | 14 (audit finding) | **0** |
| Deliverables answer | 6/9 rows | **9/9 rows** |
| Total chunks | 175 | 164 |

**A regression appeared and was fixed rather than accepted.** Making the table atomic
buried the "75%" quiz score inside a 1,934-char chunk, diluting its embedding —
exactly the failure ADR-0006 introduced windowing to solve. Context-recall@7 fell
97% → 95%.

The fix was content, not structure: the KB has a "Quick Reference: Key Numbers"
section built for precisely this kind of specific-fact lookup, and the quiz score was
missing from it. Adding it restored **context-recall@7 = 97%** (38/39, same single
known `internship-vs-coop` miss) and improved @5 from 95% → **97%**. "What score do I
need on the professional skills quiz?" now answers correctly.

This is the general shape of the trade-off, worth recording: **big chunks answer
list-shaped questions, small chunks answer fact-shaped questions.** Rather than
picking one, keep the table whole for completeness and give any specific fact buried
inside it a short home of its own.

- context-recall@1 fell 85% → 77%. Accepted: production retrieves 7 chunks, and @5
  and @7 both improved or held. Rank-1 precision matters less than what reaches the
  model.
- Three chunks now exceed `max_chars` (the rubric tables at 2,604 and 2,042 chars,
  and the deliverables table at 1,934). Deliberate.
- **`display_prefix` is now unreachable for tables** — a window can no longer start
  mid-table, so the header is always already present. The column and plumbing are
  left in place (removing a migrated column is more risk than the tidiness is worth),
  but it is superseded and a follow-up can drop it.
- Changing this requires a re-ingest.

## Alternatives rejected

- **Raise `top_k` until every fragment fits.** Wasteful, and unbounded — a bigger
  table would need a bigger k again.
- **Keep windowing and merge fragments after retrieval.** More moving parts to solve
  a problem that disappears if the table is never split.
- **Accept the 75% regression as the price of complete tables.** Unnecessary: the two
  needs are not actually in conflict once the fact has its own chunk.
