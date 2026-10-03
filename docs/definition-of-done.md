# Acceptance and handover criteria

Reviewed 2026-10-03. These describe product obligations and remaining outcomes.
Implementation is not proof that every case passes or that pilot outcomes occurred.
See [evaluation](../eval/README.md) for measured evidence and [backlog](backlog.md)
for work still open.

## Product obligations

| ID | Condition | Verification |
| --- | --- | --- |
| A1 | Student answers use retrieved approved evidence; no invented policies, exceptions or rationales | Source-based live-answer review |
| A2 | Insufficient evidence produces a graceful refusal and human contact; provider failures remain separate | Refusal fixtures, actual responses and error tests |
| A3 | Substantive answers cite actual retrieved documents/sections | Citation tests plus semantic grounding review |
| A4 | Visible AI-generated/verify-with-official-sources disclaimer | API/widget tests and browser inspection |
| A5 | Stay within reviewed MSFEA CDC content and resist off-topic/injection requests | Adversarial tests and reviewed answers |
| A6 | Department and conditional rules keep their applicability | Scope/condition and follow-up regression sets |
| A7 | Staff drafts cannot change serving content before valid checks and human approval | Curation fault-injection and end-to-end tests |
| A8 | Private AI writing warnings are visible; use triggers fresh review | Suggestion/backend/UI checks; review/publish enforcement |

## Quality evidence

Retrieval and answer correctness are separate. CI enforces the configured
context-recall floor (currently 0.90) and additional faculty, threshold, synthesis,
conversation, publication and conflict gates. This is a regression floor, not
a 90% answer-accuracy claim.

The original Phase 0 directional targets were at least 90% retrieval/answer
correctness, no unsupported answers in the refusal set and at most 10% false
refusals. They were provisional targets, not ratified faculty service levels.
Do not turn them into achieved claims. Report current dataset denominators,
known misses, provider errors, judge uncertainty and independent calibration status.

No safety failure is excused by a higher aggregate score. Wider acceptance requires
human agreement on the evaluation rubric and acceptable residual failure cases.

## Operational acceptance

- The app runs via Docker/Compose with environment-only configuration and secrets.
- KB ingestion rebuilds reviewed normalized files plus active approved revisions in
  one command. Normalization/approval are separate steps.
- The configured embedding fingerprint matches the serving index; `/ready` passes.
- Public HTTPS works and only the edge proxy exposes production service ports.
  Internal routes, databases, worker and n8n stay private.
- The LLM adapter boundary is retained. Gemini is currently implemented;
  cross-vendor portability requires another tested adapter.
- Backups include admin source revisions, audit, interactions and feedback, plus
  separate n8n storage and recoverable encryption key. Off-VM copies and isolated
  restoration are required.
- Deployment and publication recovery are documented; a named institutional
  engineering maintainer and CDC policy owner must be confirmed for handover.
- The embeddable script works on the actual host page with approved CORS/CSP.
  Standalone deployment alone does not verify AUB integration.

## Pilot outcome acceptance still to establish

Agree the cohort, timeframe, repetitive-email baseline and target reduction with
the department. Measure answered/refused/error counts, anonymous feedback and
unanswered-question review. Deflection rate is a useful proxy; it does not establish
email reduction or independently verified correctness.

The protected usage dashboard and Needs attention queue exist. Feedback feeds
human source/retrieval/generation improvements, never automatic retraining.
Career portals, student accounts and unrelated business workflows remain outside
the product scope in [AGENTS.md](../AGENTS.md).
