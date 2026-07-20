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
