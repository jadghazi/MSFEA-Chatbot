# KB publication guard — operator handover

Status: implementation and disposable-stack rehearsal only. **Do not apply this
runbook to Oracle until the owner explicitly approves the tested commit.** The
Oracle student-serving release remains unchanged.

## Ownership and scope

The CDC policy owner is responsible for source authority, applicability, conflict
decisions and replacement of outdated rules. An administrator may enter a reviewer
label, but the shared admin token authenticates only the admin role: the audit does
not prove individual identity or two-person approval. Engineering owns deployment,
backups, migrations, re-ingestion and incident recovery. n8n only sequences named
worker requests; PostgreSQL application records are the audit source of truth.

Student chat has no n8n dependency. The single Git-exported workflow is
`n8n/workflows/kb-publication-guard.json`. It has validation and publication
branches, accepts only IDs, and uses dedicated internal tokens. n8n must not be
given a public host port, Docker socket, shell node or application database access.
The production Compose network for n8n/n8n-db is Docker-internal with no external
egress; only the worker bridges it to the app network. This avoids n8n's unrelated
catalog/registry fetches and narrows the available destinations.

## Source intake and guarded review

1. Preserve the authoritative original under `kb/source/` and review its normalized
   Markdown in `kb/normalized/`. Correct extraction, section metadata and source
   provenance there; do not hand-edit pgvector rows. Unknown source approval dates
   remain unknown. See `kb/README.md` and `docs/kb-scope-provenance-audit.md`.
2. After reviewed Markdown changes, run the normal one-command ingestion on an
   isolated candidate first. The rebuild reads normalized Markdown plus active
   curated revisions; it does **not** re-extract originals. Check the 210-chunk
   baseline and evaluation deltas before a production rebuild. A concurrent
   publication changes the generation and makes a stale ingestion abort; rerun it
   from source rather than forcing its output into the database.
3. In the admin dashboard, save an exact immutable draft or successor. Scope,
   program, source locator/excerpt, paraphrase, expected evidence and change reason
   are mandatory. Saving a draft cannot modify student retrieval or resolve feedback.
4. Request validation. n8n invokes seven deterministic Python checks in order in
   the isolated `msfea_validation` database. It makes no Gemini calls. The dashboard
   polls while validation or publication is pending; errors remain attached to the
   run. A failed/missing/stale/timed-out check is blocking and cannot be waived by
   the reviewer.
5. Inspect source evidence and every related passage, including potential-conflict
   flags. “No potential conflicts flagged” is **not** a conflict-free certification.
   Record a decision and reason for this exact run even if there are no flags.
   Correct/reject a bad draft, or confirm a defensible scoped exception. For an
   outdated Markdown policy, correct and re-ingest the canonical source first; do
   not publish a contradictory curated rule alongside it.
6. Publish the exact Ready revision/run in the dashboard. FastAPI records an
   authenticated intent, and returns before activation. n8n may only ask the
   private worker to execute that existing intent. The worker rechecks fingerprint,
   active generation, full results and review, then atomically changes chunks and
   active pointer. Serving smoke and cache invalidation follow; linked feedback is
   resolved only after success. Retirement is a direct admin action with a reason.

## Production preflight — only after owner approval

- Confirm the approved Git commit, image digest, chosen provider/model and the
  Step 6 answer/eval report; set `APP_COMMIT` to that exact Git commit. No prompt,
  model, sampling, normal top-k or threshold change belongs in this rollout.
- Confirm Oracle ARM64 and headroom immediately before scheduling. The tested n8n
  `2.39.5` image publishes ARM64/AMD64; its separate PostgreSQL image is 17.
  Budget 768 MiB/0.75 CPU for n8n and 2 GiB/0.75 CPU for the worker, then observe
  chat latency under real load. Do not provision paid resources without a new
  decision.
- Generate independent `CURATION_WORKER_TOKEN`, `N8N_WEBHOOK_SECRET`,
  `N8N_DB_PASSWORD` and `N8N_ENCRYPTION_KEY`. Keep the encryption key recoverable
  outside the VM. Set `DOMAIN`, `CORS_ALLOW_ORIGINS`, `ADMIN_TOKEN`, provider secrets
  and the application/validation URLs in `.env`; never commit `.env`.
- Verify the daily application backup timer, create a fresh application dump, copy
  it off the VM, and restore it to an isolated database. Existing curation/audit,
  interactions and feedback must survive. Back up the n8n database separately after
  it is initialized; the revised daily systemd unit runs both dumps, and a failed
  second dump marks the unit failed. Rehearse a separate restore with the original encryption
  key. A local dump alone does not protect against VM/boot-volume loss.
- Rehearse migration 0004 and the exact image/Compose stack against an isolated
  restored application DB. Confirm legacy row/content parity and student-serving
  rollback compatibility. Old binaries may serve students after an additive
  migration, but old admin curation endpoints must remain disabled because they
  bypass the guard.
- Run Ruff, strict mypy, all Python/widget tests, retrieval/threshold/synthesis,
  publication/conflict gates and the frozen live-answer review as in the Step 6
  quality report. No newly lost passing evidence case or unexplained answer change
  is acceptable.

## Start and verify the workflow

