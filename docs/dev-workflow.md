# Development workflow

How this project is developed day to day. Kept here (not just in one person's
head) because the project is worked across multiple sessions and will be handed
off.

## Git

- **Commit directly to `main` and push.** No feature branches, no PRs — this is
  a solo project and everything is tested before it's pushed, so branches add no
  value. (We used one PR for Phase 0 to establish the habit, then simplified.)
- **One focused commit per completed step**, with a conventional-commit prefix:
  `docs:`, `feat:`, `fix:`, `test:`, `chore:`, `refactor:`. The commit history
  is the record of progress.
- **Test before you push.** Don't push a change that hasn't been sanity-checked
  (imports resolve, `pytest` passes).

## Documentation is part of "done"

Every step keeps the docs current so the next session/agent inherits the state:

- [`definition-of-done.md`](definition-of-done.md) — the Phase 0 acceptance criteria everything is measured against.
- [`decisions/`](decisions/) — an ADR for every costly/architectural decision (esp. all RAG choices: embeddings, vector store, chunking, retrieval, LLM provider). Explain the trade-offs, don't just pick.
- [`backlog.md`](backlog.md) — captured-but-not-yet-built ideas.
- [`progress.md`](progress.md) — dated journal; update it at the end of each working session.

## Build order

Follow the phases in [`../CLAUDE.md`](../CLAUDE.md) §5. Don't jump ahead. Most
phases can be built on placeholder content before the real guidelines arrive.

## Persistent Docker development environment

Use the development image when working on a machine without the full Python 3.12
toolchain. It inherits the production runtime and baked models, and installs the
pinned Ruff, mypy, and pytest versions once instead of reinstalling them for every
disposable test run.

Build it once (and rebuild only after `pyproject.toml` or `Dockerfile` changes):

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml build dev
```

Then run the normal gates against the live working tree:

```bash
# Full test suite (default command)
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev

# Individual gates
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m ruff check src tests eval
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm dev python -m mypy --strict src
```

The repository is bind-mounted at `/workspace`, so source edits are visible
immediately. Tool caches (`.pytest_cache`, `.mypy_cache`, `.ruff_cache`) persist in
the working tree and are already gitignored. A disposable `test-db` pgvector service
is started and health-checked automatically for integration tests. It deliberately
does not use the demo's `db` volume: retrieval tests rebuild the chunks table and must
never replace the KB used by the running chatbot.

The first production build is large because it downloads and bakes the local spaCy
and embedding models. The Dockerfile installs those before copying application source,
so later source-only builds reuse the expensive layers. Measured on the Windows dev
machine after seeding the cache: **about 17 minutes once, then 31.5 seconds unchanged**.
The image also avoids recursively changing ownership of the baked model tree; runtime
content is read-only, so a widget/KB edit no longer creates a multi-gigabyte ownership
layer just to run as the existing non-root user.
