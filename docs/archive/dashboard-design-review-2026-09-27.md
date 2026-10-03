> Historical local review. This predates the current guides and later implementation/approval decisions; it is not current operating guidance. Start with [the documentation index](../README.md).

# Desktop dashboard refinement — local review

Scope: the existing admin workspace, especially Usage. No chatbot retrieval,
generation, source ingestion, publication guards, or student tracking changed.
No new dependency. No Git push or Oracle deployment.

## Design and rationale

Persistent left navigation separates monitoring from knowledge maintenance. Usage
is the initial view, with four primary measures: questions logged, answer rate,
unresolved items from the selected period, and helpfulness among submitted answer
ratings. The other views share the same typography, spacing and restrained maroon
accent. Attention items show the question first and expand their correction form
on demand. Validation and human review before publishing remain in place.

Research used:
- [NN/g: Dashboards, charts and graphs](https://www.nngroup.com/articles/dashboards-preattentive/):
  use position and length for comparisons. Daily stacked bars and ranked source
  bars have numeric labels/table equivalents; no decorative gauges or pie charts.
- [NN/g: Progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/):
  keep common decisions visible and reveal secondary detail as needed. Applied to
  generation diagnostics and correction forms, without hiding the review queue.

These are design decisions, not evidence of better student answer quality or a
completed admin usability study.

## Reporting contract

New authenticated read-only endpoint: `/admin/api/analytics?days=7|30|90`.
Existing `/stats` and process-local `/usage` contracts remain unchanged.

The window includes today (partial) and preceding calendar days in UTC. All
aggregates come from a consistent PostgreSQL snapshot of existing interactions.
Missing days are zero-filled. Missing token/latency measurements remain null.

| Measure | Definition / limitation |
| --- | --- |
| Questions logged | Persisted interactions in the period; not unique students or sessions. Rejected requests and logging failures are outside this count. |
| Answer rate | Answered / (answered + refused). Excludes temporary service errors. Does not prove correctness, task resolution or email deflection. |
| Needs review | Unresolved refusals or thumbs-down, excluding service errors, for questions in the selected period. Sidebar badge and attention queue remain all-time. |
| Helpful rating | Thumbs-up / all submitted answer ratings. No ratings shows an em dash. |
| Rating participation | Rated interactions / all logged interactions in the period. |
| Daily activity | UTC daily counts, split into mutually exclusive answered, refused and temporary failure outcomes. Exact values in an expandable table. |
| Unanswered questions | Top five exact question matches among unresolved refusals in the period. Not semantic topic clustering. |
| Source usage | Top five citation labels (document + section), counted once per interaction per label. An answer can cite several labels. |
| Citation presence | Answered interactions with at least one saved citation / all answered interactions. Not citation accuracy. |
| Negative reasons | Reasons attached to thumbs-down ratings on questions from this period, including an explicit missing-reason group. |
| Generation details | Mean and p95 provider latency plus recorded input/output tokens; sample counts shown. Excludes retrieval/client network latency. Not a cost estimate. |

No department breakdown, unique-user count, monetary cost, email reduction,
uptime, or answer-accuracy score is fabricated from fields the logs do not have.
Whole-experience feedback remains separate and anonymous; it is not joined to
questions or treated as period-filtered Usage data.

## Acceptance checks and evidence

Before changing the page, recorded screenshots and layout counts with the same
synthetic admin API fixtures. Artifacts are in `artifacts/ui/dashboard-refinement`.

| Check | Before | After |
| --- | --- | --- |
| Equally prominent Usage metric cards | 10 | 4 primary metrics; supporting sections below |
| Date-range choices | 0 | 7 / 30 / 90 days |
| Daily trend / exact daily table | Neither | Both |
| First-screen activity chart at 1024, 1280, 1440 × 900 | Absent | Visible at all three widths |
| Horizontal page overflow at those desktop sizes | None | None |
| Automatically expanded correction forms per queue item | 1 | 0; opens on request |
| Missing-rating or missing-latency display | Zero-like values | Explicitly unavailable |

Also checked 390px as a fallback layout, with no horizontal overflow. This pass
is focused on desktop, not a full physical-mobile-device assessment.

Validation:
- 40 Python tests passed: admin endpoints, frontend contracts, and new reporting
  tests. Reporting integration checks ran against a disposable PostgreSQL 17
  database in a dedicated schema; no production data involved.
- 11 Node tests passed: five reporting behavior tests and six existing widget
  submission checks. Covers denominator differences, null/empty data, escaping,
  out-of-order range responses, failure and retry.
- Browser checks: range changes; daily-table and diagnostics disclosure; direct
  navigation into review/feedback; all six navigation views; correction-form
  disclosure and source-kind switching; empty answer validation; preserving an
  unsaved knowledge draft on refresh; reporting failure/retry and empty period;
  sign-in/sign-out; no browser JavaScript exceptions.
- Ruff passed on changed Python files; strict mypy passed on the reporting module
  and API module. `git diff --check` passed.
- New Node tests and database reporting tests are wired into existing CI. CI has
  not run remotely; these changes remain local.

Reproduction of local presentation review:

```powershell
node tmp/dashboard-refinement/fixtures.cjs
python tmp/dashboard-refinement/preview.py
node tmp/dashboard-refinement/check.cjs
node --test tests/dashboard_usage.test.cjs tests/widget_submission.test.cjs
```

The temporary preview at `http://127.0.0.1:8766/dashboard/` injects a prominent
synthetic-data banner and serves read-only fixture endpoints. It is not part of
the deployed dashboard. Production assets contain no demo data or auth bypass.
The backend and dashboard assets must be released together because the new
reporting view requires the new endpoint.
