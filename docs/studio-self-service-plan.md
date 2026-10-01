# Self-service Studio acceptance and implementation plan

Recorded before implementation, 2026-10-01. All demo data is synthetic and all
publication exercises use the isolated local demo, never the Oracle pilot.

The admin describes approved guidance, resolves actual policy questions, previews
the result and publishes in one workspace. Technical search preparation belongs
to the system. LLM advice never overrides factual approval or measured checks.

Acceptance:

- One resumable Describe / Resolve / Preview / Publish workspace serves direct
  knowledge intake, unanswered questions and updates. No forced trip through a
  technical draft editor or handwritten search tests on the routine path.
- Separate durable AI stages interpret the intake, compare literal source claims,
  prepare focused retrieval questions and independently verify factual coverage.
  Clarification is specific and grouped; unrelated passages stay in audit details.
- Gemini 3.1 Flash-Lite is the routine model, using the existing thin provider.
  Attempts are audited and paced; configurable model budgets replace the old
  18/day and 4/minute assumptions. No student-model quota fallback.
- Canonical guidance remains unchanged. Retrieval questions are versioned source
  data, embedded separately, and never appear as factual answer evidence.
- Candidate validation is reproducible against the same source generation.
  Diagnose and fix the advising/letter failure with measured retrieval evidence.
  Never waive tests or rewrite unrelated policies to get a green result.
- Bounded AI repair uses actual failed retrieval evidence, preserves canonical
  facts, and creates a private successor requiring fresh checks and staff approval.
- Actual answer previews use the existing student prompt/provider against the
  private candidate index, with citations and disclaimer. Quota failure is a
  service condition, never a false successful preview.
- Named human approval and atomic publication remain mandatory. Original feedback
  resolves only after successful publication. Existing Studio updates replace
  the active predecessor; official-document changes are not silently authorized.
- Independently authored questions test new-entry retrieval; the original golden,
  follow-up, synthesis, scope and department gates protect existing behavior.
- Exercise routine success, contradictions, duplicates, missing scope/conditions,
  unsupported question, stale edits, retries, refresh, concurrent submissions,
  quota failures and narrow-screen/keyboard interaction.

Keep the existing PostgreSQL jobs, Python worker and n8n publication coordination.
No new service, hosted vector database, framework or autonomous agent platform.
Document measurements separately from design targets and faculty usability claims.
