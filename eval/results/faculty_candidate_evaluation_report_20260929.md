# Full faculty-question answer evaluation — Oracle candidate, 2026-09-29

## Run and denominator

The frozen 2026-09-26 faculty workbook contributes 177 anonymized original
questions. Department-sensitive questions expand to 205 scoped cases in
[`faculty_questions_golden.jsonl`](../faculty_questions_golden.jsonl). This run
used the deployed Oracle answer path at Git commit `c07e907`, with the rebuilt
245-chunk KB, `top_k=7`, threshold `0.60`, and the unchanged
`gemini-flash-lite-latest` answer-model setting (observed as Gemini 3.5 Flash
Lite). Calls were serialized with an 8.5-second minimum between starts; no
student interaction logs were written by the evaluation runner.

All 205 answers completed with no provider errors. The separate decomposed
judge used `gemini-3.1-flash-lite`, one case per request, with the same 8.5-second
minimum after answer collection finished. An earlier 80-case segment was paced
at 12 seconds and ran alongside answer collection, keeping combined intended
traffic below 15 requests/minute. A two-case judge probe produced invalid JSON
and was discarded. The single-case judge stopped immediately at its first 429,
leaving `faculty-115-ece` unjudged. Its answer is preserved and source-reviewed.
The judgment file is append-only; use the latest record per case. It contains
204 valid case judgments and two superseded invalid probe records.

## Measured results

| Measure | Result | Meaning |
| --- | ---: | --- |
| Answers completed | **205/205** | No unanswered provider errors. |
| Annotated source-document hit among retrieved top 7 | **201/205 (98.0%)** | Document-level annotation, not proof of passage sufficiency. |
| Judge-rated policy-evidence sufficiency | **198/204 (97.1%)** | Provisional model assessment of retrieved excerpts. |
| Raw judge-rated answer correctness and grounding | **168/204 (82.4%)** | One case unjudged; includes demonstrable false negatives. |
| Original workbook wording, raw judge-rated | **145/176 (82.4%)** | One of 177 originals unjudged. |
| Refusal-behavior match | **202/205 (98.5%)** | All 205 cases are answerable; three false refusals, no required-refusal cases. |
| Citation presence on substantive answers | **202/202 (100%)** | Presence only; support is reviewed separately. |
| Visible AI disclaimer | **205/205 (100%)** | Deterministic presence check. |

| Department | Cases | Source-document hit | Raw judge-correct / judged |
| --- | ---: | ---: | ---: |
| ECE | 60 | 57/60 | 45/59 |
| MECH | 38 | 38/38 | 32/38 |
| CHEM | 38 | 37/38 | 28/38 |
| IEM | 34 | 34/34 | 31/34 |
| CEE | 35 | 35/35 | 32/35 |

## Review of every flagged case

The [case-by-case review](faculty_candidate_flagged_review_20260929.md) gives
the **full bot answer**, citations, raw judge verdict and reason, annotated
document-hit result, and Codex source-review note for all 39 cases flagged by
any of these checks: judge failure, document miss, refusal, or missing judgment.
The machine-readable labels are in
[`faculty_candidate_review_20260929.jsonl`](faculty_candidate_review_20260929.jsonl).

Codex classified those 39 as **16 confirmed answer/grounding gaps**, **8 partial
or debatable answers**, **14 acceptable answers despite a raw flag**, and **one
source-supported answer with no model judgment**. This is a targeted audit of
flags, not an independent or blinded review of all 205 cases, so it must not be
converted into a certified adjusted accuracy percentage. The raw 82.4% score
also should not be read as the bot's known true accuracy.

Examples of genuine gaps include ECE unlisted-company approval without the
petition and company-letter requirements (`faculty-020-ece`), CEE 6+2 reporting
without Chair approval (`faculty-014-cee`), a vague ECE presentation requirement
(`faculty-070-ece`), three false refusals (`faculty-087-chem`,
`faculty-132-chem`, `faculty-145-ece`), and CO-OP final deliverables without the
additional signed company letter (`faculty-177-chem`).

Examples of raw judge false negatives include a correct MECH 4+4 prohibition
(`faculty-012-mech`), a correct CHEM same-summer split answer
(`faculty-012-chem`), and an ECE visuals answer (`faculty-075-ece`): in each,
the judge's explanation says the answer is correct while its
`refusal_appropriate` flag is false. The judge also faulted the MECH Final
Report cover-page answer for missing fields absent from the official cited
template (`faculty-056-mech`). Two annotated document misses
(`faculty-025-ece`, `faculty-125-ece`) nevertheless retrieved a newer approved
FAQ and answered correctly. The one unjudged answer (`faculty-115-ece`) gives
the conditional ten-week rule correctly; no retry was sent after the 429.

The prior Oracle full-set score of 174/205 used a batch judge that could pair
ID-less judgments positionally. It is historical and **not directly comparable**
with this one-case judge run. The 14-case targeted repair result remains useful
for those selected failures but is not a population estimate. A defensible
overall accuracy claim requires independent human calibration on a representative
sample and adjudication of these contested cases.

## Reproduction

The saved [answer traces](faculty_answers_candidate_20260929.jsonl) include
retrieved passage text and citations, and the saved
[judgment traces](faculty_judgments_candidate_20260929.jsonl) retain all
decomposed verdicts. Regenerate the numeric summary with:

```bash
python -m eval.faculty_report \
  --cases eval/faculty_questions_golden.jsonl \
  --retrieval eval/results/faculty_answers_candidate_20260929.jsonl \
  --answers eval/results/faculty_answers_candidate_20260929.jsonl \
  --judgments eval/results/faculty_judgments_candidate_20260929.jsonl
```
