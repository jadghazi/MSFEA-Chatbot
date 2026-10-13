# Editable linked Studio topics — 2026-10-13

Historical release receipt; current behavior is in [Studio](../studio.md).

Release `3a8eb894c8c80d04d4bab34b4eb59f427aaf457d` makes the linked question/topic
editable on open, refresh, draft resume and working-revision edit. Clarified wording
is retained separately from the original feedback ID/record. Original wording is
shown from the loaded attention item; if unavailable, its feedback ID is shown
instead of representing edited wording as the original. Fresh review remains
required after edits; nonexistent/resolved links and empty linked topics are rejected.

The preceding CI failure was a removed draft-privacy notice checked by
`tests/test_frontend.py`. The notice was restored, preserving the test assertion.
[Full CI passed](https://github.com/jadghazi/MSFEA-Chatbot/actions/runs/38372044304):
Ruff, strict mypy, browser tests, 649 Python tests (three skips) and all retrieval gates.
Local isolated checks: 101 focused Python tests, four final linked-topic checks and
33 dashboard/Studio JavaScript checks. No live LLM calls.

Oracle app/worker were activated only after green CI. Both use the release marker
above and are healthy. Public health/readiness and private worker health returned
200. Live dashboard and version-11 Studio assets exactly match committed Git blobs
(local Windows CRLF is excluded from byte comparison). Original advisor feedback
552 remains unchanged. KB generation remains
`sha256:79a543b25a9189af7d2a902fc6b115acd6ee6606796e1ead68036454bac864ea`.
No ingestion, synthetic production review/publication, RAG or provider-profile change.
Only `APP_COMMIT` changed in Oracle ENV; all other environment text matches backup.

App image: `sha256:a289de8428c41158569e5bd253003d2270114b059a93ede6563668a8e0429178`.
Worker image: `sha256:411a0ca83bcf76c215c8db41c432e0370727045b1f386dc3d0d9d9f746a925bd`.
Previous images have `before-studio-edit-20261013` rollback tags. Fresh complete
application/n8n dumps and environment are restricted in ignored
`backups/studio-edit-20261013/` on Oracle and off VM. Matching SHA256s and gzip/dump
integrity verified: app `4406383ea700e08111991974022baa715fa7b185325a9b85b42bbf2883f09ec0`,
n8n `389e1a628b9ba8931b1aa438623dfe47f550cece7c513345d1276c315d1d0d45`.
Unrelated local CI edits/user files were preserved.
