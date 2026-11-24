# Deployment and operations

Use this guide to deploy the chatbot behind the department's existing Caddy
reverse proxy. The [archive](archive/README.md) records the earlier Oracle pilot
releases and their serving topology.

## First installation

1. Check out the approved release on the department's Docker host. Confirm the
   public hostname with IT and reserve host port 9000 for the app. Run the
   commands from the checkout. For a new installation, create the environment
   file with restricted permissions.

   ```bash
   install -m 600 .env.example .env
   git rev-parse HEAD
   ```

2. In `.env`, set `APP_COMMIT` to the printed SHA and configure the
   institution's Gemini project, admin token and independent worker and n8n
   secrets listed below. Set `CORS_ALLOW_ORIGINS` to the exact host-page origins
   if another website will embed the widget.
3. Validate the Compose configuration, start the production stack and build the
   initial index from the reviewed knowledge files in Git.

   ```bash
   docker compose -f docker-compose.prod.yml config --quiet
   docker compose -f docker-compose.prod.yml up -d --build
   docker compose -f docker-compose.prod.yml run --rm app python -m msfea_bot.skeleton ingest
   docker compose -f docker-compose.prod.yml ps -a
   curl -fsS http://127.0.0.1:9000/health
   curl -fsS http://127.0.0.1:9000/ready
   ```

   Expect `{"status":"ok"}` and `{"status":"ready"}`, respectively. The
   readiness probe returns 503 until the initial index is populated and
   compatible with the local embedding model. The `validation-db-init`,
   `n8n-import` and `n8n-publish` setup jobs should exit successfully. The app,
   databases, worker and n8n should be running and healthy. If a service is
   still starting, wait for it to finish and repeat the checks.
