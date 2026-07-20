# MSFEA Internship Course Chatbot (RAG)

A Retrieval-Augmented Generation chatbot for the AUB Faculty of Engineering
(MSFEA) internship course. It answers student questions about internship
guidelines, forms, deadlines, and eligibility **strictly from the official
source documents**, cites its source, and **refuses + escalates** rather than
guessing when the answer isn't in the material. Goal: cut the volume of
repetitive student emails to professors.

> **Status:** early development. Phase 0 (Definition of Done) and Phase 1
> (scaffolding) done. The pipeline modules are labelled skeletons — no RAG logic
> is implemented yet.

## Project docs

- [`CLAUDE.md`](CLAUDE.md) — source of truth for how the project is built.
- [`docs/definition-of-done.md`](docs/definition-of-done.md) — Phase 0 acceptance criteria.
- [`docs/dev-workflow.md`](docs/dev-workflow.md) — how the project is developed (git, docs, phases).
- [`docs/decisions/`](docs/decisions/) — architecture decision records (ADRs).
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

Requires Python 3.11+.

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

## Running with Docker (skeleton — finalized in Phase 10)

```bash
docker compose up --build
```

Brings up the app plus PostgreSQL with the `pgvector` extension.
