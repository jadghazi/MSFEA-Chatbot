# ADR-0010 — Admin dashboard + curation feedback loop

**Status:** Accepted
**Date:** 2026-07-23
**Decision owner:** Jad Ghazi

## Context

Phase 9 logs unanswered questions and (now) thumbs-down ratings, but nothing
acts on them. We want authorized CDC staff to review those cases and answer them,
turning real failures into KB content so the bot improves. (Backlog B-3 / B-3a.)

## Decisions

**Storage — Postgres `curated_answers` table as an ingestion source** (not a file
the app writes to). In a live deployment the container filesystem is ephemeral, so
a file-append would be lost on redeploy; Postgres has a persistent volume, is
transactional, and is safe under concurrent edits. The vector store is rebuilt
from *normalized markdown files + the curated table*; publishing an answer does an
incremental embed+upsert (`retrieval.store.upsert_chunks`) so no full rebuild is
needed. Each curated answer is one chunk (`source_doc = "admin-curated"`).

**Grounding integrity** — the answer is written by an **authorized admin**, so it
*is* official content. This is content authoring, not model training; the bot
stays grounded. (Contrast: we still never auto-inject model-generated answers.)

**Admin auth** — a single shared `ADMIN_TOKEN` (constant-time compared), required
on `/admin/*` endpoints; empty token = admin disabled. This is operational access
control, not a user-account system (§7). Production should front it with AUB SSO;
the token is a pragmatic v1.

**Ratings** — `interactions.rating` (+1/-1); the widget shows 👍/👎; `POST /rate`
records it; `/chat` returns the `interaction_id` to tie them together.

**Feedback view** — `/admin/api/feedback` returns interactions that are refused OR
thumbs-down, including the **retrieved chunks** so the admin can diagnose
retrieval-vs-content gaps (B-3a). `/admin/api/stats` gives aggregate usage.

## Consequences

- Verified end-to-end (live HTTP): ask → refuse → admin curates → re-ask →
  answered from the curated content; ratings, auth, and dashboard all work.
- Provenance kept (`source: admin-curated`, author). A full `ingest` includes
  curated answers, so rebuilds never drop them.
- **Follow-ups (not built):** editing/retiring a curated answer via the UI
  (`deactivate` exists in the store but isn't exposed); auto-adding a curated Q&A
  to the golden set for regression coverage; replacing the shared token with SSO.
- Dashboard shows only anonymized questions (names/emails/IDs already redacted at
  ingest, ADR-0007/0009) — no student-identifying data is exposed.
