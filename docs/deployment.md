# Deployment and operations

Reviewed 2026-10-08 against the current Compose files and paid student/Studio release.
Oracle pilot location: `/opt/msfea-chatbot`; public hostname:
`msfea-chatbot.duckdns.org`. A different institution can supply its own host/domain
without changing application code. Dated rollout evidence is in [the archive](archive/README.md).

## Configuration and topology

Use [.env.example](../.env.example) and [config.py](../src/msfea_bot/config.py) as the
configuration inventory. Keep real secrets in `.env` or the operator's secret store.
Set `LLM_PROVIDER=gemini`, the student model/key, `ADMIN_TOKEN`, `DOMAIN`,
`CORS_ALLOW_ORIGINS` and `APP_COMMIT` for the exact running release.
Use independent `CURATION_WORKER_TOKEN`, `N8N_WEBHOOK_SECRET`, `N8N_DB_PASSWORD`
and persistent `N8N_ENCRYPTION_KEY`. Do not reuse the admin token.

The deployed paid student profile uses `LLM_MODEL=gemini-3.8-flash`,
`LLM_MAX_OUTPUT_TOKENS=4096`, `LLM_GEMINI_THINKING_LEVEL=medium` and
`LLM_GEMINI_USE_SAMPLING_PARAMS=false`. The limit includes reasoning and visible
output. Staff assistance remains `CURATION_LLM_MODEL=gemini-3.1-flash-lite`;
actual student previews use the student profile. Rotate only the intended provider
key/configuration fields; preserve production database, admin, workflow and domain
settings. See the [dated rollout](archive/oracle-paid-release-20261008.md).


The base stack is app + PostgreSQL/pgvector. The production overlay adds Caddy,
the private worker, self-hosted n8n and its PostgreSQL 17 database. Validation is
a separate database (`msfea_validation`) on application PostgreSQL, not another
permanent database container. Initialization/import/publish jobs exit after setup.

Only Caddy exposes 80/443. The overlay removes app/database host ports. Internal
routes return 404 through the public proxy. Keep databases, worker and n8n private;
never give n8n a Docker socket, shell node or application DB credentials.
n8n's internal network has no external egress; the worker bridges application and
workflow networks. Student chat does not depend on n8n.

## Release procedure

Use an authorized, verified commit and inspect the diff and relevant evaluation
evidence. Do not copy synthetic demo data or a developer's database into production.

1. Check CPU/RAM/disk capacity and fresh application/n8n backups. Preserve off-VM
   copies and the encryption key; rehearse schema/image changes on isolated restores.
2. Update source at the exact release commit and set `APP_COMMIT` to that SHA.
   Git/build files must be readable by the non-root image user: use normal
   `umask 022` for checkout/build and restrict secrets/backups separately.
3. Build the exact target image natively for the host architecture before switching.
   Startup applies pending checksum-verified curation migrations. Current code has
   migrations 0001–0007; never modify already-applied SQL files.
4. For an existing installation with unchanged dependencies/workflow, recreate
   only the affected services after the native build:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps app curation-worker
```

   For initial/full-stack setup:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

5. Ingest only when the source/index/embedding change requires it. A documentation
   update does not need rebuild, ingestion or deployment. When a release requires
   both new retrieval code and content, stop the app/worker briefly, ingest with the
   new image, then recreate them so old code cannot serve the new index. For a
   content-only rebuild with compatible running code:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm app python -m msfea_bot.skeleton ingest
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart app
```

6. Verify public `/health` and `/ready`, embedding/index compatibility, expected
   generation/content, citations/links and department/follow-up smoke answers.
   Verify private services and the workflow where affected. Do not run index-rebuilding
   pytest fixtures against Oracle. Use isolated regression databases.
7. Record commit/image/configuration, observed results and remaining failures in
   a dated release record. Never describe old measurements as a new verification.

If a rebuild aborts because the generation changed, rerun from reviewed source.
Never force a stale candidate index over a newer publication.

## HTTPS, CORS and worker count

Caddy obtains certificates when DNS points to the host and ports 80/443 are open.
[deploy/Caddyfile](../deploy/Caddyfile) is the default.
[The nginx template](../deploy/nginx.conf) supports IT-managed TLS; supply its
domain/certificate paths and review the actual private upstream arrangement.

`CORS_ALLOW_ORIGINS` should contain exact host-page origins. Empty denies
cross-origin browser access while allowing same-origin. CORS does not stop direct
API callers. Enable `TRUST_PROXY_HEADERS` only behind the trusted single proxy
with no direct public backend access. Additional CDNs/proxy hops need a trust review.

Use one Uvicorn app worker/instance: rate limits, concurrency guard, response cache
and usage counters are process-local. Offline ingestion requires app restart to
clear cached answers; guarded publication invalidates them automatically.

