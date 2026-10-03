# AGENTS.md — MSFEA Student Assistant

This is the single source of project rules for coding agents and maintainers.
Read this file first. If a request conflicts with these principles, explain the
conflict and ask before proceeding. Direct user instructions take precedence.

## Start here

Read [current architecture](docs/architecture.md), then only the guide needed for
the task from [docs/README.md](docs/README.md). Check Git status and the code before
assuming a checkout or document describes the latest release. Do not load the
entire archive or decision log as startup context.

Authority order: user instructions → this file → current guides → implementation
and configuration for actual behavior. ADRs explain decisions; dated reports
record past evidence. If code and a current guide disagree, investigate and update
the guide rather than silently choosing an interpretation.

## 1. Product and scope

A source-grounded RAG assistant for AUB MSFEA's Career Development Center (CDC).
It answers Approved Experience/internship, CO-OP, IAESTE, career support, mentorship
and related CDC document questions through a standalone pilot page or a small
embeddable widget. Content can expand through reviewed documents; avoid hard-coded
topic lists. The Oracle standalone pilot and protected staff dashboard are deployed.
AUB-page integration, wider pilot outcomes and independent human answer calibration
are separate acceptance work, not implied by deployment.

Student-facing answers must be grounded in retrieved approved content, cite their
sources and show an AI-generated/verify-with-official-sources disclaimer. When
evidence is insufficient, refuse gracefully and route to a human contact. Never
invent eligibility, deadlines, links, exceptions or policy rationales.

The existing staff dashboard, feedback review and Knowledge Studio support KB
maintenance. Do not expand into student accounts, career portals or per-program
business workflows without an explicit scope decision.

## 2. Engineering discipline

- **Eval-driven:** separate retrieval coverage from answer correctness. Measure
  changes to content, chunking, retrieval, prompts and models against relevant
  frozen sets. A passing citation check is not proof of grounding.
- **Retrieval first:** inspect whether the correct evidence reached the model
  before tuning generation. Preserve both sides of conditional rules.
- **Reproducible knowledge:** normalized files plus active, approved immutable
  admin revisions are canonical ingestion inputs. Never hand-edit vectors.
  Normalization is a reviewed step, not automatically repeated by ingestion.
- **Smallest working slice:** prove an end-to-end path before expanding it.
  Avoid speculative services, dependencies, abstractions and optimization.
- **Explain real trade-offs:** state options, evidence and limitations. Never
  call something improved without a metric; retain failed and retried attempts.
- **No invented facts or filler:** label genuine placeholders explicitly.
  Ask when a material source or architecture assumption cannot be resolved.
- **Keep it legible:** type-hinted Python, focused modules, standard approaches,
  focused commits and enough documentation for handover.

## 3. Stack and boundaries

- Python/FastAPI; PostgreSQL 16 with pgvector for application data and vectors.
- Local pinned BGE-small-en-v1.5 embeddings and local spaCy name redaction.
  No hosted vector database or paid embeddings without discussing the deviation.
- All LLM calls pass through `src/msfea_bot/llm/`. Gemini is the only implemented
  production provider; another vendor requires an adapter and verification.
  Student and staff models are configured separately.
- Plain HTML/CSS/vanilla JavaScript widget/dashboard; no React. One script embeds
  the widget. The standalone frontend reuses it.
- Docker/Compose, Caddy HTTPS, environment-only secrets; configuration in
  `src/msfea_bot/config.py` and documented in `.env.example`.
- The existing private Python curation worker and self-hosted n8n coordinate
  durable checks/publication. n8n does not answer student questions, decide policy
  or authorize writes. Its separate PostgreSQL 17 database is workflow storage.

## 4. Evaluation and verification

Use [eval/README.md](eval/README.md) for datasets, commands and limitations.
The constructed golden set and faculty-approved set serve different purposes;
do not change expected answers merely to make a candidate pass.

CI runs lint/type checks, Python/widget tests and deterministic evidence gates.
Live answer evaluation is opt-in because it consumes provider quota. Human
calibration and source review remain required for trusted accuracy claims.

Run tests on an isolated database through the development Compose service.
Tests and evals that rebuild indexes must never target the demo or Oracle database.
Choose checks proportionate to the change: documentation-only work needs link,
reference and consistency verification, not live LLM calls or KB publication.

## 5. Current work order

The intake → evaluation → retrieval → grounded generation → UI → safety →
observability → deployment foundation exists. Do not restart the project as a
walking-skeleton exercise. Work now follows diagnosis → a measured small change →
appropriate regression checks → reviewed release → updated current guidance.

For knowledge changes: review authority/scope → update source and normalized
content, or use guarded Studio → verify retrieval and answers → publish/deploy
only with authorization. See [KB guide](kb/README.md).

For student-flow failures: inspect retrieved passages and conversation routing,
then generation. For staff-flow failures: distinguish AI advice, deterministic
checks, actual student-model previews and human approval; they are separate gates.
Archived references to Phase 5.3–5.12 refer to the original build sequence, not
missing features or a new implementation mandate.

## 6. Repository and documentation conventions

- Preserve unrelated user changes and identify the latest working checkout.
- Keep ingestion, retrieval, generation, API and curation modules separated.
- Never commit real keys, tokens, `.env`, student-identifying data or secret output.
- Strip student names/emails/IDs before logging/provider calls; redaction is
  best effort, so do not claim formal anonymization guarantees.
- Keep current behavior in the task guides, code defaults in configuration and
  dated measurements in result artifacts. Avoid duplicating volatile numbers.
- Update affected current guides in the same change. Record an ADR only for a
  consequential decision; keep accepted decision bodies historical.
- Archive dated investigations with a historical banner. Do not append a new
  session diary to the archived progress journal. Use commits and dated evidence.
- [Development workflow](docs/development.md) defines Git practice and checks.

## 7. Publication and privacy safeguards

Private AI writing suggestions may show advisory factual/source warnings for staff
review, including during conflicts. This is not student-answer approval. Using or
editing a suggestion requires fresh review; deterministic validation, source
confirmation and named human publication approval remain mandatory. Do not weaken
these gates to make a draft pass.

Never publish synthetic test policies on Oracle. Never mark checks passed or
revisions active directly in SQL. No automatic retraining from feedback.
Do not weaken department isolation, refusal, citations, privacy or provenance.
