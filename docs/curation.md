# Curation, validation and publication contract

Reviewed 2026-10-08 against the [deployed paid-profile alignment](archive/oracle-paid-release-20261008.md).
This is the current technical contract; staff actions are in
[Studio](studio.md), infrastructure/recovery procedures in [operations](deployment.md).
The implementation authority is `src/msfea_bot/curation/`.

## Boundaries and sources

Student retrieval uses normalized file sources plus active approved revisions through
the same chunking/store/retrieval path. Drafts, AI advice and candidate vectors
remain private. Official-source updates require reviewed normalization/ingestion;
an admin entry must not silently supersede an official file with a contradictory rule.

The dashboard can create focused admin-authored source documents with stable
`KB-<entry>` citation identity, author/responsible authority, scope, optional effective
date/reference, version and status. PostgreSQL holds their canonical source content
and history; backups are required to reproduce them. A successor replaces its own
entry's active revision rather than introducing an alternate retrieval system.

Relevant modules:
`assistance.py` (main review/budget/stages), `suggestions.py` (optional writing),
`workspace.py` (checks/previews/repair), `revisions.py` (immutable source payloads),
`validation.py` (seven checks), `publication.py` (activation/compensation),
`coordination.py` and `worker_api.py` (durable dispatch/private endpoints).

## AI review versus optional writing

Main assessment uses related evidence and structured literal claim references.
A query plan, comparison, retrieval-question preparation and independent review
normally use four staff-model calls. Missing information can stop earlier.
Classifications include new/complementary, duplicate, potential/direct conflict,
supersedes and needs clarification. Findings should refer to the same claim,
department, condition and service; semantic similarity alone is insufficient.
Comparison packets retain program/process-stage labels and one-hop reviewed
controlling context. Staff comparison remains across departments rather than
inheriting the student flow's scope exclusions. Optional writing and its verifier
receive the same applicability labels. Reviewed immutable revisions with multiple
windows form one revision bundle: retrieval restores its own eligible windows,
never an older revision or another entry sharing its title. Companion scores
cannot authorize answers below the similarity threshold.

Optional writing normally uses two calls: draft from numbered original/KB facts,
then independently check support, scope, missing details and disclosed changes.
A syntactically usable private answer is shown with highlighted edits and advisory
warnings even if numeric/link/support checks or the verifier raise concerns.
If the independent verifier is unavailable, the existing draft carries that warning.
Malformed writer output, privacy/length problems and stale review context can still
prevent a suggestion. Drafting failure leaves the input unchanged.

Optional writing is available during conflicts. This does not approve a replacement,
assert the verifier is correct or bypass main review. Use/edit records provenance and
requires fresh main assessment. Source confirmation, private checks, actual previews
and named approval apply to the new version. Saved predecessor failures remain auditable.
See [ADR-0031](decisions/0031-advisory-ai-drafts.md).

## Immutable revisions and migrations

Revision payloads are immutable; mutable workflow state is separate. Editing creates
a successor. Accepted source content, search questions, author/scope/evidence and
review records must remain associated with the exact checked version.

Startup runs checksum-verified migrations under an advisory lock; each migration
commits atomically. Modified/unknown applied SQL fails startup. Current migrations:

| Version | Responsibility |
| --- | --- |
| 0001 | Guarded revisions/state, source evidence, jobs/events/outbox; legacy backfill |
| 0002 | Validation runs/results and isolated candidate generation |
| 0003 | Durable publication attempts and recovery |
| 0004 | n8n diagnostic execution ID/outbox coordination |
| 0005 | Admin-authored source documents and provenance |
| 0006 | Guided review persistence |
| 0007 | Self-service stages, search questions and private jobs |

Legacy rows retain IDs, question/answer/author/timestamps and active/retired state.
Missing scope/approval is marked `needs_review`, never inferred. Database constraints
reject updates/deletes to revision payloads. The legacy table remains an atomic
active-content projection for read-only old binaries; old direct-publish admin writes
are incompatible and must stay disabled during rollback.

## Deterministic private checks

FastAPI records a validation run and durable jobs/outbox. The Git n8n workflow requests
these named Python steps. They do not use an LLM. `VALIDATION_DATABASE_URL` must
differ from `DATABASE_URL`; the serving chunks table is never scratch space.

