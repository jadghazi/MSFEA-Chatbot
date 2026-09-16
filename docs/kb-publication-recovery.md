# KB publication guard — publication and recovery

Implementation stage: Steps 5–7 of `kb-publication-guard-plan.md`.

## Publication contract

Publish accepts an exact immutable revision ID and validation-run ID. FastAPI
records a publication intent and an outbox event in one transaction; the browser
receives the intent ID without changing student-visible content. n8n invokes only
the private worker endpoint for that existing intent. Before any
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
- record the committed attempt and audit event.

The student answer cache is invalidated after commit. Its versioned namespace means
an answer that began before invalidation may finish, but cannot populate a key used
by later requests.

## Serving smoke and compensation

After commit, an uncached deterministic smoke check verifies the serving index model,
the published chunk identity and its expected evidence. Linked feedback is resolved
only after this smoke passes.

If the first post-commit cache callback fails, publication compensates before
running smoke and retries cache invalidation after restoration. If smoke or other
post-commit execution fails, compensation prepares the predecessor
outside its write transaction, reacquires the shared lock, and restores that exact
revision and its chunks. A new entry is deactivated. Compensation compares the
entry's current active revision first: a delayed failure for publication A cannot
roll back newer publication B. The cache is invalidated again after restoration.
If both callback attempts fail, the database/index are still restored, but the
serving process may retain a response for the cache's 30-second TTL. Treat a
persistent callback failure as an incident: check the worker/app token and private
connectivity, and restart the app if necessary to clear process-local state before
resuming publication.

Every commit has a durable attempt in `curation_publication_attempts`. Worker startup
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
duplicate Publish, failed cache callback, delayed compensation, crash recovery,
retirement, stale rebuilds,
feedback timing, and cache invalidation including old in-flight results.

## n8n outage and workflow restoration

The worker leases `curation_outbox` events and delivers only two fixed webhook paths.
Failed deliveries back off and retry (eight attempts by default); delivered but
unfinished workflows are replayed after 20 minutes. Duplicate worker requests
return durable step/publication results. An abandoned validation run times out and
blocks after the configured deadline. These states never enter student retrieval.

If n8n is unavailable, leave the app and database running. Student `/chat` is
independent. Inspect pending/failed outbox rows and validation runs; restore n8n,
then the worker retries. A terminal outbox attempt requires operator investigation
before resetting its attempts/available time. Never mark a validation result passed
or a revision active directly in SQL.

The workflow export is `n8n/workflows/kb-publication-guard.json`. The production
Compose bootstrap imports it, publishes it, then starts n8n. The import CLI
deactivates workflows, so the separate publish job is mandatory. Restore the
separate n8n database from `deploy/backup-n8n.sh`, with the original encryption key
from secure storage; then rerun the import/publish jobs and verify both private
webhooks. n8n history may be pruned; application revisions/events/runs are the
authoritative audit and belong in the ordinary application backup.
