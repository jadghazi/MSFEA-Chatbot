# Staff guide: guided Knowledge Studio

## Add knowledge

1. Open **Add knowledge**, or select **Review in Knowledge Studio** from a question
   under **Needs attention**. The student question remains attached to the draft.
2. Paste one approved guideline. Include the relevant approval conditions,
   exceptions, deadlines and department applicability. Remove student-identifying
   details. Choose the department and all applicable programs explicitly.
3. Select **Prepare & review draft**. The assistant retrieves existing guidance
   and compares the actual claims. Loading stages reflect real persisted work.
4. Read the short comparison. Proposed and existing claims are quoted side by side.
   Expand the sources only when more context is needed. A “new” result is a search
   assessment, not proof that the policy is correct or that no conflict exists.
5. If details are missing or topics are mixed, amend the guidance and review again.
   The assistant preserves the approved answer verbatim.
6. Confirm the contributor, responsible office, optional date/reference and reason.
   Check the factual approval box, then **Save draft & run checks**.
7. In **Drafts**, inspect the private checks, including retrieval for the original
   student question. Record the required named human review. Publish only after
   those checks and that decision permit it.

An exact duplicate points to the existing source instead of producing a second
copy. If a student failed to find existing information, inspect the recorded
retrieval evidence; adding a duplicate is not a retrieval repair.

## Understand a paused draft

Drafts show three separate responsibilities: **AI writing/policy review**, **search
tests**, and **staff approval**. The actual AI summary, model and quoted findings
remain visible after saving. Manual revisions explicitly say that no AI review
was used. Broad rule-based comparison flags remain expandable and are labelled
separately from AI findings.

For an existing-answer regression, the page shows the affected conversation,
the answer/source the student should receive, and whether evidence was found
before and after adding the draft privately. No original policy was deleted.
Use **Copy issue for maintainer** to prepare a handoff; this copies a report and
does not send a message. Staff are not expected to diagnose ranking changes.
**Review guidance with AI** reopens the same entry, scope and original linked
question. A genuine correction becomes a new revision and must pass all checks.
Neither an AI review nor human approval can waive a failed retrieval check.

Earlier runs that recorded only failed test IDs receive readable descriptions
from the evaluation set when displayed. Their outcomes and stored audit records
are unchanged. Missing historical passage rankings are explicitly disclosed;
the page does not invent a cause. New failures retain the actual source passages.

## Correct existing knowledge

Use **Edit** on a published admin-authored entry to prepare a successor in the same
composer. Its current revision stays active until successful replacement.
Use the existing-document/manual editor for official-source corrections. A new
admin entry must not silently overwrite an original source policy.

## Interruptions

The current intake and review ID survive a reload in browser session storage.
Review jobs and results live in PostgreSQL. Changing facts, scope or test questions,
or changing the KB generation/review rules, requires a fresh comparison.
Sign-out clears the local working intake.

Gemini may return quota or availability errors. One transient retry is bounded and
audited; an invalid or failed report never becomes knowledge. Keep the approved
guidance and retry later, or use the manual editor with the same publication checks.

## Operator notes

- Start the existing guarded stack, including the private curation worker and n8n.
- Set `CURATION_LLM_MODEL` in `.env`; `LLM_MODEL` continues serving students.
- The default full Flash model prioritizes policy judgment. Check the actual
  project quota and set `CURATION_LLM_DAILY_CALL_LIMIT` below its RPD allowance.
  The default is 18 attempts, including retries; free-tier availability is variable.
- Migration 0006 adds review records; it does not modify existing vectors or sources.
- Back up review records with the existing PostgreSQL backup. Accepted revisions
  and active curated sources remain rebuildable through normal ingestion.
- Run the live synthetic matrix only against a disposable stack:
  `python -m eval.studio_review_eval --url URL --token-env STUDIO_TEST_TOKEN`.
  Supply the test token through the named environment variable, never a CLI literal.
- Live review evaluation never publishes. Use separate disposable data for an
  end-to-end publication test; never add demonstration policies to Oracle.
