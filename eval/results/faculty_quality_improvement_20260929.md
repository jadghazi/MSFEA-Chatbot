> Historical evaluation evidence/protocol. Settings, results and instructions refer to the dated run below; use [current task guidance](../../docs/README.md) for today's implementation and verification.

# Faculty answer-quality follow-up — 2026-09-29

## Change and evidence

This change keeps the existing Gemini provider and model selection. It adds
source-backed, department-scoped FAQ passages for policy facts that were missing or
scattered across retrieved chunks, improves retrieval of strong semantic candidates
without replacing hybrid ranking, and narrows generation to a clearly dominant
approved FAQ when one exists. The answer instructions distinguish internship from
other CDC programs, policy from individual approval, and required conditions from
incidental nearby material. No vector rows were edited manually; the index was
rebuilt from the versioned KB.

The faculty grader previously accepted missing case IDs in a multi-case response
and paired judgments by position. That can assign a plausible verdict to the wrong
answer. Multi-case responses now require matching IDs; consequential comparisons
below used one case per judge call. The earlier full-set score of 174/205 is
historical and provisional, and is **not** a comparable before score for this fix.

| Measure | Baseline | Candidate | Scope |
| --- | ---: | ---: | --- |
| Correct judged answers, selected real-question failures | 0/14 | 14/14 | Same 14 faculty questions and rubric, rejudged individually; selected for failure, not a population estimate. |
| Correct judged answers, real-question control sample | — | 14/15 | Stratified previously passing cases; one answer listed the requested documents but omitted a reminder to follow CDC/Moodle procedure before starting. |
| Correct judged answers, new synthetic validation | — | 16/16 | Unique held-out paraphrase and refusal cases; judged individually. |
| Required-refusal behavior, synthetic validation | — | 16/16 | Includes answerable and refusal cases. |
| Citation on answerable synthetic validation cases | — | 15/15 | Citation presence, independently of semantic correctness. |
| Original golden-set context recall at 7 | 118/121 | 118/121 | 97.5%; unchanged. |
| Annotated faculty source-document hit at 7 | 201/205 | 201/205 | 98.0%; unchanged; document hit is weaker than policy-passage sufficiency. |
| Focused synthesis evidence/context/threshold gate | 67/67 | 75/75 | Eight source-evidence cases added. |

The final rebuilt local index contained 245 chunks. Ten repeated six-week
questions across the five departments and three employer-letter timing variants
all answered with source hits and no false refusals. These are smoke checks, not a
new full-set answer-accuracy score. The model still occasionally uses awkward
wording, so the qualitative target is not claimed as flawless.

Verification: full Docker test suite **308 passed, 2 skipped**; final targeted
tests **61 passed**; Ruff, strict mypy, and diff whitespace checks passed.
Similarity threshold calibration remained **162/162** valid cases and **12/20**
off-topic cases blocked early. Publication scope and conflict-candidate gates
remained **9/9** and **7/7**.

The candidate was not run through all 205 live answers because of the shared
500-request daily Gemini quota. The 14-case repair result is intentionally selected;
the 15-case control and 16-case validation samples bound regressions but cannot
estimate full-population accuracy. Model judgments have source review by Codex,
not independent human calibration. A later budgeted full-set answer run should
use the corrected grader and report its denominator and source evidence.