The production Compose overlay creates `msfea_validation` on the existing app
PostgreSQL server, then starts a private worker. It creates a separate n8n
PostgreSQL 17 service/user. The `n8n-import` job imports the sanitized JSON from
Git. n8n's CLI **deactivates on import**, so `n8n-publish` explicitly publishes
the workflow before the n8n server starts. After a workflow change on an already
running server, restart n8n to load its new published version.

Only Caddy may publish 80/443. The optional `docker-compose.n8n-editor.yml` starts
a temporary loopback-only proxy at `127.0.0.1:5678`; use an SSH tunnel, never a
public port, and stop that proxy after maintenance. Start only the editor service
with `docker compose -f docker-compose.yml -f docker-compose.prod.yml -f
docker-compose.n8n-editor.yml up -d --no-deps n8n-editor`; stop it with the same
file list and `stop n8n-editor`. Do not stop the main n8n service just to close the
editor. Verify
`docker compose ... ps`, public `/health` and `/ready`, and a public request to
`/internal/cache/invalidate` returning 404. Check all five departments plus an
unknown-department conditional question against the approved baseline. The private
worker `/internal/health` requires its own token. The n8n `/healthz` endpoint
signals process health, **not** that webhooks have finished activating; startup can
briefly return webhook 404, which the outbox retries.

## Outages and recovery

- If n8n fails, leave app/db serving. Stop only `curation-worker` to disable
  dispatch if necessary; drafts/intents remain durable and student chat continues.
  Restore n8n, verify the workflow is published/active, then start the worker.
- Check `curation_outbox` status/attempts/last_error, `curation_jobs`,
  `curation_validation_runs`, `curation_publication_attempts` and
  `curation_events`. Never edit result rows to claim a pass or directly set a
  revision Active. Worker lease reconciliation retries transient work; abandoned
  runs/intents fail closed at their configured deadlines.
- An outbox event that exhausted eight delivery attempts does not silently
  publish. After verifying the fixed webhook and underlying run/intent are still
  valid, an operator may requeue **that exact row** by setting its attempts to 0
  and `available_at=now()`; record the incident. A stale/timed-out run requires a
  fresh full validation, not a replay into Ready.
- A committed attempt interrupted before smoke is compensated on worker startup.
  Compensation restores only the predecessor still associated with that exact
  attempt; it cannot undo a newer publication. See
  `docs/kb-publication-recovery.md` for the bounded post-commit exposure risk.
- A failed post-commit app cache callback compensates before smoke and retries
  invalidation. If the callback remains unavailable, the database/index are
  restored but process-local cached replies can live for their 30-second TTL
  after completion of any in-flight answer;
  resolve the worker/app token or connectivity and restart the app before
  resuming publication. Inspect attempt `error_code=cache_invalidation_failed`.
- Restore the n8n database and original encryption key together on a fresh stack,
  rerun import/publish from Git, restart n8n and verify private webhooks. Execution
  history is pruned and never substitutes for the application audit backup.
  Application rollback should use a migration-compatible image; do not routinely
  restore an old full DB dump over newer student interactions.

## Evidence from disposable rehearsal

On 2026-09-16, n8n 2.39.5 imported and published the Git workflow against a
separate PostgreSQL 17 container. A fresh app DB ingested 210 chunks. A real
validation webhook completed 7/7 Python checks in the isolated validation DB;
human-review gating held a flagged revision Blocked until a clearly labeled local
test review was recorded. FastAPI returned an intent, then n8n called the worker;
one reviewed revision was smoke-checked Active. Duplicate validation and publication
webhooks changed neither job attempts nor KB generation. The Caddy test returned
200 for `/health` and 404 for both `/internal` and an internal callback path.
After moving n8n to the Docker-internal network, the worker still reached both
the app and n8n, the optional loopback editor proxy reached `/healthz`, and an
outbound request from n8n to `api.n8n.io` timed out as intended.
Stopping n8n during a successor validation kept the predecessor live and a local
student `/chat` greeting working; the durable event resumed after n8n activation.
The n8n database was dumped in custom format and restored into a separate local
`n8n_restore` database, with the workflow row present. This does not verify an
off-VM backup copy or a production encryption-key restore; those remain release
preflight checks.
The scheduled backup scripts were also exercised against the disposable stack:
both compressed SQL files passed `gzip -t`, and both were restored into separate
local databases with `psql -v ON_ERROR_STOP=1`. The n8n restore contained one
workflow; the application restore contained 211 chunks, two curated revisions,
and 12 curation events. These local restores do not substitute for an off-VM copy
or an Oracle restoration rehearsal.
These are engineering fixtures, **not** CDC policy approvals or Oracle deployment.

After Step 7 integration, the independent RAG gates remained at golden context
recall 67/68, threshold 109/109, off-topic pre-LLM blocking 11/20, and
synthesis/follow-up/scope 27/27. The frozen publication scope sample passed 9/9
across CEE, CHEM, ECE, IEM, MECH and unknown-department cases; conflict candidate
evidence remained 7/7, with two known false-positive fixtures still reported.
These are unchanged measured results, not a claim that all unsupported questions
are blocked.
The final local code gates passed: Ruff, strict mypy (51 source files), 270 Python
tests and three widget tests. The two Python warnings are upstream
TestClient/AnyIO deprecations.
