# ADR-0026 — Guarded KB publication with n8n coordination

**Status:** Accepted
**Date:** 2026-09-15
**Decision owner:** Jad Ghazi

**Scope amendment (2026-09-19):** The dashboard is also an intake for genuinely
new CDC knowledge, not only a correction tool for answers already present in the
official files. A focused submitted entry is therefore a first-class, database-backed
knowledge document. It must not claim an unrelated official file as evidence.

## Context

The admin curation loop accepted in ADR-0010 writes an answer and its embeddings
directly into the student-serving index. Editing replaces the same row and chunks
immediately. It has no immutable revision, source-evidence contract, department or
program applicability, validation record, conflict-review decision, or atomic
transaction spanning source state and indexed state. That was sufficient to prove
the feedback loop, but it is not a safe publication process for policy content.

The publication process also needs durable asynchronous coordination. Embedding a
candidate corpus and running the retrieval/regression suites should not occupy a
student API request, and a restart must not lose submitted work. The project owner
selected self-hosted n8n Community Edition for workflow coordination and practical
experience with that tool. This does not change the project's rule that policy and
publication authority stay in the application.

## Options considered

1. **Keep immediate publication and add form validation.** Smallest change, but it
   cannot isolate candidate vectors, preserve history, make publication atomic, or
   prevent an edit from bypassing review.
2. **Build a Python-only workflow orchestrator.** Keeps one runtime, but duplicates
   scheduling, retry, visibility, and recovery behavior that n8n is intended to
   provide, and conflicts with the selected delivery requirement.
3. **Let n8n own validation decisions and publication.** Convenient orchestration,
   but workflow payloads or operator access could become an authorization bypass;
   n8n execution history is also not the application's durable audit record.
4. **Use n8n only as coordinator, with Python/FastAPI owning evidence, results,
   authorization, and publication.** Chosen.

## Decision

Build versioned, source-backed curation with these boundaries:

- There are two explicit source paths. `official_reference` corrects or restates
  information that already exists in a reviewed normalized file and must resolve
  exact file/section/excerpt evidence. `admin_authored` creates one focused CDC
  knowledge document whose immutable submitted revision is the source artifact.
  It requires a document title, self-reported contributor name, responsible CDC
  office/policy owner, applicability, and optional effective date/approval reference.
- Dashboard-created documents live alongside, never overwrite, the official source
  files. They receive stable `KB-<entry>` citation identities and revision metadata,
  enter full validation/conflict review, and are included in reproducible ingestion
  only while their reviewed revision is active.

- A stable curated entry points to an immutable active revision. Creating or editing
  content creates a draft revision and cannot change student retrieval.
- A publishable revision has canonical department and program/topic applicability,
  resolved official evidence or admin-source identity/hash, representative questions, change
  reason, and a recorded source/conflict review for the exact validated fingerprint.
- Every revision receives mandatory human conflict/source review, even when
  deterministic retrieval flags no potential conflict. Similarity surfaces related
  passages; it never certifies that content is conflict-free.
- Python performs deterministic source, privacy, duplicate/candidate, positive
  retrieval, department-isolation, unknown-department, and regression checks against
  an isolated validation database. Required automatic checks use local embeddings
  and PostgreSQL and make no paid API call.
- FastAPI owns admin authorization, validation results, state transitions,
  publication intent, and the final publish decision. n8n requests named,
  idempotent steps and reports execution progress; it cannot provide a trusted
  `passed` result, approve a revision, or set it Active.
- Publication prepares embeddings outside the transaction, then atomically switches
  the active revision, replaces that entry's chunks, increments the KB generation,
  and records the event under a shared database lock and generation check. A bounded
  post-commit smoke failure compensates only if the failed revision is still active.
- Durable application records and an outbox survive n8n or application restarts.
  Student chat never depends on n8n health. Internal workflow routes are denied at
  the public proxy and use a dedicated service credential.
- Legacy active curated answers are preserved as legacy revisions with
  `needs_review` provenance. Missing applicability, approval, authors, or overwritten
  history are not fabricated.
- Contributor and reviewer names entered under the shared admin token are
  self-reported audit labels, not authenticated individual identities or proof of
  two-person approval. Adding accounts/SSO remains outside this feature.
- Self-hosted n8n Community uses its own database/user, persisted encryption key,
  pinned supported image, bounded retention and resources, and no public editor,
  Docker socket, shell nodes, community nodes, or unrelated integrations.

The student-answer configuration is frozen for this feature:
`gemini-flash-lite-latest`, temperature `0`, seed `42`, output ceiling `1024`, local
`BAAI/bge-small-en-v1.5` embeddings at revision
`5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, normal `top_k=7`, adaptive comparison
depth, similarity threshold `0.60`, the current prompt, chunking, ranking, citations,
refusals, follow-up method, and one normal generation call per student turn. A
metadata or policy correction may deliberately change retrieved evidence, but an
unexplained factual, applicability, citation, follow-up, tone, or verbosity regression
blocks release.

## Consequences

- New and edited content takes longer to publish and requires a human decision. That
  cost is intentional because a wrong eligibility or department rule is higher risk
  than a delayed update.
- n8n adds one bounded operational component, database, credential, backup target,
  and recovery procedure. It does not add a student-path dependency or policy engine.
- Candidate evaluation requires PostgreSQL capacity for a separate validation
  database and CPU/RAM for one bounded worker job. Oracle headroom must be verified
  before deployment; insufficient capacity is reported rather than replaced with a
  paid service.
- Existing active content remains available through migration but is not retroactively
  represented as validated. High-risk legacy scope gaps must be reviewed explicitly.
- The pre-change evidence and known failure are frozen in
  `docs/kb-publication-guard-baseline.md` and `eval/results/publication_guard/`.
