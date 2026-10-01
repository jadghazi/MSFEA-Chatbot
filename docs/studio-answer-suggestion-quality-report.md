# Source-backed answer suggestions — verification

This records the **initial rollout**. Its blanket conflict block and mandatory
preservation of original numbers/URLs were subsequently replaced by disclosed,
source-backed corrections at the user's request. See
[the correction follow-up](studio-answer-correction-quality-report.md) for current behavior.

2026-10-01. Optional additions to the shared direct-intake / unanswered-question /
saved-draft Studio. No student-model, prompt, retrieval, embedding or chunking change.

## Product and safety

The original answer stays in the composer while the AI drafts and verifies a
separate suggestion. Tracked changes, explanation, quoted facts and missing-detail
questions precede use/edit/discard. Human edits survive refresh and are explicitly
shown as needing fresh verification. Using a suggestion records whether it was
edited and starts a normal fresh review. Earlier checks do not authorize the new
answer. Saved versions and their failed checks/unsuccessful previews remain intact.

The two-call verifier is advisory. In the live conflicting-course trial it
incorrectly approved replacing the original 3-credit claim with the existing
1-credit rule. Nothing was published. The final implementation blocks rewrite
requests while direct conflicts or possible replacements need a policy decision,
and independently protects original numbers/URLs in code. This failing attempt
was retained rather than discarded from the record.

Unknown support IDs, invented numbers/URLs, loss of original numeric facts,
unsupported claims, changed scope, stale KB, quota and provider failures fail
closed. Official-source corrections cannot enter this admin-answer rewrite path.
Literal quotes and HTML escaping preserve provenance and avoid executable output.

## Fixed live examples

The versioned five-case set and opt-in runner live in
`eval/studio_suggestion_set.jsonl` and `eval/studio_suggestion_eval.py`.

| Case | Original requested fact coverage | Offered result |
|---|---:|---|
| Course credit value versus registration eligibility | 1/2 | 2/2; adds the source-backed 90-credit condition |
| AI text limit, disclosure and citation | 1/3 | 3/3; preserves 25%, adds disclosure/citation |
| Fictional alumni networking desk hours | Hours absent | Asks for approved hours; invents none |
| Complete short course-credit rule | 1/1 | 1/1; preserves course value |
| Proposed conflicting 3-credit rule | Direct conflict | HTTP 409; staff policy decision required |

The first four batch cases failed during intermittent Gemini 503s (three parent
reviews and one suggestion). Explicit retries completed 4/4; failures remain in
the evaluation output. The conflict trial then exposed the unsafe rewrite above;
after the guard, the same completed parent review correctly returned 409 without
calling the model. Final case outcomes: **5/5**. These are narrow source-coverage
and workflow checks, not a general answer-accuracy or retrieval-improvement claim.

## Local validation

- Full backend suite before final guards: 399 passed, two skipped. All 21 final
  suggestion tests pass, covering final guards, existing review compatibility and
  immutable failed-check/preview context. Existing assistance tests also pass.
- All 32 frontend tests pass; strict type-checking and Ruff pass.
- All eight existing gates pass after rebuilding the 253-chunk official index:
  golden 122/124, faculty 198/205, valid threshold 165/165 (off-topic 12/20),
  synthesis 75/75, conversation 21/21, stress 43/43, publication preservation 9/9,
  conflict candidates 7/7. These match the existing baseline; known misses remain.
- Real browser walkthrough: generated a source-backed answer, edited it, refreshed,
  discarded a proposal without changing the original, and accepted an edited
  answer. Its fresh review identified a duplicate and prevented a second KB copy.
  Desktop and mobile layouts were inspected; mobile client/scroll width matched.
- Saved-draft walkthrough used a real incomplete private clinic successor.
  The suggestion supplied its documented Tuesday 2–4 p.m. hours and appointment
  rule. Acceptance started fresh AI review; source confirmation created version 4,
  all seven checks and both real student previews passed, and normal named approval
  published it through n8n in the disposable local stack. Version 3 remains in
  history. No checks or earlier approvals were copied to the new revision.
- Implementation CI [36914075684](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/36914075684)
  passed the final full suite, frontend checks, strict typing and all retrieval gates.

No synthetic content was transferred to Oracle. Both deployed suggestion jobs
completed using official facts; fresh-review enforcement and the existing letter
conversation passed. The deployed dashboard was also exercised visually, showing
source-backed eligibility additions while preserving the original input.
See [deployment verification](oracle-answer-suggestion-deployment-20261001.md).
