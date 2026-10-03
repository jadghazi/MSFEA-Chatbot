# ADR-0031: Show private AI drafts with advisory source warnings

Status: accepted and deployed in `2601082` on 2026-10-02.
Recorded 2026-10-03 during documentation reconciliation; this record introduces
no new runtime behavior. Supersedes ADR-0030's strict withholding rule for optional
writing suggestions, while retaining its fresh-review and publication boundaries.

## Context and decision

Staff use the optional writer as an editable assistant. Strict numeric/link and
independent-verifier rejection hid potentially useful drafts, including harmless
number-format differences. The owner explicitly requested showing the AI answer,
warnings and highlighted changes for human review.

Keep deterministic source/number/link checks and the independent verifier, but
surface their concerns as advisory warnings on a structurally usable private draft.
If the verifier fails, show the existing draft with an unfinished-check warning.
Show the highlighted additions/removals directly. Support passages, proposed factual
corrections and missing details remain inspectable.

Malformed writer output, privacy/length problems and stale context can still stop
a suggestion. Optional writing never changes serving knowledge. Use/edit records
provenance and starts fresh main review; source confirmation, all required private
checks, actual previews and named human publication approval remain enforced.

## Trade-off and evidence

Staff can inspect useful but imperfect drafts instead of receiving an opaque refusal.
They can also see an unsupported or poorly explained suggestion, so visible is not
a claim of factual approval. The student answer contract and publishing gates are
unchanged. No schema, source KB, retrieval, provider-model or dependency change
belongs to this decision.

The implementation diff at `2601082` and suggestion/backend/UI tests verify the
warning boundary and default highlighted display. The recorded release used
targeted checks; do not attribute a newly run full retrieval evaluation to this
wording/UI change.

Current behavior: [Studio](../studio.md) and [curation contract](../curation.md).
