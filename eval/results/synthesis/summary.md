# Local RAG improvement review — 2026-09-08

This report covers the pre-deployment local validation. Oracle was not contacted
during the experiments recorded here.

## What changed and why

The strongest retrieved evidence could pass 0.60 while the first hybrid-ranked
hit did not. That incorrectly rejected “Explain the 6+2 arrangement” before the
LLM ran. The gate now checks all retrieved cosine scores.

The model also interpreted tentative restatements as requests for associated
requirements. Explicit confirmations now preserve the student's proposition and
ask for a short confirmation/correction. Short task cues distinguish definitions,
comparisons and conditional decisions. Comparisons retrieve 12 chunks; ordinary
questions retain 7. The existing model and one-call architecture remain.

## Measured result

The 12-case test set was frozen before production edits. Scores are manual reviews
by the coding assistant against expected qualities and source chunks, not an
independent human assessment. Synthesis averages exclude the intentional refusal.

| Metric | Baseline | Selected combination |
|---|---:|---:|
| Synthesis, 11 answerable cases | 3.09/5 | 4.64/5 |
| Unsupported/misapplied policy answers | 2 | 0 observed |
| False refusals | 1 | 0 |
| All required retrieval premises | 10/11 | 11/11 |
| Correct undocumented-reason refusal | 1/1 | 1/1 |
| Generation calls | 11 | 12 |
| Total input tokens | 25,572 | 29,163 |

A repeated precursor run returned identical text, citations and refusal flags on
all 12 cases. After the broader condition-boundary fix, the exact final production
configuration was rerun and manually reviewed in `production_final_review.md`.

## What was tried

| Intervention | Synthesis /5 | Outcome |
|---|---:|---|
| Shorter task-first prompt | 3.00 | Confirmation still became a checklist |
| k=3 | 3.18 | Lost necessary evidence, including topic switch |
| k=12 | 3.00 | More evidence, but misapplied the summer-course rule |
| Two-call facts then composition | 3.00 | More calls without better intent handling |
| Temperature 0.4 | 3.09 | Same text as baseline on all 12 |
| Corrected gate alone | 3.27 | Fixed false Explain refusal only |
| Alternative model, original token cap | 2.73 | Three truncated answers; no default swap |
| Native system-role policy | 2.91 | Did not fix paraphrasing or grounding |
| Structured resolved-question JSON | 2.45 | Structured the wrong interpretation |
| Source-free LLM turn rewriting | 3.64 | Lost WHY intent; rejected |
| Narrow confirmation frame, corrected isolation | 3.55 | Better but still extra details |
| Task cues | 3.82 | Generic WHY cue caused false refusal |
| Combined with fixed k=12 | 4.00 | Summer-course grounding regression |
| Combined with adaptive k, excluding WHY cue | 4.45 | Selected and repeated |

The alternative model with a larger output budget completed only 8/12 cases
before its daily quota limit; excluded from aggregate comparisons. It addressed
truncation but did not establish a synthesis advantage. This is not proof that
the model is incapable of better answers. Chunking already preserves sections and
atomic tables; retrieval depth was tested before considering an index rebuild.

## Actual before/after

“Explain the 6+2 arrangement” previously returned the generic escalation. Now it
defines six company weeks plus two faculty-research weeks, with approval conditions.

For “so 2 weeks of research,” the baseline listed research forms, alternatives and
supervisor details. The real local HTTP conversation now answers:

> Yes, the 6+2 arrangement for ECE students includes a two-week research component with an MSFEA faculty member.

Its next follow-up, “so two more weeks at the company instead?” receives:

> Not quite. For ECE students, the 6+2 arrangement requires two weeks of research with an MSFEA faculty member rather than two additional weeks at a company.

The conversation also switches successfully to IAESTE. See [actual HTTP responses](local_http.json).

## Limits and tradeoffs

Definitions still sometimes add an unasked report detail. The fairness rationale
does not explicitly address the wait-time tension. A summer-course paraphrase in
the real conversation gives the correct ten-week requirement but does not lead
with an explicit No. The original broad golden set also contains incomplete
answers; its [broader review](golden_review.md) is recorded separately, not counted
as perfect accuracy. Four concerning broad-case outputs were rerun against the
original pipeline and showed the same underlying weaknesses.

The corrected gate sends three more of 20 off-topic calibration prompts to the
LLM for refusal (11/20 skipped vs 14/20). All 109 valid calibration queries pass.
Provider latency varied with test time and is not a controlled speed comparison.
Requests now time out and empty/truncated answers take the temporary-failure path.

The broader review found one selected-prompt regression: it mixed the separate
ten-week summer-course rule into a plain 6+2 question. The decision cue was narrowed
before release so numeric rules apply only when their source conditions match the
student's stated scenario; targeted live controls preserve both the ordinary 6+2
and summer-course outcomes.

Verification: 143 tests passed in the isolated test database; Ruff and strict mypy
passed. Local app and database are healthy. Clean broader retrieval recall is
68/69 (68 golden questions plus one local curated case); the existing generic
internship-vs-CO-OP probe still misses its graduation-requirement premise.

Full case scores, citations and verbatim outputs: [reviewed results](reviewed_results.md).
Raw traces include every prompt, retrieved chunk and provider response. Partial
and invalid runs are explicitly identified in [operational notes](operational_notes.md).
Dead ends: [MISTAKES.md](../../../MISTAKES.md).
