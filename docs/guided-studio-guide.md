# Staff guide: Knowledge Studio

## Describe → Resolve → Preview → Publish

1. Open **Add knowledge**, or **Review in Knowledge Studio** from **Needs attention**.
   **Continue linked draft** and **Continue in Studio** resume saved work. **Edit**
   on a published entry prepares its replacement without taking it offline.
2. Paste one approved guideline and choose its department and programs. Include
   the conditions needed to interpret it; omit student names, IDs and contact details.
   You do not need to write search keywords or test questions.
3. Select **Prepare & review draft**. The assistant records separate stages:
   understand the entry, find related sources, compare literal claims, prepare
   focused search questions, and independently verify the findings and coverage.
4. Resolve the specific questions shown. Genuine conflicts quote your claim and
   the existing claim, identify the source and explain the difference. Similar
   wording about different services is checked independently. Full passages and
   initial comparison feedback stay in expandable details.
5. If the assistant needs facts, update the approved guidance and review again.
   It cannot invent an exception or silently replace an official document. A
   duplicate points to the existing source. A change to an official source needs
   reviewed source-file ingestion; approving a second contrary rule is blocked.
   **Suggest an improved answer** can add missing details from related approved
   sources and clarify wording. Green additions and crossed-out removals show
   changes; expand the literal source facts if needed. Choose **Edit suggestion**,
   **Discard suggestion**, or **Use & review again**. Your original answer stays
   unchanged until use, and accepting either version starts a fresh review.
   A direct conflict or possible policy replacement must be resolved by staff
   before AI can rewrite the answer; the assistant cannot choose the approved rule.
6. Confirm the contributor, responsible office, optional date/reference and reason.
   Check the source confirmation and select **Continue to checks & previews**.
   Stay in Studio: seven private checks run automatically.
7. Read **What students will see**. These are actual answers from the configured
   student model, using the private candidate and normal RAG prompt, retrieval,
   citations and disclaimer. Check the facts and links.
8. Enter a reviewer name or role, decision and approval note. Confirm and select
   **Approve & publish**. The existing worker/n8n flow publishes atomically.
   The linked unanswered question resolves only after activation succeeds.

The approved content is preserved verbatim. Generated search questions are
independently checked and retained as tests. Canonical embeddings are tried first.
For a real search failure, the assistant may make **one** bounded correction to
search wording in a new private revision. Facts, scope and original tests stay
unchanged, and the complete checks run again. Search wording never becomes answer
evidence. Longer entries keep ordinary section embeddings.

## When publication pauses

- **Missing facts or mixed topics:** answer the displayed factual questions or
  split independent topics. Review the revised complete guidance.
- **Conflict:** compare literal claims. Correct the guidance, describe an
  approved exception and its precise scope, or update the existing Studio entry.
  Staff judgment remains mandatory; AI advice cannot change policy.
- **Search failure:** the affected question, earlier conversation and expected
  answer are shown. A bounded automatic correction may run. If it still fails,
  revise genuinely incomplete guidance or leave it private for technical diagnosis.
  Never weaken the original tests to obtain a passing result.
  A saved admin-authored draft also offers an optional answer suggestion based
  on its recorded failures and unsuccessful previews. Using it creates a newly
  reviewed successor; the old revision and failed results remain in the audit.
  Adding unrelated policy facts cannot fix a search regression.
- **Quota or provider failure:** your work remains saved. Retry previews or review
  later. A failed service call is not a policy judgment or permission to publish.
  **Retry interrupted search correction** resumes the same bounded repair job
  after a service failure; it cannot create a second completed correction.
- **Knowledge changed:** review outdated AI comparisons or run fresh checks as
  directed. Earlier results remain in the audit; they do not authorize a new version.

Reload and return to **Add knowledge**, or resume from **Drafts** / **Needs attention**.
Sign-out clears the browser's working copy; saved jobs remain in PostgreSQL.
Approval notes survive refresh for the same checked revision; confirm publication again.
Approval cannot waive failed checks.

## Operator notes

- Run the existing guarded Compose stack: API, PostgreSQL, curation worker, n8n,
  n8n database and private validation database. No extra service or dependency.
- `CURATION_LLM_MODEL` defaults to `gemini-3.1-flash-lite`; `LLM_MODEL` stays
  independent. Confirm actual project quotas in AI Studio before changing models.
- Defaults admit 12 attempts/minute and 400/day/model. Routine review uses four
  calls; clarification usually stops after two. Comparison/independent verification
  may each retry invalid output once, and the provider may retry a transient error
  once. Every actual provider attempt consumes the admission budget.
- Actual student previews have a separate 60-call daily admission cap and share
  the student model's provider quota. They never silently use another model.
- Optional answer suggestions use two staff-model calls: draft from numbered
  facts, then independently verify support and original meaning. Original numbers
  and URLs are also protected deterministically. Missing facts stay questions.
  These checks reduce risk; human review and fresh publication checks still apply.
- Run the fixed suggestion examples only on a disposable stack:
  `python -m eval.studio_suggestion_eval --url URL --output tmp/suggestions.jsonl`.
  Set `STUDIO_TEST_TOKEN` in the environment. `--resume` explicitly retries failed
  cases, retaining earlier attempts and reusing completed parent reviews.
- Migration 0007 adds stage records, immutable search questions and private jobs.
  Normal source ingestion rebuilds active knowledge, including approved search text.
  The worker uses one inference thread under its CPU cap.
- Back up PostgreSQL normally. Never publish synthetic demo policies on Oracle.
- Live evaluation is opt-in on a disposable stack:
  `python -m eval.studio_review_eval --url URL --token-env STUDIO_TEST_TOKEN`.
  Supply the token through the environment. Failed attempts remain in the report
  when explicitly resumed; do not report retries as first-attempt success.