| Step | What it checks |
| --- | --- |
| `schema_source` | Valid scope/program/source data, exact evidence and unexpected identifying content |
| `candidate_index` | Rebuild normalized files + active sources + candidate replacing its predecessor in an isolated index |
| `conflict_review` | Related source passages and explainable exact/numeric/negation flags for human review |
| `positive_retrieval` | Original, representative/paraphrase and prepared questions retain candidate evidence in the actual student answer context above the threshold |
| `department_isolation` | No candidate leakage across the five department filters |
| `unknown_department` | Department-only context retains explicit applicability labels |
| `regression` | Current versus candidate preservation of passing golden/multi-premise evidence |

Checks distinguish a newly lost passing case from an existing baseline miss.
Regressions concern retrieved evidence, not an LLM guarantee about every future answer.
Heuristic conflict flags are not semantic proofs; no flags means only none were flagged.

All seven results must exist and pass. Failed, missing, skipped, timed-out or stale
results cannot be waived. Human review must bind its name/role, decision and reason
to the exact run fingerprint, even when no conflict was flagged.

The fingerprint covers revision content, normalized sources, active generation,
embedding identity, retrieval settings, relevant evaluation sets, application commit
and validator version. Changes require a fresh full run; stale results are not reused.

## Search repair and answer previews

Canonical embeddings are tested first. After a measured search failure, one bounded
repair may create a successor with search-only wording. Canonical facts, scope and
original tests stay fixed; rerun the complete checks. This is not automatic policy
rewriting. A short focused entry can use the approved separate embedding text;
long entries retain ordinary section embeddings. Generation/full-text use canonical
content. Enrichment is retained only with measured justification.

Actual student-model previews run separately through the normal retrieval/prompt/
citation/disclaimer path against the private candidate. They use LLM calls and a
separate admission budget sharing the student provider quota. They are not the same
as deterministic Preview checks and never silently fall back to another model.
Human inspection remains required. Studio approval requires fresh successful
checks/previews and checks direct replacement conflicts. The lower-level manual
revision API retains deterministic checks and human-review gates without requiring
AI assistance or model previews; it is not an alternate student retrieval path.

Saved previews bind to the student model, output/thinking/sampling configuration
and generation/provider code fingerprint. A changed profile or an older preview
without this fingerprint blocks Studio approval. **Retry answer previews** reuses
valid source/retrieval checks and records the prior attempt in the event audit;
it does not create a source revision or publish anything. Source/index/validator
changes still require the complete seven checks. A profile change during generation
also invalidates that attempt.
Publication rechecks preview freshness before writes, including after a queued
intent waits for n8n. For runs with previews, named human approval must follow
their latest completion; a retry does not reuse approval of the earlier answers.

## Activation and serving smoke

Publish specifies the exact revision/run. FastAPI atomically stores an authenticated
intent and outbox event without changing serving content. n8n may invoke only its
private worker endpoint for that existing intent.

Before live writes, the application checks Ready status, fingerprint/current generation,
all seven passing results, isolated candidate generation and non-rejecting human review.
Stale validation requires a fresh run. Embeddings are prepared before the shared
write lock; authorization/generation are rechecked under it.

One transaction replaces only the entry's chunks, switches its active pointer/states,
updates the legacy projection and KB generation, and records publication attempt/audit.
Cache invalidation and uncached serving smoke follow. Linked feedback resolves only
after smoke passes. The cache namespace prevents older in-flight answers populating
newer requests' keys.

## Compensation, retirement and rebuilding

Post-commit smoke/cache failure compensates to the exact predecessor; a new entry
is deactivated. Compensation rechecks the active revision, so a delayed failure
cannot undo a newer publication. Interrupted committed/smoke-failed attempts are
reconciled on worker startup rather than presumed successful.

There is a bounded activation-to-compensation exposure window; an answer already
served cannot be retracted. Persistent cache callback failures need private-token/
connectivity diagnosis and app restart before further publication. Restored database
content alone does not clear process-local cached replies.

Retirement is an authenticated direct API action with a reason; it removes entry
chunks and updates state/projection/generation/audit atomically without n8n.
Reactivation creates a validated successor; it is not an active-state toggle.

Full ingestion snapshots generation before reading active revisions, prepares
embeddings, then acquires the same lock. If generation changed, it aborts rather
than overwriting a newer publication. Rerun from source.

Fault-injection coverage lives in publication/coordination tests; CI includes the
publication-preservation and conflict-coverage gates. Read [evaluation](../eval/README.md)
for what those fixtures measure and what they do not certify.
