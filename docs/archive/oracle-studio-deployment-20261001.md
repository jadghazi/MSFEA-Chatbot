> Historical evidence. This file describes the implementation and measurements at the time recorded below; it is not current operating guidance. Start with [the documentation index](../README.md) and [current architecture](../architecture.md). Later decisions may supersede it.

# Oracle self-service Studio deployment verification

2026-10-01, following explicit deployment authorization. Public pilot:
[student assistant](https://msfea-chatbot.duckdns.org/),
[dashboard](https://msfea-chatbot.duckdns.org/dashboard/).

## Release and configuration

- Tested implementation commit: `fb1d83738ef7f51dd9719e680fa9ef1f9d13164a`.
  [CI run 36882309552](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/36882309552)
  completed successfully. Previous Oracle checkout: `5f6062594d957ac3259fd403edc3d10755d76947`.
- Built on Oracle ARM64. App image:
  `sha256:a525ff5d3b93d3c37ddf5e00e1c5d933a9d8826eab4d2fcb0191d010dca091f3`;
  worker image:
  `sha256:b0cf55c64373f6ed6e9a9a186929506f23d1d9363cadad3dbf894644d6246f34`.
- All seven curation migrations are applied. New migrations 0006/0007 and the
  additive `chunks.retrieval_text` column were verified. Normal ingestion rebuilt
  the production KB from source; no local demo database was copied.
- Curation model `gemini-3.1-flash-lite`, 12 admitted attempts/minute, 400/day;
  actual student previews 60/day. Student model stays `gemini-flash-lite-latest`.
  Worker inference threads are one under its existing 0.75 CPU / 2 GiB limit.
- App, worker, both databases, n8n and Caddy are healthy. Public `/health` and
  `/ready` return HTTP 200; all four new Studio assets and the dashboard return
  HTTP 200. Dashboard HTML/JS/CSS hashes match the tested checkout.
  Public `/internal/health` returns 404; only Caddy publishes host ports.
- Snapshot after rollout: root disk 47% used, 24 GiB available. App memory
  approximately 452 MiB, idle worker 47 MiB before model loading, n8n 349 MiB.
  These are operational snapshots, not performance guarantees.

## Production measurements

The existing serving index contains **253 chunks**, zero curated entries, and
the identical pre/post generation:
`sha256:d7b163e7be4bad3da2951a80c3a53e0a9ed11e704a4cb2759277f1b37354a2e4`.
No pending publication/validation jobs existed before rollout or remained afterward.

Eight retrieval-only gates ran in a separate process using the new ARM64 image,
the production database and read-only evaluation files. No fixture ingestion or
Python integration tests ran against the student database.

| Measurement | Oracle result |
|---|---|
| Golden production evidence recall | 122/124 |
| Faculty source-document recall | 198/205 |
| Valid questions above threshold | 165/165 |
| Off-topic questions blocked before generation | 12/20 |
| Synthesis, scope and model-context premises | 75/75 |
| Conversational evidence / independent parity | 21/21; 9/9 |
| Stress evidence / independent parity | 43/43; 19/19 |
| Frozen publication-preservation cases | 9/9 |
| Conflict candidate coverage | 7/7; zero known false-positive fixtures |

These match the measured local baseline. Golden misses `internship-vs-coop`
and `faq-cee-exception`, plus the seven faculty source-document misses, remain;
passing the floors is not a claim of perfect retrieval or comprehensive answer accuracy.

A private review of the existing official 90-credit eligibility rule completed
four audited requests with the configured model and `self-service-studio-v9`.
All four feedback stages were persisted; it classified the rule as duplicate.
Attempting to save the reviewed duplicate returned HTTP 409 with
“This guidance is already covered. Use the existing source instead of a duplicate.”
No draft, curated entry, publication or index change was created. This one review
remains in the audit; the local synthetic acceptance batch was not run on Oracle.

Browser verification on the live ECE student page asked “How do I request an
internship letter?” and then “Where do I get it?” Both returned the official
Microsoft Forms link, one supporting citation and the visible disclaimer.
The full admin publication walkthrough was already tested in the disposable stack;
production smoke checks deliberately did not publish fictional guidance.

## Backups and recovery

- Fresh application and n8n dumps are in
  `/opt/msfea-chatbot/backups/studio-20261001-154834/`, together with the protected
  previous `.env` and checkout commit. Compressed dumps are 599,021 and 60,042 bytes.
- Both dumps restored with `ON_ERROR_STOP` into separate temporary databases:
  application 253 chunks / zero curated entries, n8n one workflow. Both temporary
  databases were removed. Off-VM dump copies were saved to the operator's ignored
  `tmp/oracle-backups/` directory. Encryption-key recovery remains in the protected
  production environment backup; it is not committed or printed.
- The daily systemd backup timer remains active. Prior app and worker images are
  retained under `before-studio-20261001` tags.
- Migration 0007 is additive, but releases whose migration inventory stops before
  0007 reject the new schema. A rollback build must retain the unchanged 0006/0007
  migration files and be verified for schema compatibility; simply selecting the
  earlier image is insufficient. Do not restore an old whole database over newer
  student interactions as routine rollback. Stop the worker during recovery and
  prefer a verified forward fix when possible.

A restrictive backup umask initially also affected newly checked-out source files,
so the first new-image import failed before migration or serving-app restart.
Tracked file permissions were corrected, images rebuilt, and all checks above
completed on the corrected images. Secrets retained their restricted permissions.
