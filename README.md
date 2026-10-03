# MSFEA Student Assistant

A source-grounded RAG assistant for the American University of Beirut's Maroun
Semaan Faculty of Engineering and Architecture Career Development Center.
It answers documented internship/Approved Experience, CO-OP, IAESTE, career
support and mentorship questions with sources and an AI-guidance disclaimer.
Unsupported questions are escalated rather than guessed.

The standalone pilot and protected staff dashboard are deployed on Oracle.
The same vanilla-JavaScript widget can embed on an AUB page. Deployment does not
establish wider pilot outcomes or independently calibrated answer accuracy.

## Start here

- Coding agents: read [AGENTS.md](AGENTS.md), then [current architecture](docs/architecture.md).
- All task guides: [documentation index](docs/README.md).
- Knowledge sources and normalization: [KB guide](kb/README.md).
- Evaluation sets, commands and evidence: [evaluation guide](eval/README.md).

## Run locally

Docker/Compose is the simplest app/database setup. Copy `.env.example` to `.env`,
set `LLM_API_KEY` and a strong `ADMIN_TOKEN` for the dashboard. Never commit secrets.

```bash
docker compose up -d --build
docker compose run --rm app python -m msfea_bot.skeleton ingest
```

Open the [assistant](http://localhost:8000/), [dashboard](http://localhost:8000/dashboard/)
or [readiness endpoint](http://localhost:8000/ready). The widget script is
`/widget/widget.js`; `data-layout="standalone"` selects its page layout.

The base Compose stack has only app and database. Full Studio AI review,
private checks and publication require the worker/n8n stack in the
[deployment guide](docs/deployment.md); a basic local chat stack does not provide
those services. For Python development use Python 3.12+, `pip install -e ".[dev,gemini]"`
and the [isolated development workflow](docs/development.md).

## Repository map

| Path | Responsibility |
| --- | --- |
| `kb/`, `src/msfea_bot/ingestion/` | Reviewed source material, chunking and local embeddings |
| `src/msfea_bot/retrieval/` | Department-aware hybrid search and vector storage |
| `src/msfea_bot/generation/`, `src/msfea_bot/llm/` | Conversation routing, grounded answers, provider adapter |
| `src/msfea_bot/api/`, `widget/`, `frontend/`, `dashboard/` | API, dashboard, widget and standalone page |
| `src/msfea_bot/curation/`, `n8n/` | Immutable revisions, private assistance, checks and publication |
| `src/msfea_bot/observability/`, `src/msfea_bot/experience/` | Anonymized interaction review, usage and experience feedback |
| `eval/`, `tests/` | Evaluation datasets, result evidence and regression tests |
| `deploy/`, `docker-compose*.yml` | HTTPS, deployment, backups and isolated development |
| `docs/` | Current task guides; historical evidence is separated in `docs/archive/` |

All runtime settings and service secrets are documented in [.env.example](.env.example).
Read [current architecture](docs/architecture.md) before modifying retrieval,
generation, curation or deployment. The vector index is derived; approved admin
revisions are source records in PostgreSQL and must be backed up.
