# Faculty-question golden-set evaluation — Oracle, 2026-09-29

## Scope and method

The anonymized, faculty-approved workbook contains 177 original questions across all
18 sheets. Seven policy-sensitive questions were tested separately for every
department, producing 205 frozen department-scoped cases in
[`faculty_questions_golden.jsonl`](../faculty_questions_golden.jsonl). The 177
original wordings remain identifiable with `primary_workbook_case`. This is a
real-question set; the 28 added department variants are scoped adaptations, not
additional student submissions. The source workbook and resolved owner decisions
are recorded in [`faculty_run_manifest_20260928.json`](faculty_run_manifest_20260928.json).

The bot answers were generated through the production answer path in the Oracle
container, against deployed app commit `f029b30369ed999f5032e5d5172e0a54ce5e33e6`
and KB generation `sha256:4eeb6f2bdb8a626c60cb09386267f8d7e11c22ffd08267fd4ca2b943c329f769`.
The bot used `gemini-flash-lite-latest` (the observed quota model was
`gemini-3.5-flash-lite`), `top_k=7`, and similarity threshold `0.60`. Calls were
paced below 15 requests/minute. All 205 answers completed; temporary Gemini quota
and service errors were retried rather than counted as policy failures. The
separate grader used `gemini-3.1-flash-lite` with the decomposed rubric in
[`faculty_judge.py`](../faculty_judge.py). Malformed grader responses were retried
one case at a time; the canonical judgment file contains one valid judgment per
case.

## Results

| Measure | Result | Interpretation |
| --- | ---: | --- |
| Annotated source-document hit in retrieved top 7 | **201/205 (98.0%)** | Right document appeared; this does not prove the right policy passage was present. |
| Policy-evidence sufficiency in retrieved excerpts | **194/205 (94.6%)** | Grader found enough policy facts to answer the resolved question. |
| Answer correctness and cited grounding | **174/205 (84.9%)** | Provisional decomposed model-judge score, not independently human-calibrated. |
| Original workbook question correctness | **151/177 (85.3%)** | Same grading on original wordings, excluding added department variants. |
| Refusal behavior match | **190/205 (92.7%)** | All 15 mismatches were false refusals. This set has no required-refusal cases. |
| Citation on substantive answers | **190/190 (100%)** | Citation presence only; the grader separately assessed support. |
| Visible AI disclaimer | **205/205 (100%)** | Deterministic presence check. |

| Department | Cases | Source-document hit | Sufficient evidence | Correct answer |
| --- | ---: | ---: | ---: | ---: |
| ECE | 60 | 57/60 | 54/60 | 43/60 (71.7%) |
| MECH | 38 | 38/38 | 37/38 | 33/38 (86.8%) |
| CHEM | 38 | 37/38 | 38/38 | 34/38 (89.5%) |
| IEM | 34 | 34/34 | 31/34 | 30/34 (88.2%) |
| CEE | 35 | 35/35 | 34/35 | 34/35 (97.1%) |

The direct six-week internship question was rated correct in all five departments
(`faculty-008-*`). Related split-placement questions were less reliable. For
example, the CHEM answer to “Can I combine two internships?” discussed Final
Report formatting without the required prior written approval; its 4+4 answer
also omitted approval. The IEM 4+4 question was refused. This explains why a
single successful six-week test did not establish robust department behavior.

The four annotated source-document misses were `faculty-007-chem`,
`faculty-025-ece`, `faculty-045-ece`, and `faculty-125-ece`. Eleven cases lacked
sufficient policy evidence even though only four missed the expected document:
document-level retrieval is a weak proxy for policy-level retrieval. The 15 false
refusals include answerable questions about pre-start approval, startup eligibility,
the ECE quiz passing grade, employer letters, and course grading. Other substantive
misses include the ECE presentation-content questions and a CHEM AI-content
consequence that was stated too strongly.

## Grader audit and limits

Codex reviewed 48 source-backed answers, deliberately oversampling high-risk
rules and rubric challenges. It labeled 37/48 correct. The final model judge
agreed on **46/48 (95.8%)**; the disagreements were `faculty-011-mech` and
`faculty-154-cee`. This is an internal source review, **not independent human
calibration** and not a random estimate of full-set accuracy. The judge also
made at least one obvious false-negative outside that sample: `faculty-055-ece`
states every requested font/spacing rule, yet its judgment marks
`refusal_appropriate=false` while its own reason calls the answer correct. The
84.9% figure is therefore a raw, provisional judge score. Do not use it as a
certified answer-accuracy claim until an independent reviewer adjudicates a
representative sample and the grader errors.

The faculty set contains only answerable questions. The separate synthetic and
edge-case golden set still tests appropriate refusal; the 92.7% refusal-behavior
score here measures **false refusals**, not ability to refuse unsupported questions.
One live answer per case was scored, so the numbers do not measure variation across
repeated runs. No app behavior was changed during this baseline.

## Reproduction and next work

The frozen traces are [`faculty_retrieval_20260928.jsonl`](faculty_retrieval_20260928.jsonl),
[`faculty_answers_20260929.jsonl`](faculty_answers_20260929.jsonl), and
[`faculty_judgments_20260929.jsonl`](faculty_judgments_20260929.jsonl). Recreate
the summary with:

```bash
python -m eval.faculty_report \
  --cases eval/faculty_questions_golden.jsonl \
  --retrieval eval/results/faculty_retrieval_20260928.jsonl \
  --answers eval/results/faculty_answers_20260929.jsonl \
  --judgments eval/results/faculty_judgments_20260929.jsonl \
  --review-labels eval/results/faculty_calibration_labels_20260928.jsonl
```

Next, independently review the 48 labeled cases plus the grader contradiction,
then fix the retrieval/evidence gaps and false-refusal paths before tuning answer
wording. Repair department-specific split approval and presentation guidance,
then rerun this set and a separate holdout to measure the change. The deployment
should not be updated solely on this baseline; this run establishes what needs
repair.
