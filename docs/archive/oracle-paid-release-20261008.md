# Oracle paid student and Studio release — 2026-10-08

**Dated deployment evidence.** This records the October 8 rollout, not a live
monitoring snapshot. Current guidance is in [architecture](../architecture.md)
and [operations](../deployment.md).

The user authorized GitHub publication, Oracle deployment and alignment of the
Oracle environment with the paid Gemini setup. The release deploys the general
student retrieval/context improvements and bounded Studio alignment documented in
the [paid audit](../../eval/results/student_quality_paid_migration_20261008.md) and
[Studio alignment report](../../eval/results/studio_alignment_20261008.md).

## Release identity and configuration

- Initial feature commit: `ea1cd8c7ac5ebbbbf535212a004b1db9c945dc07`.
- Final application commit: `bc6d5a805aa3e4633f458c5a118f85d65fb3efd8`.
- Oracle checkout: `/opt/msfea-chatbot`, native ARM64 Docker build.
- Final app image: `sha256:944b592bef3dae3ceea6f675c114934ac2cbfc6932ebe6d32e5ff406530f92e8`.
- Final worker image: `sha256:10e059878002a3a930a00926acdd949451935a3883d7ea149e4792a377893843`.
- Student: `gemini-3.8-flash`, medium thinking, 4,096 output tokens including
  reasoning, temperature/seed omitted. Actual Studio previews use this profile.
- Staff comparison/writing: `gemini-3.1-flash-lite`, existing separate structured
  response profile, medium thinking and 6,144 output tokens.
- Native Gemini SDK: 2.29.0. The configured student, preview and staff factories
  were checked inside the built image and running app; live calls verified access.

Only the provider/key/profile and application commit fields were updated in
Oracle `.env`. The known-working local paid key was copied through SSH stdin,
without printing it. All other environment settings were preserved; the file
remains owned by `ubuntu` with mode `600`. No secret is in this receipt or Git.
Normal HTTP/session abuse controls and separate staff admission budgets remain.

## Safeguards and index

Before switching, application and n8n PostgreSQL dumps passed `gzip -t` and were
copied off the VM. Previous environment, commit and image identities were saved
under the restricted `backups/paid-release-20261008/` directory; the local copy has
restricted Windows ACLs. Previous app/worker images retain
`:before-paid-20261008` rollback tags. These backups contain secrets and are ignored.

The pre-release inventory had zero active curated revisions and zero queued or
running assistance/workspace jobs. The app and worker stopped briefly while the
new image ingested only reviewed normalized sources and any active approved
revisions. No synthetic test policy, developer database, or direct SQL approval
was published. The index changed from 253 to 246 source chunks. All canonical
chunk IDs, text, sources, sections, metadata, retrieval text and display prefixes
were compared with the image's chunker output and matched exactly.

- KB generation: `sha256:79a543b25a9189af7d2a902fc6b115acd6ee6606796e1ead68036454bac864ea`.
- Embeddings: `BAAI/bge-small-en-v1.5@5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`.
- Four overview chunks and 93 chunks with reviewed companion links.
- No new migration, workflow import/publication or n8n/database restart.

## Verification and retained correction

The [initial feature CI run](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/37758561912)
passed lint, strict typing, JavaScript checks, the full Python suite and the
retrieval gate. Prior isolated Studio and student evaluations remain linked in
the reports above; they are not new production measurements.

The first six-turn public smoke passed the internship overview, duration
follow-up, CO-OP switch, fee follow-up and controlling ECE report rule. Its opening
“So what can you help me with?” unnecessarily refused: the existing deterministic
capability route recognized the same question without the discourse prefix.
The [initial trace](../../eval/results/oracle_paid_release_smoke_initial_20261008.json)
retains that failure.

The bounded correction allows conversational prefixes on the existing capability
intent; it inserts no university facts, topic list or screenshot response.
Eighteen combinations of prefixes and capability intents plus a named-request
guard were added. All 71 conversation tests, focused Ruff checks and strict typing
passed. The code correction rebuilt from cached native layers and recreated the
app/worker; it did not reingest unchanged content. The same six-turn public smoke
was rerun with actual new assistant history, not canned history. Its
[final trace](../../eval/results/oracle_paid_release_smoke_20261008.json) records
the final application commit and responses. All six turns returned healthy,
source-cited answers with the disclaimer and no unnecessary refusal. A manual
source check confirmed the requested intent and controlling rule:

| Turn | Observed result |
| --- | --- |
| Capability opening | CDC services and career readiness overview |
| Internship orientation | Ordinary purpose, requirements and process; no assumed split placement |
| Duration attribute | Eight-week standard minimum and hours, still internship |
| CO-OP topic switch | Optional paid program with at least six months |
| Fee attribute | FEAA 500 first-semester tuition and FEAA 500A without additional tuition; no invented monetary amount |
| ECE report scope | Five pages and 1,500 words minimum, 20-page ceiling and documented exclusions |

The protected Studio options route returned 200 with registry-backed sources and
programs. The private worker health route returned 200 with its dedicated token.
A single live staff comparison of the real ECE final-report rule against 40 source
candidates correctly classified it as a duplicate, selected matching ECE evidence
and passed structured statement verification. The
[staff receipt](../../eval/results/oracle_paid_studio_smoke_20261008.json) retains
the report and usage metadata. It saved no draft or publication. Conflict,
suggestion, preview freshness and publication gate behavior were tested on the
isolated stack before deployment, not by publishing test policies on Oracle.

Public `/health` and `/ready` returned 200. Public `/internal/health` returned 404
and unauthenticated `/admin/api/curation-options` returned 401. App, worker and
both databases were healthy; n8n remained healthy and Caddy served HTTPS. Only
Caddy publishes host ports. The complete release CI for the bounded correction
is [this run](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/37760452401);
at the release observation, lint, JavaScript checks and strict typing had passed;
the full Python suite was still running and the retrieval gate was pending.
The focused 71-test correction receipt above is complete. Consult the linked run
for its subsequent outcome rather than treating this dated status as current.

## Limits

The production smoke is bounded release verification, not a replacement for the
larger constructed audit or independent faculty calibration. Known retrieval
misses and minor answer completeness/clarity limits remain in the dated audit.
No 100% real-world accuracy or institutional policy-owner acceptance is implied.
Package ranges are not fully locked; exact final image identities are recorded
above. Documentation-only follow-up commits do not change the running image or
its `APP_COMMIT`.
