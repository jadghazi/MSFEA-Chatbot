# Current architecture and project state

Reviewed 2026-10-03 against code through `2601082`. This is the current system map.
Defaults below describe code/example configuration; a deployed `.env` can override
them. Deployment observations are dated evidence, not a live monitoring snapshot.

## State and limits

The source-backed CDC knowledge base, standalone student pilot, embeddable widget,
department scoping, bounded follow-ups, feedback/usage dashboard and guarded
Knowledge Studio are implemented. Oracle deployment was verified through the
2026-10-02 suggestion update. The [October rollout record](archive/oracle-studio-deployment-20261001.md)
documents the serving topology and unchanged 253-chunk source index at that rollout.
The latest private-draft behavior is recorded in [ADR-0031](decisions/0031-advisory-ai-drafts.md).

Wider pilot/email-deflection outcomes, AUB-page integration, institutional ownership
and independent human calibration remain open. Deterministic retrieval gates have
known misses; see [evaluation](../eval/README.md) and [backlog](backlog.md).
Do not infer 100% policy correctness from passing checks.

## Sources and ingestion

Official originals live in `kb/source/`. Reviewed Markdown in `kb/normalized/` is
the file-backed ingestion input; extracting and reviewing originals is a separate
step. Approved staff entries are immutable PostgreSQL revisions, not edits to an
official document. A rebuild reads normalized files plus each active revision.

`ingestion/chunking.py` splits by section and line-aware windows (defaults 500
characters, 150 overlap), keeps tables atomic, inherits department scope in nested
sections and excludes editorial provenance sections. Oversized lines/tables can
exceed the normal window size. `ingestion/embeddings.py` uses pinned local
`BAAI/bge-small-en-v1.5` weights with a fingerprint.

`retrieval/store.py` owns PostgreSQL chunks, canonical text, optional retrieval text,
source/section metadata and generation/model identity. Embeddings are computed
before atomic replacement. Ingestion, publication and retirement share a write
lock; a stale rebuild aborts if the active generation changes. Never hand-edit vectors.

Canonical text grounds answers and supplies keyword search. A focused curated entry
can have a separate, reviewed representation for embeddings after measured search
repair. This text never becomes factual answer evidence. See [curation](curation.md).

## Student request path

1. The shared vanilla-JavaScript widget sends the question, selected department,
   ephemeral session ID and bounded page history. `frontend/` hosts the standalone
   page; `dashboard/` serves the protected staff dashboard.
2. `api/app.py` applies input/body/rate/concurrency guards and best-effort local
   redaction. Whole-message greetings/acknowledgements/noise can return locally.
   Exact effective requests in a session can replay a 30-second response.
3. `generation/conversation.py` deterministically resolves follow-ups. Explicit
   new subjects take precedence; ambiguous references can search literal and
   contextual queries. Assistant history is never policy authority. No second
   LLM query-rewrite call is deployed (ADR-0027).
4. `retrieval/store.py` fuses vector and PostgreSQL full-text rankings with RRF.
   Normal depth is 7; explicit comparisons use at least 12. Selected departments
   exclude other departments' rules and can reserve relevant own-department evidence.
   With unknown department, applicable department labels remain explicit.
5. `generation/answer.py` builds bounded canonical evidence. The strongest retrieved
   cosine must clear 0.60; otherwise the request escalates without generation.
   A 24,000-character context ceiling asks for a narrower question rather than
   silently discarding policy conditions.
6. The provider in `llm/` produces the grounded answer/refusal. Citation labels are
   checked against retrieved sources. Responses display citations and disclaimer.
   Provider outages/quota errors are distinguished from knowledge refusals and give
   a retry path.
7. `observability/` stores anonymized interactions/retrieval labels, feedback and
   provider usage/latency. Provider failures do not become unanswered-content work.
   `experience/` separately stores anonymous experience feedback.

The browser allows six completed questions per chat. The API history limit is eight
messages of at most 1,200 characters each; questions are at most 2,000 characters.
There is no persistent student account or server conversation store.

## Staff maintenance path

Both Needs attention and Add knowledge enter the same Describe → Resolve → Preview
→ Publish workspace. The private worker retrieves related evidence, compares literal
claims, generates focused test questions and independently verifies review coverage.
Routine preparation uses four staff-model calls; clarification can stop earlier.
Structured output/quote checks and durable stage records make the advice inspectable.

Optional answer writing normally uses two staff calls. It remains available during
policy conflicts and shows the proposed answer with highlighted changes, supporting
facts, missing details and advisory warnings. Factual/source concerns no longer hide
a usable private draft. Malformed output, privacy and stale-context failures can
still prevent a draft. Accepting/editing requires fresh main review.

Source confirmation creates an immutable draft. Seven deterministic checks run on
a separate validation database. A measured search failure can trigger one bounded
search-only repair without changing facts, scope or original tests. Actual student
model previews are separate LLM calls. Named human approval and valid checks are
required before atomic publication; linked feedback resolves after serving smoke.
[Studio guide](studio.md) explains staff actions; [curation contract](curation.md)
describes exact gates and recovery.

## Providers, budgets and topology

Student `LLM_MODEL` and staff `CURATION_LLM_MODEL` are independent configuration.
The example student model is `gemini-flash-lite-latest`; staff defaults to
`gemini-3.1-flash-lite`. Gemini is the only implemented production adapter.
Admission defaults are 400 staff attempts/day/model, 12/minute, and 60 student-model
preview calls/day. These are app budgets, not provider guarantees or entry counts.
The local 500/day demo override does not change the production default.
Retries also use quota; verify the project's actual allowance before changes.

Production runs app, application PostgreSQL, private worker, self-hosted n8n,
n8n PostgreSQL and Caddy. Validation uses a separate database on the application
PostgreSQL server, not a seventh permanent container. Bootstrap jobs initialize
validation and import/publish the Git workflow, then exit. Student chat is independent
of n8n; n8n sequences checks/publication IDs and cannot approve content.

Use one application worker/instance: rate limiting, concurrency, response cache and
usage counters are process-local. API admission limits and backup/recovery procedures
are in [operations](deployment.md). Persistent application records are authoritative;
n8n execution history and process counters are not audit or billing ledgers.

## Verification boundaries

CI measures retrieval/evidence preservation, thresholds, conversation routing and
publication/conflict coverage without live provider calls. Live answer correctness,
staff suggestions and previews require separate source-based review. Independent
human calibration is still pending. Best-effort redaction and natural-language AI
checks are safeguards, not guarantees. See [evaluation methods](../eval/README.md).
