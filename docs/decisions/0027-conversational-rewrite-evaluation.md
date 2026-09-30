# ADR-0027: Keep selective LLM rewriting out of the pilot

**Status:** Accepted, 2026-09-30

## Context

The existing resolver makes short retrieval queries and searches both the literal
and contextual question when needed. We tested whether a second Gemini model,
called only for uncertain references, would improve this flow. The experimental
route used Gemini 3.1 Flash-Lite for a short JSON standalone query, retained the
literal retrieval path, rejected low-confidence or suspicious rewrites, and fell
back to the current resolver on provider errors. Clear standalone questions did
not call the second model.

## Evidence

We evaluated 43 mixed-turn cases on the same freshly rebuilt 253-chunk local KB:
the existing 21-case conversation set plus 22 cases for vague quantities,
pronouns, omitted subjects, topic switches, switch-backs, and standalone questions
with irrelevant history. The source text, embedding model, database, and retrieval
depth were fixed across runs. The original `origin/main` resolver and final
deterministic change are saved in
`eval/results/conversation_stress_original.json` and
`eval/results/conversation_stress_final.json`.

| Measure | Original resolver | Final deterministic resolver |
| --- | ---: | ---: |
| Expected evidence in top 7 | 42/43 | 43/43 |
| All expected evidence in top 3 | 38/43 | 39/43 |
| Standalone questions identical to no-history retrieval | 17/19 | 19/19 |

The missed original case was a follow-up after an explicit return to the
internship topic: it still retrieved CO-OP context. A lowercase named subject
after “and” also inherited old context, and the subject hint truncated “CO-OP”
to “OP.” The final change fixes these general routing and acronym behaviors.

The selective LLM candidate did not improve evidence recall or ranking beyond
the final deterministic resolver on this set. Seven paired live answers were
reviewed directly; both variants answered all seven correctly. The model made
one answer more concise but did not correct a factual failure. It also added
three rewrite attempts on the retrieval run, including a transient 503 that
required fallback. The second call therefore adds latency and quota use without
a measured answer-quality gain on the latest pipeline.

## Decision

Do not ship the selective rewrite call during the pilot. Keep the existing
single-generation-call architecture and its dual-path retrieval. Ship only the
measured deterministic routing fixes and put the 43-case stress gate in CI.
Reconsider a second model only if new, anonymized pilot failures demonstrate
that the deterministic path misses or misinterprets references despite correct
source evidence, and a paired evaluation shows a substantive gain without
standalone or switch-back regressions.
