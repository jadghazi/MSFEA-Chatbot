# Progress journal

Dated log of what was built each working session and why. This is the
monitoring trail for the capstone. Newest entries at the top. Keep entries
short: what changed, why, what's next, what's blocked.

---

## 2026-07-20 — Evaluation methodology + dashboard decision (docs only)

**Decided (ADR-0002).** Answer grading uses a **layered hybrid**, matching
production RAG practice — all four layers, since this is built to deploy:
1. Deterministic checks (refusal / citation / disclaimer) — free, no LLM.
2. Decomposed LLM-as-judge (faithfulness/groundedness + relevance).
3. Human calibration on a small sample to trust the judge.
4. Production feedback (👍/👎, escalation/deflection rate, unanswered-questions).
Layers 1–3 = Phase 2 (offline harness); Layer 4 = Phase 9 (online).

**Clarified.** 👍/👎 feedback does NOT auto-retrain the bot — it signals a human
to fix content/retrieval/prompt (human-in-the-loop). Documented in ADR-0002 and
DoD C4.

**New backlog item B-3 (+ B-3a).** Admin/usage analytics dashboard (department
asked if usage can be seen). End-stage, sits on top of Phase 9 logging, aggregate
metrics only, no student-identifying data (privacy per §7). B-3a: a feedback
review/audit queue where 👎 answers surface with their retrieved chunks so an
admin can diagnose retrieval-vs-generation failure and record what should have
been answered (fix = update source docs, not hard-code; verified corrections seed
the golden set).

**Docs touched:** ADR-0002 (new), decisions/README index, backlog B-3,
definition-of-done (Tier B note + C4), this journal. No code — Phase 2 not built
yet.

---

## 2026-07-20 — Phase 1: scaffolding

**Done.** Built the repo skeleton (no RAG logic yet — labelled `# PLACEHOLDER`
where empty, per CLAUDE.md §2):
- `src/msfea_bot/` split into `ingestion` / `retrieval` / `generation` / `llm`
  (the provider abstraction, §3) / `api`, plus `config.py` (all env vars in one
  place, §6).
- `llm/` provides the `LLMProvider` contract + `get_llm_provider()` factory —
  concrete vendor deferred to the generation phase (§5.6).
- FastAPI app with a real `/health` endpoint; `/chat` deferred to the walking
  skeleton (§5.3).
- Tooling: `pyproject.toml` (src-layout, hatchling; runtime deps kept minimal —
  fastapi/uvicorn/pydantic-settings — heavier RAG deps added in their phases),
  `.env.example`, `.gitattributes` (LF normalization), Docker/compose skeletons
  (app + pgvector), `eval/` placeholder, expanded README.
- `docs/dev-workflow.md` added.

**Verified before push:** `pytest` 1 passed, `ruff check` clean, `mypy --strict`
clean.

**Workflow change (this session).** Switched to committing **directly to `main`,
no branches** (solo dev, tested before push). Recorded in `docs/dev-workflow.md`.

**Next.** Phase 2 — evaluation harness: `eval/golden_set.jsonl` structure + the
two-metric runner (retrieval recall@k, answer correctness/refusal) on placeholder
questions. First RAG design decisions (embedding model, chunking) will be
presented with trade-offs as ADRs when we reach ingestion.

---

## 2026-07-20 — Phase 0 kickoff (no content yet)

**Situation.** Repo was empty except `CLAUDE.md`. Department has not yet
provided source material or numeric success criteria. Goal confirmed with the
user: reduce repetitive student internship emails by deflecting questions the
guidelines/FAQ already answer, and safely escalating the rest.

**Done.**
- `git init` — repo under version control.
- Set up the documentation system:
  - `docs/decisions/` — ADR process (README + template + ADR-0001).
  - `docs/progress.md` — this journal.
- Wrote Phase 0 **Definition of Done** (`docs/definition-of-done.md`) with
  binary product behaviors (Tier A), measurable quality gates (Tier B),
  pilot outcomes (Tier C), and operational/handover criteria (Tier D).
  Numeric targets are marked `[CONFIRM]` pending department sign-off.

**Blocked on department (see DoD §4).** Baseline email volume, target reduction
+ timeframe, pilot cohort, go-live date, escalation contact, and the actual
source docs + real past student questions.

**Also captured.** Two future requirements from the user, recorded in
[backlog.md](backlog.md) (not built now): B-1 smart escalation routing to the
most-relevant person, and B-2 department-specific answers. B-2 carries a
forward-compat note: reserve a `department`/`applies_to` metadata field in
Phase 4 ingestion so we don't have to retrofit the index later.

**Decided.** `[CONFIRM]` metric targets kept as provisional placeholders; added
a "baseline-first" note to the DoD making clear the standard practice is to
measure a baseline before fixing targets (there is no universal magic number).

**Next (all buildable on placeholder content, no department input needed):**
1. Repo scaffolding — module layout (ingestion / retrieval / generation / api),
   `.env.example`, `.gitignore`, README, Docker/compose stubs.
2. Phase 2 — evaluation harness structure with a placeholder golden set.
3. Phase 3 — walking skeleton on 1–2 placeholder docs.
