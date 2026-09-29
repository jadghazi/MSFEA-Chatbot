# ADR-0025 — Current-question-first conversation retrieval

**Status:** Accepted
**Date:** 2026-09-29

## Problem

The pilot's bounded history was useful for elliptical follow-ups, but its word
rules sometimes attached unrelated older turns to a new question. The retrieval
query pasted an earlier user turn, sometimes an earlier assistant answer, and
the current question together. On Oracle, “What is mentorship?” after CO-OP
lost the MentorPlus+ source and refused; after a later mentorship turn,
“Is it mandatory?” answered about the older CO-OP topic. A detailed CDC
support-letter question also lost its answer passage after an unrelated salary
turn. These are retrieval failures before they are generation failures.

## Decision

- Treat explicit named subjects and sufficiently detailed questions as new turns.
  Relative “that” in a self-contained sentence is not by itself a follow-up.
- Resolve genuine references from the most recent substantive student turn,
  skipping intervening elliptical turns. Send a short resolved question to both
  retrieval and generation. Earlier assistant wording stays in the bounded
  generation history where relevant, never in the retrieval query.
- When the current turn has its own substantive terms but still looks contextual,
  search both the literal and resolved query. Score both candidate sets against
  the **literal current question**; use small hybrid-rank preferences only to
  break close calls. A candidate's high similarity to the older topic cannot
  outrank current-question evidence just because its contextual query is strong.
- Keep one Gemini generation request per student turn. The second path uses only
  the existing local embedding model and PostgreSQL. No session store, provider
  rewrite, or KB changes are introduced.
- For yes/no policy questions, lack of a rule for the resolved subject is not
  evidence for “No.” The grounded answer must refuse rather than transfer a
  binary rule from another retrieved program.

## Measurement

Fifteen conversation cases were frozen and measured on the same source-built
253-chunk index before the code change (commit `444b145`) and afterward:

| Measure | Before | After |
| --- | ---: | ---: |
| Expected section in top 7 | 6/15 | 15/15 |
| Expected section at rank 1 | 5/15 | 8/15 |
| Independent question: exact ranked parity with standalone | 2/8 | 8/8 |

Two additional ambiguous dual-path cases were added after the first comparison;
the final 17-case gate scores 17/17 evidence hits and 8/8 independent parity.
The gate is in CI. The existing synthesis gate remains 75/75; golden context
recall is 122/124 and faculty source-document recall is 200/205 on the local
index. These are retrieval checks, not answer-accuracy claims.

Focused Gemini answers were reviewed manually with requests spaced at least
six seconds apart. The previously failing mentorship switch now answers the
mentorship question; the ambiguous mandatory follow-up refuses rather than
applying CO-OP's optional rule. A switch back to CO-OP still gives its documented
optional status. The support-letter question returns the CDC form URL; a genuine
“Where do I get it?” follow-up also returns that URL. A CO-OP pay follow-up uses
the paid-work source. The internship and June-start questions after CO-OP no
longer answer with CO-OP rules. These focused observations are not a statistical
estimate of overall answer quality.

## Trade-off and limits

Ambiguous turns can run a second **local** retrieval, increasing embedding and
database work but not Gemini RPM/RPD. A self-contained question uses one search.
Deterministic language rules still cannot resolve every vague pronoun or unusual
topic shift; a pilot can add anonymized examples to this set as they occur.
Retrieved blocks remain untrusted candidates, and the generator can still need
to refuse when the chosen subject's policy is undocumented.
