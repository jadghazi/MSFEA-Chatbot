# Progress journal

Dated log of what was built each working session and why. This is the
monitoring trail for the capstone. Newest entries at the top. Keep entries
short: what changed, why, what's next, what's blocked.

---

## 2026-07-23 — Admin dashboard + curation feedback loop (B-3/B-3a, ADR-0010)

Built the loop that turns failures into KB content.
- **Storage:** Postgres `curated_answers` table as an ingestion source (chosen
  over a file — ephemeral container FS vs persistent DB volume; transactional).
  Vector store rebuilds from md files + curated table; publish = incremental
  embed+upsert.
- **Ratings:** `interactions.rating`; widget 👍/👎; `POST /rate`; `/chat` returns
  `interaction_id`.
- **Admin (token-auth, constant-time):** `/admin/api/stats`, `/admin/api/feedback`
  (refused OR 👎, with retrieved chunks), `/admin/api/curate` (publish answer).
- **Dashboard page** (`/dashboard/`): stats, feedback list, inline answer→publish.
- `curation/` module (store + service). `skeleton ingest` now includes curated.

**Verified end-to-end (live HTTP):** ask → refuse → admin curates → re-ask →
answered from curated content; ratings + auth (401 w/o token) + dashboard (200)
all work; demo data cleaned up afterward. Hermetic admin/rate tests + DB
integration test (skips w/o DB). ruff/mypy/pytest clean (46 tests).

**Follow-ups (ADR-0010):** edit/retire curated answers via UI; auto-add curated
Q&A to golden set; replace shared token with AUB SSO.

## 2026-07-23 — Name redaction via local NER (closes the §7 names gap)

Closed the open privacy gap from ADR-0007/0008. `anonymize()` now redacts
personal names using local spaCy NER (`en_core_web_sm`), after the email/number
regexes. Free/offline (no API/per-use cost); fail-safe if the model is missing
(warns, skips names, regex still applies). Verified: "Sara Khoury, student
202012345, sara@aub.edu.lb" -> "[redacted-name], student [redacted-number],
[redacted-email]"; domain terms ("8 weeks", "FEAA 500", "3.3") preserved.
Dep: `spacy` + one-time `python -m spacy download en_core_web_sm` (into Docker in
Phase 10). ADR-0009. 39 tests green.

## 2026-07-23 — Phase 8: safety / abuse hardening

**Built (ADR-0008).**
- `api/security.py`: `sanitize()` (strip control chars) + thread-safe in-memory
  sliding-window `RateLimiter`. `/chat` rate-limited per client (429), sanitizes
  input, and returns a gentle message on empty input. Client key = client IP (or
  first X-Forwarded-For only when `trust_proxy_headers`).
- Hardened the system prompt: scope-locked to CDC topics; treat the question as
  untrusted; ignore embedded instructions / role changes / prompt-reveal; refuse
  out-of-scope or override attempts.
- Added a jailbreak golden case (`refuse-injection`).
- Config: `rate_limit_*`, `trust_proxy_headers`, `cors_allow_origins` in .env.example.

