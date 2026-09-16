# Guarded curation migration and compatibility

Date: 2026-09-16
Migrations: `0001_guarded_curation.sql` through `0004_n8n_coordination.sql`

## Migration contract

The curation schema is now managed by a checksum-verified, advisory-lock-protected
migration runner. A migration is applied in one PostgreSQL transaction and its
checksum is recorded only in that transaction. A changed or unknown applied
migration fails startup rather than guessing about schema state.

The first migration is additive. It creates stable entries, immutable revision
payloads, separately mutable workflow state, validation runs/results, mandatory
human-review records, audit events, durable jobs, and a webhook outbox. It does not
drop or alter `curated_answers`.

Every existing legacy row is copied one-for-one with:

- the same numeric entry ID, question, answer, author, timestamp, and active/retired
  state;
- revision number 1 and an active pointer only when the legacy row was active;
- `department = NULL`, empty programs/evidence, and
  `provenance_status = needs_review`;
- a migration audit event that explicitly says scope and approval were not inferred.

The database rejects updates and deletes to revision payloads. Edits must create a
successor revision; state transitions occur in `curation_revision_state`.

Migration 0002 allows repeated validation runs for the same revision/fingerprint and
stores the isolated candidate-index generation. Migration 0003 adds durable
publication attempts and recovery status. Both are additive; neither changes or
removes legacy content.
Migration 0004 adds a diagnostic n8n execution ID to publication attempts and an
outbox retry index. n8n IDs are never authorization or audit authority.

## Rehearsal evidence

The automated rehearsal creates an isolated PostgreSQL database, seeds both an
active and a retired legacy row, migrates twice, and verifies:

- the second execution is a no-op;
- legacy and migrated question/answer/author/state parity;
- preserved IDs and a correctly advanced identity sequence;
- missing legacy scope/evidence remains missing and marked `needs_review`;
- one migration event per legacy revision; and
- database-enforced revision immutability.

The Step 0 production inventory found zero active and zero total curated rows, so the
eventual production backfill is expected to be empty. That fact does not weaken the
non-empty migration test. No migration has been run against Oracle.

## Rollback compatibility decision

The migration is forward-compatible with the currently deployed application because
the legacy table and its columns remain intact. A student-serving rollback binary can
read the same legacy rows and chunks. Do not remove the additive tables as routine
rollback.

Old-binary **admin writes are intentionally not considered compatible**: the old
curation endpoints publish directly and bypass revision validation. If an application
rollback is needed after guarded curation is enabled, disable admin writes (unset the
admin token or block admin routes) until the guarded release is restored. Step 5 must
keep the legacy table as an atomic active-content projection so a read-only old binary
can still serve the last published content. This restriction is explicit rather than
silently claiming full rollback compatibility. The guarded release now keeps the
legacy table as an atomic active-content projection and has exercised that path
under publication/compensation fault injection.

## Operator command

Run the migration in the application image with:

```text
python -m msfea_bot.curation.migrations
```

Normal application startup also invokes the runner before accepting traffic. Migration
failure prevents readiness; it cannot leave a partially applied schema.