## Admission controls and provider failures

| Layer | Current bounds/defaults |
| --- | --- |
| HTTP/question/history | 64 KiB body; 2,000-character question; eight history messages, 1,200 characters each |
| IP | Configurable minute window, default 60/minute; also 12/5 seconds and 300/hour |
| Browser session | 20/minute, 80/hour; session IDs are not authentication |
| Expensive concurrency | One/session, four/IP, sixteen/app worker |
| Response reuse | Exact effective session/context, 30 seconds, bounded 256 entries |
| Evidence/output | 24,000 context characters; code output default 1,024 tokens, deployed paid profile 4,096 |
| Staff AI | Default 12 attempts/minute, 400/day/model |
| Student-model previews | Separate 60-call daily admission cap; shares student provider quota |

Runtime `.env` overrides can differ. The local demo's 500 staff attempts/day override
is not the Oracle/default setting. Daily caps count calls/attempts, not entries;
a routine assessment uses multiple calls and previews use the student model.
Provider quotas depend on project/model and other usage; inspect the actual
allowance before changing budgets. Do not hard-code a universal free-tier limit.

The Gemini SDK has one attempt; the application allows one transient retry
after 0.5 seconds. Student timeout is 30 seconds per attempt. Staff calls can set
their own timeout. Quota errors do not get an automatic transient retry.
Transient failure responses are not cached; rate-limit cooldown responses can be.
For a provider outage, preserve saved drafts, explain the service failure and retry
when available. Do not turn a transport failure into a content judgment.

## n8n import, editor and workflow recovery

The exported workflow is [kb-publication-guard.json](../n8n/workflows/kb-publication-guard.json).
Import deactivates workflows, so the separate publish bootstrap job is required.
After a workflow change, rerun the import/publish jobs and restart n8n:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm n8n-import
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm n8n-publish
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart n8n
```

n8n process health does not prove webhook activation; short startup 404s are retried
by the durable outbox. Workflows accept only existing validation/publication IDs.

For visual maintenance, use the optional loopback editor proxy and SSH tunnel:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.n8n-editor.yml up -d --no-deps n8n-editor
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.n8n-editor.yml stop n8n-editor
```

It binds `127.0.0.1:5678`; never expose the editor publicly. Closing the editor
does not require stopping n8n.

If n8n is down, leave app/db serving. Stop only the worker if dispatch must pause;
drafts/jobs/intents remain in PostgreSQL. Restore n8n/database/key, rerun
import/publish, verify private webhooks, then resume the worker.

Inspect `curation_outbox`, `curation_jobs`, `curation_validation_runs`,
`curation_publication_attempts` and `curation_events`. Delivery retries default
to eight attempts; delivered-but-unfinished work can replay after 20 minutes.
A terminal outbox event needs investigation. Only after verifying its run/intent
remains valid may an operator requeue that exact event and record the incident.
Stale/timed-out checks need fresh validation. Never directly mark results passed
or set a revision active.

## Backups and restore

Application backups contain source revisions, audit/workflow records, interactions,
ratings and experience feedback as well as derived chunks. n8n storage is separate;
its execution history is not the application audit.

```bash
./deploy/backup.sh
./deploy/backup-n8n.sh
sudo ./deploy/install-backup-timer.sh
sudo systemctl start msfea-chatbot-backup.service
systemctl list-timers msfea-chatbot-backup.timer --no-pager
```

The systemd timer runs at 02:00 in the VM's local timezone, with up to 15 minutes'
random delay, catches up after downtime and retains 14 days locally. Verify both
dumps and copy them off the VM. Keep `N8N_ENCRYPTION_KEY` recoverable separately.

Rehearse restoration in disposable databases with `psql -v ON_ERROR_STOP=1` and
validate records/workflow import. [restore.sh](../deploy/restore.sh) is destructive
and targets the configured application database; do not use it as a routine
rollback or an isolated-restore command without adapting the target deliberately.
Old full-database restoration can erase newer interactions and approvals.

Prefer migration-compatible image rollback. Older direct-write admin endpoints
must stay disabled; additive tables do not make old admin behavior safe.
[The curation contract](curation.md) details compensation after failed activation.

## Ownership and security maintenance

The CDC policy owner decides source authority, exceptions and replacements.
Engineering owns infrastructure, backups, source ingestion and incident recovery.
Reviewer names/roles are self-reported under a shared admin token, not verified
identity or two-person approval. Confirm institutional owners at handover.

Redaction is best effort; keep the baked local NER model available and do not
claim complete anonymization. Review dependency advisories on the built image,
public-port/proxy assumptions and real quota/capacity periodically. Historical
security audits are dated evidence, not a current blanket security certification.
