# Starter-question refresh — 2026-10-10

Historical deployment receipt; current system guidance is in [architecture](../architecture.md).

Release `3b53e0f1c2e1e80655d8977bbc3ccad030bb25d5` replaces the IAESTE starter
with “Can I combine a company internship with faculty research?” and the CO-OP
GPA starter with “How can the CDC help me prepare for job interviews?”. The
standalone widget URL advances to `pilot-standalone-10` to refresh browser caches.

JavaScript syntax/whitespace checks, 16 existing widget behavior tests and four
existing frontend tests passed. Local Docker was unavailable; the four pure
frontend tests passed on host Python without database access. No LLM calls.

Oracle built the app natively and recreated it. Running app image:
`sha256:109cd1dad6985be42bc1ead7bbeab5f0ae18cfa39f0714460f2b89bb84d85e56`.
Only `APP_COMMIT` changed in the existing environment. The worker was recreated
using its existing image to load the same release marker, keeping Studio validation
fingerprints aligned. Worker health returned 200 with the matching marker.
Retrieval, models, approved content and workflows are unchanged.

Public health/readiness returned 200. Public HTML/widget bytes exactly match the
reviewed files; all four starter strings and version 10 were verified. Widget
SHA256: `8998ac2725a40eccb1f8b114b8fac2396140bb19949d21ad4a6fea0bf24b64f0`.
Index generation remains `sha256:79a543b25a9189af7d2a902fc6b115acd6ee6606796e1ead68036454bac864ea`; no ingestion.

Fresh application/n8n dumps and the pre-release environment/encryption key are in
restricted ignored `backups/starters-20261010/` on Oracle and off VM. Dump integrity
and matching SHA256s were checked: app `15b5f1cf6d0408848ed5c7992c0e0eb4e9a9d9d1f47f68198a5cf6f5160bc577`,
n8n `d6726bd2211e5a2627d8d757698808a5ce3a4d5437bc26b22baec42ff39cec65`.
The previous app image is tagged `before-starters-20261010` for rollback.
Unrelated local CI edits and untracked user files were preserved.
