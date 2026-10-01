# Oracle answer-suggestion deployment verification

2026-10-01. Public [dashboard](https://msfea-chatbot.duckdns.org/dashboard/).

## Release

- Runtime implementation `d9da055135fbfe368766ab24de5f492b718fe65e`;
  [CI 36914075684](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/36914075684)
  completed successfully, including the full backend suite and all eight gates.
- Oracle ARM64 app image:
  `sha256:0ddd50f7808d595e469a3b9b899557f76b2f62096717b3baf5e792efda0ecf05`.
  Worker image:
  `sha256:9ab6d2ac746ecea2e4553e48dab9fed350a4043d1ba26972bdb29e92de2d8135`.
- World-readable source checkout and non-root import/asset preflight succeeded
  before restarting app/worker. No schema migration or source ingestion was needed;
  migrations 1–7 remain applied. No in-flight staff/publication jobs at restart.
- Six services healthy. Public health/readiness 200, internal health 404, and
  unauthenticated suggestion access 401. Only Caddy publishes host ports.
  The daily `msfea-chatbot-backup.timer` remains active.
- The environment file matches its protected pre-rollout copy. Student model
  `gemini-flash-lite-latest`, staff model `gemini-3.1-flash-lite`, budgets and worker
  limits are unchanged. No extra service, dependency or n8n workflow was introduced.

## Recovery

- Fresh application/n8n dumps and protected environment/commit copies:
  `/opt/msfea-chatbot/backups/answer-suggestion-20261001-185944/`.
  Both dumps passed separate temporary-database restores: 253 chunks, zero curated
  entries and one n8n workflow. Temporary restore databases were removed.
  Dumps were also copied off the VM into ignored local storage; secrets were not
  copied into Git or images.
- Previous compatible schema-7 images remain tagged
  `msfea-chatbot-app:before-answer-suggestion-20261001` and
  `msfea-chatbot-curation-worker:before-answer-suggestion-20261001`.

## Verification

- Production KB generation before/after:
  `sha256:d7b163e7be4bad3da2951a80c3a53e0a9ed11e704a4cb2759277f1b37354a2e4`.
  Still 253 chunks and zero curated entries; no synthetic local data transferred.
- All eight gates passed using the new image against the production index:
  golden 122/124, faculty 198/205, valid threshold 165/165 (off-topic 12/20),
  synthesis 75/75, conversation 21/21, stress 43/43, publication preservation 9/9,
  conflict candidate coverage 7/7. Existing misses are unchanged.
- Official 90-credit suggestion `4567aabb698841c7a2dfdf98e88c9def` completed.
  Attempting to save it directly as an accepted review returned 409. Explicit
  selection queued fresh review `5990d98dce0647168dd6234f7d008992`, which completed
  and identified a duplicate. Six audited staff-model attempts; no KB entry created.
- Live browser intake with the official 1-credit course statement and a question
  also asking eligibility correctly identified the missing requirement. Suggestion
  `4225f5bca61f44ed8739ea5f1430c4b8` completed and added the documented 90-credit
  threshold. The original input remained unchanged; highlights, explanation,
  literal sources and use/edit/discard controls were visually inspected. It was
  left as a private optional suggestion, with no draft or publication.
- Existing ECE letter question and “Where do I get it?” both returned the official
  CDC form URL, citation and disclaimer through the unchanged student pipeline.
- Public bytes of dashboard HTML, Studio CSS/JS, review JS and the new suggestion
  module match the tested checkout. Cache versions are CSS v6, Studio v8,
  review v5 and suggestion v1. Root disk remains 47% used with 24 GiB available.