4. Add the [example Caddy site block](../deploy/Caddyfile) to the department's
   existing configuration, substituting the assigned hostname. Have the proxy
   operator validate and reload the shared configuration using their normal
   process. See [HTTPS, CORS and worker count](#https-cors-and-worker-count)
   if Caddy uses a separate network namespace or host.
5. Verify the same health and readiness responses over HTTPS. Replace the example
   hostname in these commands. Each internal path should return 404.

   ```bash
   curl -fsS https://chatbot.aub.edu.lb/health
   curl -fsS https://chatbot.aub.edu.lb/ready
   curl -sS -o /dev/null -w '%{http_code}\n' https://chatbot.aub.edu.lb/internal
   curl -sS -o /dev/null -w '%{http_code}\n' -X POST https://chatbot.aub.edu.lb/internal/cache/invalidate
   ```

   Open the student page and ask a known in-scope question. Verify the answer,
   citations, disclaimer and source destinations. Sign in at `/dashboard/` and
   confirm that staff can access the expected Studio and feedback views. Confirm
   backups and their owners before opening the service to students.

## Configuration and topology

Use [.env.example](../.env.example) and [config.py](../src/msfea_bot/config.py) as the
configuration inventory. Keep real secrets in `.env` or the operator's secret store.
Set `LLM_PROVIDER=gemini`, `LLM_API_KEY`, the student and staff models,
`ADMIN_TOKEN`, `CORS_ALLOW_ORIGINS` and `APP_COMMIT` as appropriate.
Use independent `CURATION_WORKER_TOKEN`, `N8N_WEBHOOK_SECRET`, `N8N_DB_PASSWORD`
and persistent `N8N_ENCRYPTION_KEY`. The example environment file documents how
to generate secret values. Keep a recoverable copy of the n8n encryption key.

The deployed paid student profile uses `LLM_MODEL=gemini-3.8-flash`,
`LLM_MAX_OUTPUT_TOKENS=4096`, `LLM_GEMINI_THINKING_LEVEL=medium` and
`LLM_GEMINI_USE_SAMPLING_PARAMS=false`. The limit includes reasoning and visible
output. Staff assistance remains `CURATION_LLM_MODEL=gemini-3.1-flash-lite`;
actual student previews use the student profile. Rotate only the intended provider
key/configuration fields; preserve production database, admin, workflow and domain
settings. See the [dated rollout](archive/oracle-paid-release-20261008.md).

The standalone production Compose file starts the app, PostgreSQL/pgvector, the
private worker, self-hosted n8n and n8n's PostgreSQL 17 database. Validation uses
the separate `msfea_validation` database on application PostgreSQL.

The app is the only service with a published port. It serves on host port 9000
and keeps its internal container port 8000. Keep databases, the worker and n8n
private. Never give n8n a Docker socket, shell node or application DB credentials.
n8n's internal network has no external egress. The worker connects the application
and workflow networks. Student chat runs independently of n8n.

## Release procedure

Use an authorized, verified commit and inspect the diff and relevant evaluation
evidence. Keep the existing Compose project name when updating an installation
so it continues to use the same volumes. If migrating a release with bundled
Caddy, coordinate its retirement and the proxy cutover with the operator. Keep
synthetic demo data and developer databases out of production.

1. Check CPU/RAM/disk capacity and fresh application/n8n backups. Preserve off-VM
   copies and the encryption key; rehearse schema/image changes on isolated restores.
2. Update source at the exact release commit and set `APP_COMMIT` to that SHA.
   Git/build files must be readable by the non-root image user: use normal
   `umask 022` for checkout/build and restrict secrets/backups separately.
3. Build the exact target image natively for the host architecture before switching.
   Startup applies pending checksum-verified curation migrations. Current code has
   migrations 0001–0009; never modify already-applied SQL files. Rollbacks must
   retain recognition of applied migrations, including the discarded-draft state.
4. For an existing installation with unchanged dependencies/workflow, recreate
   only the affected services after the native build:

```bash
docker compose -f docker-compose.prod.yml up -d --no-deps app curation-worker
```

   For a full-stack update:

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml ps -a
```

5. Ingest only when the source/index/embedding change requires it. A documentation
   update does not need rebuild, ingestion or deployment. When a release requires
   both new retrieval code and content, stop the app/worker briefly, ingest with the
   new image, then recreate them so old code cannot serve the new index. For a
   content-only rebuild with compatible running code:

```bash
docker compose -f docker-compose.prod.yml run --rm app python -m msfea_bot.skeleton ingest
docker compose -f docker-compose.prod.yml restart app
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

Point the site's DNS to the existing proxy, which handles TLS. For Caddy running directly
on the Docker host, use `reverse_proxy 127.0.0.1:9000` and keep the default
`APP_BIND_ADDRESS=127.0.0.1`. If Caddy cannot reach the host's loopback, have IT
select a private host address reachable by the proxy. Set `APP_BIND_ADDRESS` to
that address, update the upstream and restrict access to port 9000 to the trusted
proxy. The [nginx template](../deploy/nginx.conf) is also available for
IT-managed TLS.

`CORS_ALLOW_ORIGINS` should contain exact host-page origins. Empty denies
cross-origin browser access while allowing same-origin. The production app trusts
`X-Forwarded-For` for client IP rate limiting. Keep the backend port private and
have the proxy set the forwarded address from the verified client. The example
uses [Caddy's default forwarded-header handling](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#defaults).
Review this setting with IT if the shared proxy already trusts an upstream proxy
or CDN. Keep the 404 block for both `/internal` and `/internal/*` on the public route.

Use one Uvicorn app worker/instance: rate limits, concurrency guard, response cache
and usage counters are process-local. Offline ingestion requires app restart to
clear cached answers; guarded publication invalidates them automatically.

## Admission controls and provider failures

| Layer | Current bounds/defaults |
| --- | --- |
| HTTP/question/history | 10-second body-read deadline; 64 KiB body; 2,000-character question; eight history messages, 1,200 characters each |
| IP | Default 60/minute; 12/5 seconds and 300/hour; persistent 200/UTC day |
| Browser session | 20/minute, 80/hour; persistent 40/chat per rolling 24 hours; IDs are not authentication |
| Expensive concurrency | One/session, four/IP, sixteen/app worker; shared eight paid attempts across app/worker |
| Response reuse | Exact IP/session/department/effective context/index version, five minutes, 256 entries |
| Evidence/output | 24,000 context characters; code output default 1,024 tokens, deployed paid profile 4,096 |
| Staff AI | Default 12 attempts/minute, 400/day/model |
| Student-model previews | Separate 60-call daily admission cap; shares student provider quota |
| All paid workloads | Persistent 100 attempts, 500,000 budgeted tokens and estimated $0.50/UTC day; first reached stops new calls |

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

## Paid-call controls and billing

Every Gemini generation attempt, including retries, staff advice/writing and student
previews, reserves tokens and estimated cost atomically in application PostgreSQL.
The reservation uses a conservative UTF-8 input bound plus schema/framing and the
full server output ceiling. Complete SDK usage settles input and all output,
including reasoning. Failed, unmeasured and interrupted attempts keep their holds.
Therefore an allowance can block earlier than its nominal actual-use capacity.
Neither restart nor a new chat resets global usage. Database failure blocks paid
calls before contacting Gemini. UTC rollover resets daily admission, not the pause.

Configure `LLM_DAILY_REQUEST_LIMIT`, `LLM_DAILY_TOKEN_LIMIT`,
`LLM_DAILY_COST_LIMIT_USD` and `LLM_GLOBAL_CONCURRENCY` in both app/worker environments.
The configured prices are estimates, not the provider invoice; changing models
requires reviewing their input/output prices. `LLM_PRICE_VALID_UNTIL` blocks calls
after expiry until reviewed. Current rates expire on 2026-12-31. A usage-bound
violation automatically pauses new calls. Unmeasured usage remains reserved.

**Paid usage & controls** in the authenticated dashboard shows seven UTC days by
model/workload, input, visible output, reasoning, estimated cost, uncertain holds
and protection events. It refreshes every 30 seconds while visible. Warning banners
flag 80% usage, expired pricing, pauses and provider cooldowns; server warning logs
record near-limit, rejection, circuit and operator events. No email/SMS alert
service is configured. This ledger starts at this release; historical student
analytics remain in Usage overview. Neither view is the prepaid account balance.

The dashboard Pause/Resume control persists in PostgreSQL and affects new attempts
in both services. It cannot reset counters, raise ceilings or clear the cooldown.
Already dispatched calls may finish. `LLM_CALLS_ENABLED=false` is an additional
operator environment override that the dashboard cannot lift. Authentication/quota/
payment failures or five recent provider failures open a two-minute cooldown.
Resuming does not bypass daily limits; saved Studio drafts remain available.

Daily IP/chat counters store keyed hashes, not raw IPs or session IDs. Rotating a
session cannot bypass the IP/global ceiling; IDs are not identity. The browser's
six-question UX cap is separate. Shared campus IPs may need an operator allowance
adjustment. Short-term guards, bounded cache, local acknowledgements/noise replies,
retrieval gates and private staff authentication provide the initial bot protection;
CAPTCHA is not required to contain paid spend. Distributed attacks can still deny
service by exhausting the finite allowance. Monitor events before adding another
anti-bot service. CORS alone cannot stop direct callers.

### Google project safeguards (separate operator step)

In the correct Google AI Studio project, **Spend → Monthly spend cap → Edit** can
set a monthly project cap; $5 is a reasonable starting cap for the current trial
budget. On Billing, check prepaid balance and keep auto-reload disabled unless
additional charges are intentional. Check the project's actual rate quotas too.
The default Tier 1 billing cap is much larger than this trial budget. Google's
project cap/prepay halt can lag by about ten minutes, so retain application limits.
App controls do not cover other services or leaked keys used outside this app.
See [Google billing guidance](https://ai.google.dev/gemini-api/docs/billing/#project-spend-caps)
and [pricing](https://ai.google.dev/gemini-api/docs/pricing).
The agent session had no authenticated Google console; these settings were not
verified or changed during the safeguard rollout.

Migration 0008 adds only usage/control tables. After it is applied, an older image
that recognizes only migrations 0001–0007 will reject the database at startup.
For rollback, build a reviewed revert retaining migration 0008 and the guard, or
restore the pre-release backup with an explicit plan for any subsequent writes.
Never delete usage rows or migration history just to resume spend or start old code.

## n8n import and workflow recovery

The exported workflow is [kb-publication-guard.json](../n8n/workflows/kb-publication-guard.json).
Import deactivates workflows, so the separate publish bootstrap job is required.
After a workflow change, rerun the import/publish jobs and restart n8n:

```bash
docker compose -f docker-compose.prod.yml run --rm n8n-import
docker compose -f docker-compose.prod.yml run --rm n8n-publish
docker compose -f docker-compose.prod.yml restart n8n
```

n8n process health does not prove webhook activation; short startup 404s are retried
by the durable outbox. Workflows accept only existing validation/publication IDs.

Maintain the workflow export in Git. Keep the n8n editor on the private workflow network.

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

Run both scripts from the checkout using the running stack's Compose project.
If the project was given a custom name, set `COMPOSE_PROJECT_NAME` to that name.

```bash
./deploy/backup.sh
./deploy/backup-n8n.sh
```

Use the institution's backup scheduler. For systemd, adapt the account and paths
in the [example service](../deploy/systemd/msfea-chatbot-backup.service) before
installing the timer:

```bash
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
