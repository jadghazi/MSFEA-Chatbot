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
> bounded same-chat follow-ups, provider-aware failure handling, observability,
> and an admin dashboard with a curation loop. Containerized and
> CI-gated (Phase 10). Pending: the pilot (Phase 11).

## Project docs

- [`CLAUDE.md`](CLAUDE.md) — source of truth for how the project is built.
- [`docs/definition-of-done.md`](docs/definition-of-done.md) — Phase 0 acceptance criteria.
- [`docs/dev-workflow.md`](docs/dev-workflow.md) — how the project is developed (git, docs, phases).
- [`docs/decisions/`](docs/decisions/) — architecture decision records (ADRs).
- [`docs/deployment.md`](docs/deployment.md) — production hardening runbook (HTTPS, CORS, backups, security review).
- [`docs/pilot-readiness.md`](docs/pilot-readiness.md) — current small-pilot release checklist.
- [`docs/backlog.md`](docs/backlog.md) — captured-but-not-yet-built ideas.
- [`docs/progress.md`](docs/progress.md) — dated development journal.
- [`docs/usage-audit.md`](docs/usage-audit.md) — usage guards, measured savings, limits and remaining risks.

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

- **Standalone pilot assistant:** http://localhost:8000/
- **Future embedded widget:** load `/widget/widget.js` on the host page without
  `data-layout="standalone"`; it retains the compact bottom-right launcher.
- **Admin dashboard:** http://localhost:8000/dashboard/ (paste your `ADMIN_TOKEN`)
- **Liveness check:** http://localhost:8000/health
- **Readiness check:** http://localhost:8000/ready (also verifies the populated KB/model match)

Everyday commands:

```bash
docker compose logs -f app     # tail the app logs
docker compose down            # stop (KEEPS the database volume)
docker compose down -v         # stop and DELETE the database (fresh start)
```

For repeated development checks without reinstalling Ruff, mypy, and pytest each
time, build and use the persistent development image documented in
[`docs/dev-workflow.md`](docs/dev-workflow.md#persistent-docker-development-environment).

### Required environment variables

| Variable | Required | What it is |
|---|---|---|
| `LLM_API_KEY` | **yes** | Gemini API key. |
| `ADMIN_TOKEN` | for admin | Shared secret for the admin dashboard; empty = admin disabled. |
| `LLM_PROVIDER` | no | `gemini` (default); swappable behind the provider abstraction. |
| `LLM_MODEL` | no | Default `gemini-flash-lite-latest`. |
| `EMBEDDING_MODEL` | no | Default `BAAI/bge-small-en-v1.5` (baked into the image). |
| `EMBEDDING_MODEL_REVISION` | no | Exact HF commit of the embedding model, so rebuilds reproduce the same vectors. Changing it needs a full re-ingest. |
| `LLM_TEMPERATURE` | no | Default `0.0`. Decoding is deterministic on purpose (ADR-0012). |
| `LLM_SEED` | no | Default `42`. Temperature alone did not stop the model varying its wording. |
| `LLM_MAX_OUTPUT_TOKENS` | no | Default `1024`; caps runaway generations against the free-tier quota. |
| `DATABASE_URL` | no | Set automatically by Compose; only needed for host-based dev. |
| `ESCALATION_CONTACT` | no | Email shown when the bot refuses. |
| `CORS_ALLOW_ORIGINS` | no | Comma-separated origins allowed to embed the widget. |
| `WARM_MODELS_ON_STARTUP` | no | Default `false`; Compose sets `true` so readiness waits for local embedding/PII models and the first student avoids their cold-start delay. |

Every variable is documented in [`.env.example`](.env.example).

### Same-chat context and free-tier behavior

The widget remembers at most four earlier messages **in memory on the current web
page only**. Closing and reopening the bubble keeps them; refreshing, opening a new
tab, or changing department starts a new chat. History is never stored as a user
profile or server-side session. The API sanitizes/anonymizes every history message,
and only sends bounded history when a question appears to be a follow-up.

Each student turn uses at most **one Gemini generation request**. Follow-up retrieval
is reformulated deterministically, so there is no second LLM call just to rewrite a
question. If Gemini returns a quota/rate-limit or service error, the widget shows an
actionable retry message. These failures are counted separately from genuine
knowledge-base refusals. The Usage tab records aggregate LLM input/output token counts
and average generation latency returned by Gemini (ADR-0018).

Because the Gemini free tier may use submitted content to improve Google's products,
the widget asks students not to enter personal information. The backend still redacts
detected names, emails, student IDs, and phone numbers before the provider and logs;
the notice is defense in depth because name detection cannot be perfect.

Gemini quotas vary by model, project, and account. Check the active RPM/TPM/RPD limits
in Google AI Studio before a pilot; do not size traffic from an old hard-coded number.

### Student controls and anonymous feedback

The standalone page and embedded widget share the same accessible vanilla-JavaScript
client. **New chat** clears visible messages and the bounded in-memory follow-up context
without changing the chosen department. Successful answers can be copied without their
citations or disclaimer, sources expand from a compact disclosure, and temporary failures
offer a student-triggered retry. Messages are never persisted in browser storage.

Students can submit a separate 1–5 experience rating with optional approved reason tags
and a comment of at most 500 characters. The `experience_feedback` table contains only an
ID, timestamp, rating, tags, and comment; it has no interaction, conversation, session,
network, device, or identity fields. The protected dashboard's **Experience feedback** tab
shows totals, average, distribution, tag counts, and recent escaped comments. Thumbs-down
feedback can also carry one optional predefined reason on the existing interaction row.

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

For the September synthesis/follow-up investigation, see
[ADR-0022](docs/decisions/0022-measured-synthesis-and-followups.md), the frozen
[12-case set](eval/synthesis_set.jsonl), and
[reviewed before/after outputs](eval/results/synthesis/reviewed_results.md).
CI also checks that all required synthesis premises survive retrieval and the
similarity gate. Live candidate runs use `python -m eval.synthesis_eval --variant
combined_adaptive --name local_recheck`; they require a populated source index and
provider quota. Run pytest through the dev Compose overlay to isolate its database.
