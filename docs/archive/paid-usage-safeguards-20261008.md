# Paid-usage safeguard audit — 2026-10-08

Historical implementation/verification record. Current operations are in
[deployment.md](../deployment.md#paid-call-controls-and-billing). This change
covers abuse/spending controls only; source content, retrieval, generation prompt,
models and staff publication policy were not changed.

## Audit and result

| Requested safeguard | Finding / implementation |
| --- | --- |
| Server-only Gemini key | Already environment-only on app/worker; no frontend key or client model selection |
| IP short-term and daily admission | Retained minute/burst/hour guards; added PostgreSQL 200 requests/UTC day |
| Backend chat cap | Added persistent 40 requests/chat per rolling 24 hours, even across IP changes; new chats still share IP/global caps |
| Global daily requests/tokens/cost | Added shared atomic reservations: 100 attempts, 500,000 tokens, estimated $0.50/UTC day; retries/staff/previews included |
| Provider safeguards | Reviewed Google guidance; console requires sign-in, so Google project cap/auto-reload/actual quotas remain unverified |
| Request/body/history/context | Retained 64 KiB, 2,000 characters, 8 × 1,200 messages, 24,000 context characters; added 10-second body deadline |
| Output cap | Retained student 4,096 / staff 6,144; validates server output range up to 8,192; reasoning counts as paid output |
| Concurrency | Retained 1/session, 4/IP, 16/app; added shared 8 provider reservations across app/worker |
| Timeout/retries | Retained SDK 30s student / 90s staff, SDK retry disabled and one app transient retry; each attempt charged separately |
| Automated abuse | Bounded admission, local greeting/noise path, evidence gate, auth/private staff paths; no speculative CAPTCHA service |
| Input/control validation | Strict student/history shapes; extra fields rejected, protected strict boolean pause API; no client expensive parameters |
| Safe caching | Extended exact IP/session/department/effective-context/index-version response reuse to 5 minutes; 256 entries, no cross-student reuse |
| Monitoring/alerts | Separate Paid usage & controls tab; 7 UTC days by model/workload; input/visible/reasoning/cost/uncertainty; 30-second visible polling; warning banners/logs |
| Kill switch/circuit | Persistent pause + environment override; auth/payment/quota or repeated provider failures cause 120s cooldown; no counter reset |

Conservative input bounds/full output limits are reserved before contacting Gemini.
Unknown/failed/crashed usage keeps its reservation. Complete SDK usage replaces it
with measured input and all output. An unexpected reservation overrun pauses new
calls. A database outage fails closed. The app ledger is an estimate beginning at
this release, not Google's prepaid balance. Distributed clients can still exhaust
an allowance and deny service; the financial exposure is bounded for this app,
not for independent callers using a leaked key or the same Google project.

Google's experimental project monthly cap and prepay halt have approximately
10-minute accounting latency. Recommend a $5 project monthly cap for the trial and
no unintended auto-reload. See [Google billing](https://ai.google.dev/gemini-api/docs/billing/#project-spend-caps)
and [pricing](https://ai.google.dev/gemini-api/docs/pricing). Model prices require
review after 2026-12-31; expiry blocks new calls. No provider settings were claimed
as changed without authenticated console evidence.

## Verification

All Python runs used development Compose's isolated `msfea_test` database; no hosted
provider calls. Retained attempts: initial focused run 84 passed; expanded run 89
passed; full suite 620 passed / 3 skipped with two existing deprecation warnings.
Final changed admission/migration paths were rerun separately: 26 passed, including
7→8 migration preserving existing rows, atomic concurrent ceilings, retry accounting,
reasoning, uncertain holds, database failure, persisted pause, cooldown, rotated
IP/session admission and protected strict control requests.
Frontend checks: 47 passed, including stale/failed-control refresh, authentication,
reasoning display and escaped usage values. Ruff passed; strict mypy passed across
115 source/evaluation files. Local browser fixture verified the paid tab's desktop
layout, warning banner, usage rows and pause-button visibility; it used sample data
and made no paid calls. Small-screen screenshot verification was interrupted by a
lost browser session; responsive wrapping uses the existing dashboard breakpoints.

## Release safety

Migration 0008 is additive; migrations 1–7 were untouched. Retained fresh Oracle
application/n8n dumps, previous environment and images in the ignored restricted
`backups/paid-safeguards-20261008/`, with off-VM copies and verified gzip/SHA256:

- Application: `690265af91ed437d853dce1f43cebd97b29c616677786baf2691e1e9829156ff`
- n8n: `e71642145cb5dfe66025fc1b7af3dbc7e365d967d0b21a0fb2c888151b91b789`

An old version-7 image rejects migration 8 at startup. Roll back with a reviewed
compatible revert retaining the guard/migration, or a deliberate backup restore
accounting for subsequent writes. Do not erase spend records to start an old image.
No KB ingestion or synthetic publication is part of this rollout. Deployment
verification and exact image/commit identities are recorded after rollout below.

## Oracle verification

Initial application release: `3920320d8516df6d471d16a0ee3a5811ce7d2340`.
Both app/worker became healthy; public health/readiness returned 200, unauthenticated
paid monitoring returned 401 and the private health path returned 404. Migration
inventory was 1–8; the source index remained 246 chunks without ingestion.
Authenticated pause blocked the student route and both staff/preview providers in
the separate worker, with zero paid attempts. Resume restored service. One live
IAESTE answer was grounded/cited; its immediate identical repeat reused the response
without another SDK attempt. Ledger: 2,421 input + 86 visible + 489 reasoning =
2,996 tokens, estimated $0.003972, one completed attempt, no uncertain holds.

The smoke receipt's direct JSON printer failed after these assertions because
PostgreSQL SUM(bigint) produced Decimal. The protected API encoded that value as a
string, also risking concatenation when aggregating multiple workloads. A bounded
follow-up converts the aggregate to an integer and normalizes frontend arithmetic;
dedicated Python JSON/API and multi-model frontend regressions cover it. The revised
guard suite passed 20 tests; frontend paid-view suite passed eight (the complete
frontend run previously passed 47). Pricing fixtures are pinned independently of
operator settings/expiry, with expiry tested explicitly. This correction changes
reporting only, not admission, model configuration or knowledge behavior.
