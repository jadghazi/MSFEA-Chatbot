# Procedural follow-up release — 2026-10-09

Historical deployment receipt. Current behavior is in
[architecture](../architecture.md); paired local evidence is in the
[follow-up review](../../eval/results/procedural_followup_review_20261009.md).

## Release and verification

Application commit: `1e37924be18813f2a0eaa36577ae224ebc6a1215`.
This focused correction retains the activity through generic process-stage
questions, distinguishes recent object references, and uses contextual scoring
for process ellipses while preserving literal numerical/conditional checks.
There is no extra LLM call or persistent memory. No KB, model, threshold, UI,
Studio implementation, workflow or policy change.

Local checks: 644 Python tests passed, one existing optional test skipped;
92 focused conversation tests passed; Ruff and strict mypy passed. All eight
deterministic evidence gates passed. The four completion paraphrases improved
from 1/4 to 4/4 threshold passes. Source review accepted ten actual-history replies
and five controls (13 paid calls, estimated $0.1030815). Final query/prompt parity
was verified without additional provider calls. See the review for retained
intermediate attempts, existing unrelated retrieval misses and calibration limits.

GitHub code-release CI: [run 37967205379](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/37967205379),
**passed**, including the full Python suite, frontend checks and all eight
deterministic evidence gates against the exact deployed commit.

## Oracle

Built natively on Oracle and recreated only app and private curation worker, so
student retrieval and staff preview/validation run the same implementation and
frozen guard cases. Other services remained running and healthy.

- App image: `sha256:199a26fe36211c543f57aca6a7b96996e89d1fd38ae56bc2bef2a16e550a07b0`.
- Worker image: `sha256:1aa41ae971baf6c5ddc869c04a650ed0b0bfa54a625b71d6ccc36019e99f7665`.
- Running conversation source SHA256: `998f3e85e50153e048a1d2e18feedc935c28ddf622b972378c3426e594530080`, matching the local candidate.
- Only `APP_COMMIT` changed in the existing production environment. Student profile
  remains Gemini 3.8 Flash, medium thinking, 4096 output tokens, sampling omitted;
  staff model configuration is preserved.
- Source/index generation remains `sha256:79a543b25a9189af7d2a902fc6b115acd6ee6606796e1ead68036454bac864ea` with 246 chunks. No ingestion or synthetic policy publication.

Public `/health` and `/ready` returned 200. App, worker, database, n8n and n8n
database were healthy. Three public API requests passed actual returned history
to the next request: internship orientation → before accepting an offer → “and
once I finish it?”. Interactions 527–529 returned non-refusal answers, approved
source citations and the required disclaimer. The third answer listed completion
deliverables and the controlling ECE report/presentation deadline of one week
after completion. No feedback or admin content was published during this smoke.

## Rollback and backups

Fresh application and n8n PostgreSQL dumps, the pre-release environment (including
the workflow encryption key) and previous image references are stored under
restricted ignored `backups/procedural-followup-20261009-verified/` on Oracle.
Off-VM copies are in restricted ignored `backups/procedural-followup-20261009/`.
Compressed integrity/completion and matching SHA256s were verified:

- App dump: `375cebc4a8a6689cb6c0bafe6b273533a0a4b92e7fcdc6ada653bb406fe42129`.
- n8n dump: `e04efe975a48d26291591459558a52a287edfd7f767d997dbd7acdc5ad6ab2a7`.

Previous app/worker images have `before-procedural-followup-20261009` rollback tags.
An initial streamed backup command consumed later script input and only created
an application dump; the complete verified attempt used explicit closed stdin
for Docker exec. No serving data was modified by either backup attempt.

Unrelated local CI edits and untracked user material were preserved. The final
documentation receipt does not require another image build or change APP_COMMIT.
