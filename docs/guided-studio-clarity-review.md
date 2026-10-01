# Knowledge Studio: explain the decision and the next step

The first implementation exposed seven pass/fail checks after saving but dropped
the AI report. An older advising test lacked readable failure details. Staff could
not tell what was wrong, whether AI had reviewed the entry, or who should fix it.

## Changes

- A draft now separates AI advice, deterministic search tests and human approval.
  The actual recorded model, summary, classification and quoted findings remain
  visible after saving. A manual revision never claims to have an AI assessment.
- Publication problems precede the checklist. An existing-answer regression shows
  the full affected conversation, expected answer/source and recorded before/after
  evidence outcome. Staff receive a maintainer handoff rather than a vague demand
  to fix their wording. Copying the report sends nothing externally.
- New-answer failures show the specific question and missing answer evidence.
  Policy conflicts show the AI's explanation and the two literal claims. Missing
  information lists the questions staff need to answer before saving.
- Seven checks, broad rule-based flags, original source/test inputs and audit IDs
  remain expandable. They are explicitly separate from LLM policy judgments.
- Guided correction preserves entry identity, scope and the original linked
  question. Accepted corrections are new immutable revisions. Identical reviewed
  resubmissions produce a readable conflict instead of a database exception.
- Model failures say that no AI assessment exists, identify the model and explain
  the recovery action. The failed review and working guidance survive refresh.

## Historical honesty

For older test results containing only a failed test ID, the authenticated read
path attaches the question, history, expected answer and source from the evaluation
catalog. It does not change the stored result, rerun retrieval, or modify an index.
Unknown old IDs remain unknown. Recorded expectations take precedence over the
current catalog. Missing historical passage rankings are disclosed explicitly.
New golden-set failures record the source passages retrieved before and after.
This is evidence of the impact, not permission to invent an exact ranking cause.

## Verification

Nine Node tests exercise regression explanations, honest historical diagnostics,
escaped model/source text, manual revisions, passing tests with mandatory review,
literal conflict claims, specific new-answer failures, copied issue reports and
explicit incomplete-coverage advice.
The existing ten widget tests also pass. Fifty focused Python tests pass, covering
the read-only legacy explanations, protected API report handoff, guided successors,
identical resubmissions and the original assistance contracts. Lint and strict
typing pass (63 modules). The full Python suite passes **368 tests with two skips**.
The isolated serving demo retains **123/125** production-depth context recall,
the same result as before this interface rework, including its published test entry.

Live browser QA uses the same isolated local demo. The original advising failure
now shows the letter-request follow-up, its expected form/source and a maintainer
action; its recorded failure remains unchanged. Copying the issue and opening the
guided correction were exercised. A real Gemini quota response was shown as a
service failure, not a policy rejection, and was retained across refresh. At 390px
the interface has no horizontal overflow. Both Needs attention routes, explicit
keep/replace decisions and the saved-draft correction were browser-tested.

This tests explanatory behavior. It is not a claim that faculty usability has been
measured. Faculty feedback still determines whether the language and flow work for
their actual review tasks. No source document, embedding, ranking, student prompt,
required publication gate, n8n workflow or Oracle deployment changed.
