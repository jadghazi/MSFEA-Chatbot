# MSFEA Internship Course Chatbot (RAG)

A Retrieval-Augmented Generation chatbot for the AUB Faculty of Engineering
(MSFEA) Career Development Center. It answers student questions about the CDC's
programs — internship (Approved Experience), CO-OP, IAESTE, full-time job
support, and mentorship — **strictly from the official source documents**, cites
its source, and **refuses + escalates** rather than guessing when the answer
isn't in the material. Goal: cut the volume of repetitive student emails to
professors and the CDC.

> **Status:** functional end-to-end — ingestion, hybrid retrieval, grounded
> generation with citations + refusal, the chat widget, safety/rate-limiting,
> observability, and an admin dashboard with a curation loop. Containerized and
> CI-gated (Phase 10). Pending: the pilot (Phase 11).

## Project docs

- [`CLAUDE.md`](CLAUDE.md) — source of truth for how the project is built.
- [`docs/definition-of-done.md`](docs/definition-of-done.md) — Phase 0 acceptance criteria.
- [`docs/dev-workflow.md`](docs/dev-workflow.md) — how the project is developed (git, docs, phases).
- [`docs/decisions/`](docs/decisions/) — architecture decision records (ADRs).
- [`docs/deployment.md`](docs/deployment.md) — production hardening runbook (HTTPS, CORS, backups, security review).
- [`docs/backlog.md`](docs/backlog.md) — captured-but-not-yet-built ideas.
- [`docs/progress.md`](docs/progress.md) — dated development journal.

## Project layout

```
src/msfea_bot/
  ingestion/   load + clean + chunk + embed source docs -> pgvector
  retrieval/   query pgvector, return top-k chunks
  generation/  build grounded prompt, enforce citation + refusal
  llm/         provider abstraction (swap OpenAI/Azure/Gemini/local in one place)
  api/         FastAPI app the widget calls
  config.py    all env vars, loaded in one place
eval/          golden set + metrics harness (Phase 2)
tests/
docs/
```

## Development setup

Requires Python 3.12+.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 2. Install the package with dev tools (editable)
pip install -e ".[dev]"

# 3. Run the tests
pytest

# 4. Run the API locally
uvicorn msfea_bot.api.app:app --reload
# then open http://127.0.0.1:8000/health
```

Copy [`.env.example`](.env.example) to `.env` and fill in values as phases need
them. Never commit the real `.env`.

## Running with Docker (recommended — runs anywhere)

Everything ships as two containers — the app and PostgreSQL/pgvector — so it runs
identically on any machine or on AUB infrastructure with no code changes. The
embedding and NER models are **baked into the image**, so the container needs no
internet at runtime (firewall-safe).

**Prerequisites:** Docker + Docker Compose.

```bash
# 1. Configure: copy the example env file and fill in the two secrets.
cp .env.example .env
#     LLM_API_KEY : Gemini key from https://aistudio.google.com/apikey
#     ADMIN_TOKEN : any strong random string (protects the admin dashboard)

# 2. Build and start the app + database.
docker compose up -d --build

# 3. Load the knowledge base into the vector store (one time, and after any
#    content change) — rebuilds from kb/normalized/ + curated answers.
docker compose run --rm app python -m msfea_bot.skeleton ingest
```

Then open:

- **Widget (demo page):** http://localhost:8000/widget/demo.html
- **Admin dashboard:** http://localhost:8000/dashboard/ (paste your `ADMIN_TOKEN`)
- **Health check:** http://localhost:8000/health

Everyday commands:

```bash
docker compose logs -f app     # tail the app logs
docker compose down            # stop (KEEPS the database volume)
docker compose down -v         # stop and DELETE the database (fresh start)
```

### Required environment variables

| Variable | Required | What it is |
|---|---|---|
| `LLM_API_KEY` | **yes** | Gemini API key. |
| `ADMIN_TOKEN` | for admin | Shared secret for the admin dashboard; empty = admin disabled. |
| `LLM_PROVIDER` | no | `gemini` (default); swappable behind the provider abstraction. |
| `LLM_MODEL` | no | Default `gemini-flash-lite-latest`. |
| `EMBEDDING_MODEL` | no | Default `BAAI/bge-small-en-v1.5` (baked into the image). |
| `DATABASE_URL` | no | Set automatically by Compose; only needed for host-based dev. |
| `ESCALATION_CONTACT` | no | Email shown when the bot refuses. |
| `CORS_ALLOW_ORIGINS` | no | Comma-separated origins allowed to embed the widget. |

Every variable is documented in [`.env.example`](.env.example).

### Updating the knowledge base

1. Add/edit the official doc under `kb/source/` and its cleaned version under
   `kb/normalized/` (see [`kb/README.md`](kb/README.md)).
2. Re-ingest: `docker compose run --rm app python -m msfea_bot.skeleton ingest`.
3. Add matching questions to `eval/golden_set.jsonl` and re-run the eval.

## Continuous integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push/PR:
ruff (lint), mypy `--strict` (types), pytest (including DB-backed tests via a
Postgres service), and the **retrieval eval with a context-recall floor** so a
retrieval regression fails the build. The answer eval is intentionally not in CI
(it calls the live LLM); run it locally with `python -m eval.answer_eval`.
