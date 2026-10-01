# Source-backed answer suggestions — acceptance

2026-10-01. Add an optional editable revision within the existing Studio, using
the current bounded worker and provider abstraction. No new service or dependency.

- Offer a suggestion after completed AI review and for private saved revisions
  needing correction. Bind it to the original guidance, scope, failure snapshot
  and KB generation. Persist requests/results in the existing assistance jobs.
- Compare original/proposed text visibly. Highlight additions/removals, show why
  changes help, literal supporting sources and remaining questions for staff.
- Make writing assistance available for all completed review outcomes, including
  conflicts, possible replacements and duplicates. Corrections to original claims
  require existing KB evidence, exact before/after quotes and an explanation.
- Independently check every proposed sentence against supplied facts, disclose
  changes to meaning/conditions/numbers/links, preserve scope, and reject unsupported output. Missing
  opening hours/deadlines/authority must remain questions rather than guesses.
- Use, edit and discard are explicit choices. Original input stays intact until
  acceptance. Accepting an edited or unedited suggestion records its provenance,
  starts fresh AI review and leaves previous drafts/checks in history. Existing
  source confirmation, seven checks, previews and publication approval remain.
- Failed unrelated retrieval questions inform focused wording, but their policy
  facts cannot be copied into unrelated guidance. No promise of passing tests.
- Verify stale requests, quota/provider failures, refresh, XSS, unsupported facts,
  conflicting numbers, short complete answers and changed scope. Measure source
  coverage on fixed examples before/after; run existing retrieval gates unchanged.
- Visually exercise accept/edit/discard, direct intake and a saved-draft revision
  in the local disposable stack, including mobile. Never publish fictional facts
  in Oracle; verify live suggestion/review plumbing on existing official content.
