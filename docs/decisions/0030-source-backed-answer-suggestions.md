# ADR-0030: Optional source-backed answer suggestions

Status: implemented and deployed on Oracle, 2026-10-01. Extends the existing Studio.

Use the existing bounded assistance worker and provider abstraction for two
optional calls: draft a focused revision from numbered original/source claims,
then separately verify factual support, disclosure of changed meaning, scope, and
whether missing-detail questions are essential. Writing assistance is available
even during conflicts and possible replacements. Any proposed correction to an
original claim requires exact before/after quotes, a reason and existing KB facts.
Code rejects undisclosed removal of original numbers/URLs and invented values.
The first implementation blocked conflict rewrites after an LLM verifier missed
a 3-to-1-credit change. That was too restrictive for an answer-writing assistant.
The revised boundary allows visible, source-backed corrections for staff review;
it does not authorize a policy update. 'Normally summer' cannot become either
'winter permitted' or 'winter prohibited' without supporting evidence.

Keep the proposal separate from the input. Show tracked changes, explanation,
literal supporting facts, remaining questions and explicit use/edit/discard
choices. Acceptance records provenance and enqueues a normal fresh review;
source confirmation, private checks/previews and human publication approval apply
to the new version. Saved drafts retain their earlier versions and failures.
Official-source corrections continue through their source/ingestion workflow.

Reuse the existing assistance table with a distinct prompt version, shared model
budgets and request deduplication. No migrations, service, dependency, alternate
retrieval path or student-provider changes. The trade-off is two extra calls and
possible service failure; optional requests preserve the original answer. AI
suggestions cannot guarantee policy correctness or repair retrieval regressions.

See [acceptance](../studio-answer-suggestion-plan.md) and
[the measured review](../studio-answer-suggestion-quality-report.md).
