# Development and verification

Read [AGENTS.md](../AGENTS.md) and [architecture](architecture.md), then inspect
the affected code. Preserve unrelated edits. Check `git status`, current commit
and `origin/main` before treating a checkout as current; different local worktrees
can be at different revisions.

## Git and documentation

This solo project normally commits focused, verified changes directly to main and
pushes. A worktree can be used to isolate work from a dirty checkout; do not reset
or overwrite someone else's changes. Use conventional commit prefixes such as
`docs:`, `fix:` and `feat:`. Push only the reviewed task changes.

Update the affected current guide in the same change. Store new measurements in
dated evidence artifacts and add an ADR only for consequential decisions.
Do not append diaries to the archived progress journal or copy provider quotas and
evaluation scores into many guides. Archive reports have historical banners.

## Local environments

For host development use Python 3.12+, install `pip install -e ".[dev,gemini]"`,
provide PostgreSQL/pgvector, and install the local spaCy model. Docker is the
preferred reproducible runtime; the image bakes pinned embeddings and local NER.

The base Compose app/database stack supports chat. Full curation needs the
production overlay's private worker, n8n and validation database; use disposable
configuration and volumes for synthetic Studio tests. Do not repurpose Oracle.

Build the persistent development image after dependency/image changes:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml build dev
```

The dev service bind-mounts the repository, persists tool caches and uses `test-db`
with `msfea_test`. Database fixtures rebuild indexes, so never run them in a
container configured for the demo or production DB.

## Choose checks for the change

Documentation-only: check relative links, deleted/moved references, decision index,
configuration claims and diff scope. No ingestion, live LLM calls or deployment.

For executable changes, use the isolated suite and lint/type checks:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m ruff check src tests eval
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m mypy --strict src eval
node --test tests/widget_submission.test.cjs tests/studio_review.test.cjs tests/studio_preview.test.cjs tests/studio_suggestion.test.cjs
```

For knowledge/chunking/retrieval/prompt/model changes, reproduce the relevant
deterministic gates against an isolated ingested database. The exact CI commands
are in [.github/workflows/ci.yml](../.github/workflows/ci.yml); datasets and live
answer procedures are in [eval/README.md](../eval/README.md). Live provider checks
are opt-in, consume quota and must retain failures/retries in their reports.

For staff changes, also exercise private checks, previews, refresh/resume, failures,
scope/conflict and fresh-review enforcement. Publish synthetic content only on a
disposable stack. Test fault paths when modifying publication or compensation.

## Lessons to retain

- Diagnose evidence coverage before prompts. RRF order is not cosine order;
  the strongest retrieved cosine drives the similarity gate.
- Preserve conditions and all premises. Lower top-k can hide decisive policy;
  larger context alone does not make answers correct.
- Compare actual prompts/configuration and frozen expectations across experiments.
  Avoid trial state leaking between variants.
- More LLM calls or a listed model do not establish quality or usable quota.
- A fact present in the KB must support the same service, scope and claim.
  Student context and private AI suggestions are not authoritative policy.
- Prefer deterministic routing when it matches stronger-model evidence without
  extra latency/quota.

[Historical experiments](archive/engineering-lessons-20260908.md) retain detailed
failed variants and measurements. Read them when testing the same hypothesis,
not as a mandatory startup bundle.
