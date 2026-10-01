# MSFEA Student Assistant

A source-grounded RAG assistant for the American University of Beirut's Maroun
Semaan Faculty of Engineering and Architecture (MSFEA) Career Development Center
(CDC). It helps students find documented guidance on Approved Experience
internships, CO-OP, IAESTE, career and full-time job support, mentorship, and
Career+. Department-specific rules are scoped to the selected department.

The assistant cites supporting documents and declines to invent an answer when
the available evidence is insufficient. It is informational guidance, not a
substitute for a decision by the CDC or a course coordinator.

**Project state (September 2026):** the standalone pilot is deployed on Oracle
Cloud with HTTPS; the same vanilla-JavaScript client can also run as an embedded
widget. The application, source-backed knowledge base, guarded admin publication
flow, and automated retrieval checks are implemented. Wider pilot outcomes and
independent human calibration of answer accuracy remain open work.

## How it works

1. Reviewed source documents in `kb/source/` are normalized into
   `kb/normalized/`. Ingestion rebuilds the PostgreSQL/pgvector index from
   those files and active, reviewed admin-authored knowledge revisions.
2. Department-aware hybrid retrieval combines semantic and keyword matches.
   A calibrated similarity gate skips generation when no useful evidence is found.
3. The Gemini provider receives bounded retrieved context and produces a cited
   answer or a refusal with an escalation contact. Local embedding and
   personal-information redaction models run inside the app.
4. A short, temporary conversation history supports follow-ups. Explicit new
   subjects take precedence over old context; ambiguous turns may search both
   the student's literal question and a compact contextual query. Query resolution
   is deterministic, so there is no second LLM rewrite call. The client limits
   each chat to six completed questions and offers a fresh chat afterward.

The provider interface is isolated under `src/msfea_bot/llm/`; **Gemini is the
only implemented provider at present**. The model is configurable through
`LLM_MODEL`. Transient provider errors are handled separately from knowledge
refusals, and the UI gives students a retry path. Answers show sources and an
AI-generated guidance disclaimer. Students are asked not to submit personal
details; the backend also applies best-effort redaction before provider calls
and logging.

## Repository map

| Path | Purpose |
| --- | --- |
| `src/msfea_bot/ingestion/`, `kb/` | Reviewed source material, normalization, and reproducible indexing |
| `src/msfea_bot/retrieval/` | Department-scoped hybrid search and evidence selection |
| `src/msfea_bot/generation/`, `src/msfea_bot/llm/` | Conversational routing, grounded answers, and provider adapter |
| `src/msfea_bot/api/`, `widget/`, `frontend/` | FastAPI service, embeddable widget, and standalone pilot page |
| `src/msfea_bot/curation/`, `n8n/` | Versioned admin knowledge publication and private workflow coordination |
| `eval/`, `tests/` | Golden sets, retrieval/answer reviews, and regression tests |
| `deploy/`, `docker-compose*.yml` | HTTPS, private services, backups, and deployment configuration |

## Run locally

Docker with Compose is the simplest way to run the app and pgvector database.
Copy `.env.example` to `.env`, then set at least `LLM_API_KEY` for answers
and a strong `ADMIN_TOKEN` if using the dashboard. Never commit `.env`.

```bash
docker compose up -d --build
docker compose run --rm app python -m msfea_bot.skeleton ingest
```

Open the [standalone assistant](http://localhost:8000/), the
[admin dashboard](http://localhost:8000/dashboard/), or the
[readiness endpoint](http://localhost:8000/ready). The reusable widget is
`/widget/widget.js`; without `data-layout="standalone"` it presents the
compact launcher. The local Compose file contains only the app and database.

For Python development, use Python 3.12+, `pip install -e ".[dev,gemini]"`,
and `pytest`. The full development environment and database isolation are
documented in [the development workflow](docs/dev-workflow.md).

For a public installation, use the production Compose overlay and
[deployment runbook](docs/deployment.md). It adds Caddy for HTTPS, a private
curation worker, n8n and its database, and a separate validation database.
Those services require additional independent secrets and a public `DOMAIN`,
all listed in [`.env.example`](.env.example). Do not use the local two-container
setup as the public deployment topology.

## Updating knowledge

Keep original official files in `kb/source/`, review their normalized Markdown
in `kb/normalized/`, and re-run ingestion after a file-backed content change.
Add or update source-grounded evaluation cases at the same time. The
[KB guide](kb/README.md) records provenance, normalization, and department
scope.

The protected dashboard also accepts focused corrections and genuinely new CDC
knowledge. Drafts are immutable revisions: validation runs against an isolated
index, a human records the source/conflict decision, and publication activates
the reviewed revision atomically. n8n coordinates these steps but does not
decide policy or bypass application checks. See
[ADR-0026](docs/decisions/0026-guarded-kb-publication.md).

Knowledge Studio provides the same guided composer from **Add knowledge** and
**Needs attention**. Staff paste one approved guideline and select its scope.
The private worker proposes a title and student questions, compares exact claims,
and asks for missing details. The factual guidance stays verbatim. Saving starts
the existing private validation workflow; a recorded human decision is still
required before publication. The original unanswered question is also retrieval-tested.

Set `CURATION_LLM_MODEL` separately from `LLM_MODEL` (default:
`gemini-3.6-flash`). Run the full guarded Compose stack for AI assistance; the
manual editor remains available. Staff requests use JSON-schema output, verified
quote/source references, durable review records, and a conservative allowance of
four attempts/minute and eighteen/day/model, including one transient retry.
`CURATION_LLM_DAILY_CALL_LIMIT` must fit the selected model's actual AI Studio quota.
These limits are conservative pilot admission controls, not a promise of provider
availability. See [the staff guide](docs/guided-studio-guide.md) and
[ADR-0028](docs/decisions/0028-guided-knowledge-studio.md).
See [the measured implementation review](docs/guided-studio-quality-report.md)
for the live model limitations and publication tests.

## Evaluation and limits

The versioned evaluation material has two complementary parts:

- `eval/golden_set.jsonl` contains 130 cases, mostly constructed edge and
  refusal cases, including conversation transitions.
- `eval/faculty_questions_golden.jsonl` contains 177 anonymized
  faculty-approved question/answer pairs expanded to 205 department-scoped
  cases. The extra departmental variants are **not** additional student
  submissions.

CI runs linting, strict type checks, Python and widget tests, ingestion,
retrieval/context gates, threshold and synthesis checks, conversation regression
sets, and publication/conflict gates. It does **not** run the full live-answer
set on every push because that consumes provider quota. Retrieval hit rate and
answer correctness are reported separately; a relevant document in the top
results does not guarantee a correct answer. Model-judge answer ratings are
provisional until independently calibrated by humans. Methods, current result
artifacts, and limitations are in the [evaluation guide](eval/README.md);
the latest conversation-routing decision is [ADR-0027](docs/decisions/0027-conversational-rewrite-evaluation.md).

The pilot's free-tier Gemini limits and occasional service outages constrain
throughput. Check the limits of the configured model before increasing traffic.
The six-question client limit bounds context length; it is not a server-side
account or conversation store.

## Further documentation

- [Project principles and scope](CLAUDE.md)
- [Definition of done](docs/definition-of-done.md)
- [Architecture decisions](docs/decisions/)
- [Deployment and operations](docs/deployment.md)
- [Development workflow](docs/dev-workflow.md)
- [Pilot-readiness snapshot](docs/pilot-readiness.md) (historical prelaunch measurements)
- [Progress journal](docs/progress.md)
