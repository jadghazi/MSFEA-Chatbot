# Production deployment & hardening

How to take the containerized bot (see the README for the basic run) from "works
on my machine" to "safe to expose to students." Everything here is engineering
that's already done or templated; the only IT-supplied inputs are a handful of
**values** (a domain, the page origin, a cert or auto-cert), noted below.

---

## What IT / the department needs to provide

| Thing | Used for | Where it goes |
|---|---|---|
| A **domain** (e.g. `chatbot.aub.edu.lb`) + DNS pointing at the server | Public HTTPS URL | `DOMAIN` env (Caddy) or `server_name` (nginx) |
| The **page origin** that embeds the widget (e.g. `https://www.aub.edu.lb`) | CORS allow-list | `CORS_ALLOW_ORIGINS` in `.env` |
| A **TLS certificate** | HTTPS | *Automatic* with Caddy; or IT's cert with nginx |
| The **LLM provider/quota** decision | Real traffic (the free tier is ~20 req/day) | `LLM_PROVIDER` / `LLM_API_KEY` / `LLM_MODEL` |
| Backup storage location | Off-box backups | `BACKUP_DIR` for `deploy/backup.sh` |

---

## 1. HTTPS in front of the app (required for a public page)

A browser on an `https://` AUB page **cannot** call an `http://` API — so the API
must be served over HTTPS. The app itself speaks plain HTTP; a reverse proxy
terminates TLS in front of it. Two options:

### Option A — Caddy (recommended, automatic HTTPS)
Turnkey: Caddy obtains and renews the certificate from Let's Encrypt automatically.

```bash
DOMAIN=chatbot.aub.edu.lb docker compose \
    -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```
Config: [`deploy/Caddyfile`](../deploy/Caddyfile). Requires DNS for `DOMAIN` on this
server and ports 80 + 443 open.

### Option B — IT-managed nginx
If IT already runs nginx and provides certs, use
[`deploy/nginx.conf`](../deploy/nginx.conf) as a template (fill in `server_name`
and the cert paths). It proxies to the app on `127.0.0.1:8000`.

---

## 2. Proxy ↔ rate-limit setting (important, easy to get wrong)

The per-client rate limiter keys on the client's IP. Behind a proxy, **every**
request arrives from the *proxy's* IP unless you trust the forwarded header:

- **Behind a proxy** (Options A or B): set **`TRUST_PROXY_HEADERS=true`** so the
  app reads the real client IP from `X-Forwarded-For`. (The Caddy overlay sets this
  for you.) Without it, all students share one rate-limit bucket and throttle each
  other.
- **NOT behind a proxy:** keep it **`false`**. If it were `true` with no proxy,
  clients could spoof `X-Forwarded-For` to bypass the limit.

Rule of thumb: `TRUST_PROXY_HEADERS` should be `true` **iff** there's a trusted
proxy in front.

---

## 3. Lock down CORS

`CORS_ALLOW_ORIGINS` defaults to **empty = deny all cross-origin** (same-origin
still works). In production set it to the exact page origin(s) that embed the
widget:

```
CORS_ALLOW_ORIGINS=https://www.aub.edu.lb
```
Never use `*` in production — it lets any website call your API and burn your LLM
quota.

---

## 4. Secrets

- All secrets come from the environment (`.env`), never baked into the image.
  `.env` is gitignored; keep it off version control and off shared drives.
- **Rotate the admin token**: change `ADMIN_TOKEN` in `.env` and
  `docker compose up -d` to apply. Generate one with
  `python -c "import secrets; print(secrets.token_urlsafe(24))"`.
- In production, don't publish the database port (drop `5432:5432` from
  `docker-compose.yml`); the app reaches it over the internal network.

---

## 5. Backups

The vector index is rebuildable from source, but **admin-curated answers and the
interaction logs are not** — back up the database.

```bash
./deploy/backup.sh          # -> ./backups/msfea-YYYYmmdd-HHMMSS.sql.gz
./deploy/restore.sh ./backups/msfea-20260727-020000.sql.gz
```
Schedule `backup.sh` (e.g. daily cron) and store copies off the box (`BACKUP_DIR`).

---

## 6. Security review (2026-07-27)

A review of the public-endpoint threat model. **No critical issues.**

**Verified safe:**
- **SQL injection** — all queries parameterized; no user input in any f-string SQL.
- **XSS** — the widget renders user text and answers via `textContent` and escapes
  citations; the dashboard escapes all output.
- **PII** — questions are anonymized (emails, IDs, names) *before* the LLM call and
  *before* logging; fail-safe.
- **Prompt injection** — the system prompt treats the question as untrusted and is
  scope-locked to CDC topics.
- **Errors** — `/chat` degrades gracefully; no stack traces leak to users.
- **Dependencies** — `pip-audit`: 0 known vulnerabilities.

**Fixed in this pass:**
- **CORS** was open (`*`) → now strict-by-default (deny cross-origin unless
  configured).
- **Rate-limiter memory** could grow unbounded under many distinct IPs → now sweeps
  stale keys.

**Accepted / documented (no code change):**
- Admin endpoints aren't rate-limited, but the 192-bit random `ADMIN_TOKEN` +
  constant-time comparison make brute force infeasible. Front with AUB SSO when
  available (ADR-0010).
- In-memory rate limiter is per-process — fine for a single instance / pilot; a
  multi-instance deployment needs a shared store (Redis) (ADR-0008).

Re-run the dependency scan periodically: `pip-audit`.

---

## Pre-launch checklist

- [ ] Real LLM provider/quota set (not the ~20/day free tier).
- [ ] `CORS_ALLOW_ORIGINS` = the real page origin (not `*`, not empty).
- [ ] HTTPS working (Caddy or nginx); `TRUST_PROXY_HEADERS=true` behind the proxy.
- [ ] `ADMIN_TOKEN` set to a fresh strong value.
- [ ] Database port not publicly published.
- [ ] Ingestion run once; `/health` green.
- [ ] Backups scheduled and a restore tested.
- [ ] Real student questions in the golden set; `eval` passing.
