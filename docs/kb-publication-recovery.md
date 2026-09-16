# KB publication guard — publication and recovery

Implementation stage: Step 5 of `kb-publication-guard-plan.md`.

## Publication contract

Publish accepts an exact immutable revision ID and validation-run ID. Before any
live write, FastAPI verifies that the run passed, all seven named results exist and
passed, the isolated candidate generation exists, a non-rejecting human review is
bound to the same fingerprint, and the revision is Ready. A stale fingerprint
returns `stale_validation` and creates a fresh full validation run.

Embeddings are prepared before the write lock. Publication, retirement,
compensation and normal full ingestion use the same PostgreSQL advisory lock. Once
the lock is held, publication rechecks authorization and then commits these changes
in one transaction:

- replace only the stable entry's `curated-<entry>-*` chunks;
- switch the entry's active-revision pointer and revision states;
- update the read-only legacy projection for rollback compatibility;
- recompute the content-derived KB generation;
- record the durable publication attempt and audit event; and
- enqueue the fixed-ID `publication_committed` outbox event.

The student answer cache is invalidated after commit. Its versioned namespace means
an answer that began before invalidation may finish, but cannot populate a key used
by later requests.

## Serving smoke and compensation

After commit, an uncached deterministic smoke check verifies the serving index model,
the published chunk identity and its expected evidence. Linked feedback is resolved
only after this smoke passes.

If smoke or post-commit execution fails, compensation prepares the predecessor
outside its write transaction, reacquires the shared lock, and restores that exact
revision and its chunks. A new entry is deactivated. Compensation compares the
entry's current active revision first: a delayed failure for publication A cannot
roll back newer publication B. The cache is invalidated again after restoration.

Every commit has a durable attempt in `curation_publication_attempts`. Startup/job
reconciliation can call `recover_committed_publications()` to compensate attempts
left `committed` or `smoke_failed` by a process crash. This is intentionally
fail-closed: an interrupted smoke does not get assumed successful.

There is a bounded exposure window between activation and a failing smoke rollback.
No software rollback can retract an answer already served during that interval;
the strong prepublication gates minimize this risk and the audit record preserves it.

## Retirement and rebuilds

Retirement is a direct authenticated FastAPI operation and does not depend on n8n.
It requires a reason and atomically removes the entry chunks, clears the active
pointer, updates the legacy projection, refreshes generation, and records an event.
Reactivation is not a state toggle: create a successor revision and validate it
against the then-current KB.

Normal ingestion snapshots the current generation before reading active revisions.
After embedding, it acquires the shared lock and aborts with `GenerationChanged` if
publication or retirement changed the KB meanwhile. The operator reruns ingestion
from source; a stale rebuild can never overwrite a newer publication.

## Fault-injection evidence

The publication test suite covers failure before commit, failure immediately after
commit, smoke exceptions and negative smoke results, predecessor restoration,
duplicate Publish, delayed compensation, crash recovery, retirement, stale rebuilds,
feedback timing, and cache invalidation including old in-flight results.
