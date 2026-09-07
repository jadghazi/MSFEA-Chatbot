# ADR-0019 — Minimal hardening for a small hosted pilot

**Status:** Accepted
**Date:** 2026-09-07
**Decision owner:** Jad Ghazi

## Context

The immediate goal is a small student pilot on a low-cost/free host, not a
multi-instance production platform. An audit found that the RAG and bounded
conversation flow were already suitable, while a few ordinary deployment issues
created unnecessary latency or unsafe defaults: the production overlay exposed the
raw app and database ports, model loading still attempted Hugging Face network
resolution, readiness did not verify the KB, startup loaded models without executing
first inference, each Gemini call created a new client, and interaction-table DDL ran
on every request.

## Decision

Fix those issues without changing the RAG architecture:

- The production Compose overlay exposes only Caddy. FastAPI and PostgreSQL stay on
  the private Compose network.
- Docker forces Hugging Face/Transformers offline mode after baking both local models.
- Startup initializes schemas, executes one embedding and NER inference, and exposes
  `/ready`. Readiness requires a populated index whose recorded embedding fingerprint
  matches this container.
- Interaction schema creation/migration runs once per process, not for every chat.
- Database connection attempts have a five-second bound.
- One Gemini provider/client is reused per app process so its HTTP connection pool can
  be reused.
- Vulnerable packaging tools found by the audit are upgraded in the production image.

Keep the single-process FastAPI + PostgreSQL/pgvector design. Do not add Redis,
queues, a reranker, a vector index, automatic provider failover, answer caching, or a
database pool for this pilot. Local same-network PostgreSQL connection cost should be
remeasured on the eventual host before adding pooling.

## Consequences

- The deployment has safer defaults and can start behind a firewall without reaching
  Hugging Face.
- The first student no longer pays model first-inference setup.
- Docker reports healthy only after the KB is usable and compatible.
- A new/empty deployment remains unready until the one-command ingestion is run; this
  is intentional and visible.
- The image is still large because local PyTorch embeddings and spaCy redaction are
  retained. Removing either would require a measured retrieval or privacy replacement,
  which is outside this focused pilot-hardening step.
