# Knowledge Studio: staff workflow

Reviewed 2026-10-13 against [Needs Attention review/context](archive/attention-review-release-20261013.md)
and the [deployed paid-profile alignment](archive/oracle-paid-release-20261008.md).
Both **Add knowledge** and
**Needs attention → Review in Knowledge Studio** use one resumable workspace.
Continue linked draft/Continue in Studio resume saved work; editing a published
entry prepares its replacement while the current version remains active.

## Describe

### Needs attention

The queue contains unresolved formal refusals, negative student ratings and possible
incomplete answers identified by explicit missing-information wording. The last
category is an advisory signal, not an accuracy judgment or model confidence score.
Ordinary answers and temporary provider errors stay out. Filters separate these
reasons; the view loads the newest 100 candidates. Review counts include all three
categories without changing recorded answered/refused outcomes.

Each card shows the actual student question and reply, available department and
original retrieval excerpts. Expand **Previous conversation** to see the bounded,
redacted exchange submitted with a new request (up to eight messages of 1,200
characters each). Browser-supplied history is not verified policy evidence. Older
interactions have no saved context; any specifically restored staff-provided
exchange is labeled separately. No raw session/IP is added to these logs.

Review the response before opening Studio or dismissing it. A useful partial
answer or an appropriate refusal need not result in new knowledge. Review signals
use existing response text and consume no additional LLM calls.

### Preparing guidance

Paste one approved guideline, choose department/program scope and include necessary
conditions. Omit student names/IDs/personal contact details. You do not need to
engineer keywords or test questions. A supplied student question helps the review
check whether the guidance actually answers it.

When opening a Needs Attention case, the question/topic is prefilled and editable
so staff can clarify wording or restore an omitted subject. The original feedback
record remains linked and unchanged. The edited topic survives refresh/resume;
changing it requires a fresh review before continuing with the draft.

Select **Prepare & review draft**. Visible worker stages explain understanding/search,
literal claim comparison, focused search questions and independent coverage review.
Your factual guidance is retained; AI advice does not publish anything.

## Resolve

Read the focused feedback: missing facts, exact proposed-versus-existing claims,
source passages and recommended next action. Similar topics need not conflict;
different services/conditions must not be blended. Full passages are available
in expandable evidence.

- Missing facts: provide approved details and review again; unknown permission
  remains a question.
- Duplicate: use the existing source instead of publishing a competing entry.
- Conflict: correct the guidance, establish the precise approved exception, or update
  the appropriate existing source. AI advice cannot make a policy decision.
- Official-document replacement: use reviewed source normalization/ingestion;
  do not publish a contradictory admin rule beside an unchanged official source.

**Suggest an improved answer** stays available, including during conflict review.
The proposed answer shows green additions/crossed-out removals directly.
**Changes to your claims**, supporting facts, missing details and check warnings help
you inspect factual corrections. Source/numeric/verifier concerns are advisory for
this private writing draft, so the suggestion can still be shown for your judgment.
Do not infer that visible means verified or approved.

Choose **Edit suggestion**, **Discard suggestion** or **Use & review again**.
The input remains unchanged until use; using/editing starts a fresh main review.
A malformed response, privacy problem, stale context or writer service failure can
still prevent a suggestion. A failed verifier can leave the draft visible with a
warning that its independent check did not finish.

Confirm contributor, responsible office, optional date/reference, change reason and
source confirmation before **Continue to checks & previews**.

## Preview

Seven private checks run automatically and show their stages and feedback.
These checks are local/deterministic: source validity, private candidate index,
related/conflict passages, retrieval, department isolation, unknown-department
labels and preservation of existing tested evidence.

A failed existing-answer check means a previously passing test lost necessary
retrieved evidence in the candidate index. It does not necessarily mean your topic
contradicts that answer. Read the affected question/history, expected evidence and
actual change shown. Adding unrelated facts is not a reliable repair.

Canonical embeddings are tried first. A measured search failure can trigger one
bounded search-only repair; facts/scope/tests stay unchanged and all checks rerun.
If it still fails, keep the draft private and use the diagnostic guidance/report.
Never weaken original tests to obtain a pass.

**What students will see** contains separate, actual answers from the configured
student model against the private candidate, with normal grounding/citations.
Those previews use LLM calls. Inspect facts, qualifications and links; passing the
local checks does not guarantee the generated answer is correct.

If the student model or its settings changed since the saved preview, approval is
paused. **Retry answer previews** refreshes those answers while retaining valid
source checks and the prior attempt in the audit. A knowledge/source change still
requires fresh complete checks. Comparisons and writing suggestions retain
department, program and process-stage applicability; related placement guidance
does not establish a later employment outcome.

A saved failed draft can also offer optional answer-writing assistance using its
recorded checks/previews. Acceptance creates a successor and fresh review; earlier
versions and failures remain in history.

## Publish

Enter reviewer name/role, decision and approval note. After inspection, confirm and
select **Approve & publish**. Valid checks/source confirmation and human approval
remain mandatory; private AI warnings do not bypass them.

The worker/n8n path atomically activates the exact reviewed revision and checks
the serving index. The linked unanswered question resolves only after success.
No draft becomes student content merely by saving, generating or accepting AI text.

## Recover saved work

Reload or resume from Drafts/Needs attention. Saved stages/jobs live in PostgreSQL;
sign-out clears the browser working copy. Approval notes survive refresh for the
same checked revision; publication still requires confirmation.

Quota/provider failures preserve work and need retry later, not a policy change.
Retry interrupted search correction resumes the same bounded job, not a second
completed repair. Knowledge changes can invalidate old comparisons/checks and
require a fresh review/run.

## Who decides what

Staff/policy owners decide authority, scope, facts and replacements. The AI helps
write and review; deterministic checks measure specified evidence/scope properties.
The shared admin token authenticates access; reviewer labels are self-reported,
not verified identity or two-person approval.

See [curation contract](curation.md) for technical guarantees and
[operations](deployment.md) for models, budgets, services and recovery.


Paid generation shares the student assistant's durable daily request/token/cost
allowance. **Paid usage & controls** reports staff work and previews separately and
can pause all new calls. Pausing or exhausting an allowance preserves saved drafts;
resume/retry after the operator restores service. Existing review, validation,
source confirmation and human publication gates remain required. See
[paid-call operations](deployment.md#paid-call-controls-and-billing).