**Verified live:** legit question answered (co-op GPA 3.3); injection ("reply
HACKED") refused (no compliance); "write my essay" refused. Unit tests for
sanitize + RateLimiter; API rate-limit test (429). ruff/mypy/pytest clean (38).

**Notes / open gaps.** Grounding is the primary defense; prompt hardening is
defense-in-depth (no prompt is jailbreak-proof — regressions guarded by the eval
case). Rate limiter is per-process (single instance); multi-instance needs Redis.
Name-stripping in logs still a gap (needs NER) — carried from ADR-0007.

## 2026-07-23 — Phase 9: observability (interaction logging + unanswered log)

**Built (ADR-0007).**
- `observability/store.py`: Postgres `interactions` table (ts, anonymized
  question, refused, answer, citations, retrieved). Logging is **fail-safe** — a
  logging error never breaks the chat.
- `observability/privacy.py`: `anonymize()` strips emails + long digit runs
  (student IDs, phones), preserves domain numbers ("8 weeks", "3.3", "75%").
- `/chat` anonymizes the question once and uses it for BOTH the LLM and the log
  (CLAUDE.md §7). `Answer` now carries `retrieved` chunks for logging/diagnosis.
- `python -m msfea_bot.observability` prints the unanswered-questions log.

**Verified live:** the "how many credits is the internship?" refusal is now
captured in the unanswered log; a PII question was stored as
`student [redacted-number], email [redacted-email]`. Privacy unit tests; API
tests made hermetic (stub logging). ruff/mypy/pytest clean (32 tests).

**Known limitation (→ Phase 8):** regex anonymization does not strip personal
names (needs NER). Tracked in ADR-0007.

## 2026-07-22 — Phase 7: API /chat endpoint + chat widget

**Built.**
- `POST /chat` (FastAPI) wired to the guarded `generate_answer`; returns
  `{answer, citations, refused, disclaimer}`. CORS enabled (for cross-origin
  embed), input length cap, graceful degradation (never 500s the student — a
  backend error returns a polite escalation).
- `widget/widget.js` — self-contained vanilla-JS chat bubble (bottom-right),
  thin client that POSTs to `/chat` and renders answer + sources + disclaimer.
  Embeds via one `<script>` tag (`data-api-url` or `window.MSFEA_CHAT_API`).
- `widget/demo.html` served via a static mount at `/widget` for local demoing.

**Verified over real HTTP:** `/health` ok; `POST /chat` returned a grounded
answer with citations + disclaimer; widget files served (200). 4 API tests
(monkeypatched, no DB/LLM). ruff/mypy/pytest clean (28 tests).

**Run locally:** `uvicorn msfea_bot.api.app:app` then open
`http://localhost:8000/widget/demo.html`.

**Minor refinement noted.** The model sometimes inlines `[label]` citations in
the answer text (redundant with the citations field) — a small prompt tweak for
later; not blocking.

## 2026-07-22 — Phase 4: improved chunking, measured — context-recall 90% → 100%

**Change (ADR-0006).** Chunker now splits oversized sections into <=500-char
overlapping windows (overlap 150), each keeping its section heading. Window size
chosen by an empirical sweep against context-recall (not guessed).

**Sweep result:** 500 is the largest window reaching 100% context-recall@5
(baseline 86 chunks/90% → 144 chunks/100%).

**Confirmed end-to-end:** the two previously-failing questions now answer
correctly ("75% on the Moodle quiz"; "formal petition ..."), i.e. the two
answer-eval false refusals are fixed. Expected B4 false-refusal now ~0/21
(full LLM answer-eval re-run deferred to conserve free-tier quota; context-recall
is the validated predictor).

**Metrics now:** doc-recall@5 100%, context-recall@3 95%, context-recall@5 100%.
Added windowing unit tests. All checks green.

## 2026-07-22 — Phase 4/5 prep: built the metric that measures the real gap

Before tuning retrieval, built the metric that captures the actual problem
(CLAUDE.md §2: build the metric first).

**Added `evidence` to every answerable golden item** — a verbatim fact that must
appear in retrieved context (e.g. "75%", "formal petition"). A test enforces that
each evidence string really exists in its KB source doc (no mis-annotations).

**New metric: context-recall** (`eval/metrics.evidence_present`) — is the answer's
evidence in the top-k chunks? Stricter than doc-level recall, needs no LLM.

**Baseline:** doc-recall@5 = 100% (saturated), **context-recall@5 = 90% (19/21)**.
The 2 misses (`int-skills-quiz` '75%', `int-petition-exception` 'formal petition')
are exactly the 2 answer-eval false refusals — so this free metric predicts the
expensive LLM one. Now we can tune retrieval cheaply and confirm with one LLM run.

**Next:** improve chunking (Phase 4) to get those 2 evidence chunks into top-5,
measured against context-recall; then hybrid keyword search (Phase 5) if needed.

## 2026-07-22 — Phase 6 COMPLETE: guardrails + first answer-quality numbers

**Built.** `generation/answer.py`: answer only from context, two-layer refusal
(similarity-threshold gate + prompt `INSUFFICIENT_CONTEXT` marker), structured
citations, disclaimer on every answer. Skeleton uses it. `eval/answer_eval.py`
measures Layer-1 answer metrics.

**Answer eval (26 golden questions, flash-lite):**
- correct-refusal (B3): **5/5 = 100%** (target 100% ✅)
- missed refusals: **0** ✅
- false-refusal (B4): **2/21 = 9.5%** (target ≤10% ✅, just under)
- citation present: 26/26 ✅ · disclaimer: 26/26 ✅

**Key diagnosis (eval-driven).** The 2 false refusals (`int-skills-quiz`,
`int-petition-exception`) are **retrieval failures, not guardrail failures** —
the answer-bearing chunk was NOT in the top-5, so the bot correctly refused
instead of hallucinating. This validates the guardrail AND pinpoints the real
gap: **chunk-level** retrieval (< doc-level recall@5 of 100%). Exact-term
questions ("75%") are the classic case for **hybrid search** (§5). → concrete
Phase 4/5 to-do, measured against this baseline.

**Caveats.** Synthetic questions, small set (26), flash-lite model. Targets are
provisional (`[CONFIRM]`). Don't over-read; re-measure with real student
questions.

**Quota note.** Free-tier is per-model and tight: gemini-2.0-flash = 0/day,
gemini-flash-latest (3.6-flash) = 5/min & 20/day, flash-lite = usable. Now
defaulting to `gemini-flash-lite-latest` (ADR-0005 updated). Free tier is a
dev-only constraint; production needs paid/AUB vendor (one-file swap).

## 2026-07-22 — Retrieval wired into eval: first baseline recall@k

`eval/retrieval_eval.py` runs the golden set through the vector store and reports
document-level recall (is a chunk from the expected source_doc in top-k).

**Baseline (crude section chunking, bge-small, 21 answerable questions):**
recall@1 = 71% (15/21), recall@3 = 100%, recall@5 = 100%. No misses at k=5.

**Honest read.** Strong, but (a) small KB + 21 questions makes 100%@3 easy — don't
over-read it; (b) this is *document*-level, coarser than chunk-level; (c) the
recall@1 misses are likely multi-doc facts where the top hit is a different but
valid doc than the single label. Retrieval is not the bottleneck right now, so
avoid over-tuning a near-saturated metric (premature optimization).

**Ops note.** The pgvector container had stopped (Docker/host sleep); the named
volume persisted the 86 chunks across restart — nice reproducibility signal.

**Recommended next.** The biggest *product* gap is guardrails (Phase 6): the bot
has no refusal logic yet, so the 5 should-refuse golden cases would currently
fail. Adding refusal + similarity threshold + grounded prompt + structured
citations is higher value than tuning retrieval further, and it lights up the
answer metric (Layer 1 + refusal correctness).

## 2026-07-22 — Phase 3 COMPLETE: walking skeleton (all 5 steps) 🎉

The full path works end to end: `python -m msfea_bot.skeleton "<question>"` →
chunk → embed → pgvector → retrieve → Gemini → **grounded answer with citations**.
For "minimum internship duration?" it answered "8 weeks" and correctly surfaced
the CEE/IEM 6-week department exceptions, citing its source sections.

**Model note.** `gemini-2.0-flash` had a 0 free-tier quota on this account and
`gemini-2.5-flash` is deprecated for new users (it's mid-2026); using
`gemini-flash-latest` (stable alias). Provider swap remains one file (ADR-0005).

## 2026-07-22 — Phase 3: walking skeleton (steps 1-4 working)

**Decisions.** ADR-0004 embedding model = local `BAAI/bge-small-en-v1.5`
(free/offline). ADR-0005 provisional LLM provider = Google Gemini free tier
(behind the llm abstraction; one-file swap later; privacy note for real data).

**Built + verified end-to-end (chunk -> embed -> pgvector -> retrieve):**
- `ingestion/embeddings.py` (sentence-transformers, 384-dim), `retrieval/store.py`
  (pgvector: rebuild-on-ingest, cosine search), `llm/gemini.py` + factory wiring,
  `msfea_bot/skeleton.py` runner (`ingest` / `"<question>"`).
- Docker: pgvector container up; `skeleton ingest` indexed **86 chunks**.
- Retrieval smoke test returns sensible chunks (e.g. "split into two 4-week
  periods" -> department-specific rule chunks; "co-op GPA" -> eligibility).
- deps added: sentence-transformers, psycopg[binary], pgvector, google-genai
  (extra). ruff/mypy/pytest all clean (mypy target bumped to 3.12 for numpy stubs).

**Remaining (step 5).** The final LLM call needs a Gemini API key in a local
`.env` (LLM_API_KEY). Retrieval already works without it. Once the key is added,
run `python -m msfea_bot.skeleton "<question>"` for the full grounded answer.

**Next after that.** Phase 4 (proper ingestion: semantic chunking + one-command
rebuild) and wiring retrieval into the eval harness for the first real recall@k.

---

## 2026-07-22 — Phase 2: evaluation harness (golden set + metrics)

**Built.**
- `eval/golden_set.jsonl` — 26 cases (21 answerable, 5 should-refuse), seeded from
  the real CDC-KB FAQs + refusal cases (dates, case-specific, fees, abuse,
  off-topic) + 2 department-specific "clarify" cases. `is_synthetic` marks the 15
  predicted ones (placeholders until real student questions arrive).
- `eval/loader.py` (validated load), `eval/metrics.py` (retrieval recall@k +
  Layer-1 deterministic answer checks: refusal / citation / disclaimer),
  `eval/run.py` CLI summary.
- Tests: 10 passing (metrics + golden-set-vs-KB consistency). ruff + mypy clean.

**Honest status of the harness** (ADR-0002 layers): Layer 1 ready; retrieval
recall@k function ready but needs a retriever (Phase 4) to run end-to-end;
Layer 2 (LLM-judge) pending the provider (Phase 6); Layer 3 pending real answers.

**Backlog.** Added B-4: question-augmented indexing (Phase 5 retrieval tuning) —
generate questions as retrieval aids, never inject generated answers into the KB.

**Next.** Phase 3 (walking skeleton) or Phase 4 (ingestion) — first real RAG that
gives the eval harness something to actually score. First RAG design decisions
(embedding model, chunking) will come as ADRs with trade-offs.

---

## 2026-07-22 — Phase 1: scope broadened + batch-1 sources normalized

**Scope decision applied (ADR-0003).** Bot scope = all CDC content. Updated
CLAUDE.md §1 wording accordingly (user confirmed; new preference: update plan
docs on new decisions without re-asking).

**Tooling.** Added `python-docx` + `python-pptx` as ingestion/parse dependencies.

**Normalized all 4 batch-1 sources → `kb/normalized/`** (clean Markdown, the
canonical ingestion input): `cdc-knowledge-base.md`,
`summer-training-guidelines-2026.md`, `internship-report-templates-and-rubrics.md`,
`final-presentation-slide-template.md`. Process (code extraction + assisted
curation) documented in kb/README.

**Verified against originals:** no mojibake left; all 5 dept emails + CDC email;
all 5 department-specific rule sections; key numbers intact; deliverables table
9/9 rows; 18 FAQ pairs preserved; 3/3 rubric tables. Committee cover note
intentionally stripped.

**Next.** Phase 2 — draft the golden set (the CDC-KB FAQs give ~18 real Q/A/source
triples to seed it) + build the metric runner. Real student questions still to
come (batch 2). Then ingestion (Phase 4).

---

## 2026-07-22 — First KB content arriving — starting Phase 1 (KB intake)

**Phase-numbering note.** Earlier commits labelled the repo scaffolding as
"Phase 1"; that was un-numbered groundwork. CLAUDE.md's *numbered* Phase 1 is
**Knowledge base intake**, which begins now that some real content has arrived.

**Done.** Set up the KB source-of-truth structure: `kb/source/` (tracked
originals — the landing zone for documents) and `kb/README.md` (intake
convention, provenance manifest, add-content-later workflow). Built index stays
in gitignored `data/`.

**Status.** User has received *some* (not all) of the KB content. Treating it as
batch 1 — the reproducible pipeline absorbs the rest later with no rewrite.

**Batch 1 received & assessed (4 files).** `msfea_cdc_kb.md` (clean, sectioned,
has FAQs), `Summer training guidelines - June 2026.docx` (authoritative course
rules; has dept contacts + dept-specific rules; tables need python-docx),
`Internship Templates and Rubrics.docx` (templates/rubrics; strip committee
note), `Advanced Experience template.pptx` (presentation template, 8 slides).
Originals committed to `kb/source/`; manifest filled.

**Concrete findings.** (1) Escalation contacts (B-1) and department-specific
rules (B-2) are now real, with data — captured in backlog. (2) Cleaning is
genuinely needed (docx tables + encoding) — validates Phase 1. (3) Scope
question raised: the markdown KB covers CO-OP/IAESTE/full-time/mentorship, beyond
internship-only — awaiting user decision before normalizing/ingesting.

**Next (pending scope decision).** Clean/normalize each source into sectioned
markdown in `kb/normalized/`; for docx use python-docx. Then draft golden-set
questions (the FAQs seed it). Real student questions still to come (batch 2).

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
