# Progress journal

Dated log of what was built each working session and why. This is the
monitoring trail for the capstone. Newest entries at the top. Keep entries
short: what changed, why, what's next, what's blocked.

---

## 2026-07-27 — Phase 5: hybrid retrieval (ADR-0011)

Triggered by a real miss: "difference between internship and co-op?" answered
co-op-only. Diagnosis — the internship-side chunk sat at vector rank ~40; pure
vector never retrieved it.

- **Fixed the ruler first.** The golden set had no cross-topic cases, so retrieval
  read a *false* 100% context-recall. Added comparison + exact-term questions
  (`internship-vs-coop`, `internship-mandatory`, `feaa500a`); honest baseline was
  context-recall@5 = 97% (1 miss).
- **Hybrid search (kept).** Vector + Postgres full-text (`tsv` generated column +
  GIN), fused with **Reciprocal Rank Fusion**; all in Postgres, no new infra.
  Returned chunks keep cosine `score` (threshold gate unaffected). **Fixed a bug in
  my own first cut:** the keyword half ANDed every word (1 hit for a sentence);
  switched to OR (`to_tsquery('a | b | …')`) so keyword is a real recall booster.
- **Measured:** context-recall@1 **79% → 90%**, doc-recall@1 **83% → 90%**;
  @5 unchanged (97%); @3 dipped 97%→93% (reordering within top-5). Clear top-rank
  win, same top-5 coverage.
- **Reranker: declined** (ADR-0011) — a cross-encoder's model/latency/image cost
  isn't worth rescuing one comparison question at this KB size (Jad's call).
- **Query decomposition: backlogged (B-5)** — the real fix for cross-topic
  comparisons; build when the data shows the need. The `internship-vs-coop` miss
  stays in the golden set as the tripwire.

New: `tests/test_retrieval.py` (RRF unit tests + DB-gated keyword-recall test).
ruff/mypy clean; 66 tests pass (1 known-flaky timing test passed on re-run).

---

## 2026-07-27 — Add CO-OP handbook to the KB (batch 2), reconciled to one source

New source `kb/source/msfea-cdc-coop-handbook.pdf` (official 10-page MSFEA CO-OP
handbook) added and integrated.

- **Finding:** the KB already covered CO-OP well in `cdc-knowledge-base.md`
  (curated from this same handbook), and 4 CO-OP golden questions already passed.
  So this was a **reconcile + gap-fill**, not a fresh add — a naive second doc
  would have created ~80% duplicate chunks competing in retrieval.
- **Decision (user-approved): handbook = single authoritative CO-OP source.**
  Normalized the full handbook → `kb/normalized/msfea-cdc-coop-handbook.md`
  (extracted with `pypdf`; stripped cover/ToC/running-header mojibake/footnotes;
  fixed `)!`/`1.!` bullets and `|` headings). **Merged in the KB-only facts** so
  nothing was lost: the Figure-1 application-timeline (an image, transcribed from
  the batch-1 KB), the "max 3 ranked applications" detail, and the 4-vs-6-month
  duration note. Then **trimmed the CO-OP section in `cdc-knowledge-base.md` to a
  one-line pointer** so every co-op fact lives in one place. Provenance/​limits
  recorded in an "About this document" footer + the KB README manifest.
- **Known gap (flagged, not hidden):** the exact application deadlines are in an
  image (Figure 1) and the FEAA 500 syllabus (Appendix 1) isn't in the PDF text.
- **Eval (measured, per §2/§4):** moved the 4 existing CO-OP golden entries'
  `source_doc` to the handbook and **added 4 net-new questions** for the newly
  captured content (deliverable forms, midterm site visit, FEAA 500A tuition,
  pay). Re-ingested (175 chunks). Retrieval eval: **doc-level recall@3/5 = 100%,
  context-recall@5 = 100%, no misses** on 26 answerable questions (was 22).
- **Retrieval miss found + fixed (retrieval-before-generation):** `coop-second-
  tuition` first missed because a hard line-wrap split the evidence phrase
  (`no additional\n  tuition`) so no chunk contained it literally — a
  normalization artifact, not a ranking problem. Un-wrapped the phrase,
  re-ingested → green.
- `pypdf` added to `dependencies` (with reason) for reproducible PDF extraction.

ruff/mypy clean; 59 tests pass.

---

## 2026-07-23 — Curated Q&As as live eval cases (closes ADR-0010 follow-up)

Curated answers now feed the evaluation harness, so a real past failure that was
fixed by curation becomes a permanent **retrieval + grounding regression test**.

- **Derive at run time, don't copy into the file.** New `eval/curated_cases.py`
  `curated_eval_items()` expands each *active* curated row into a `GoldenItem`
  (`id=curated-<n>`, `source_doc=admin-curated`, `evidence=<answer>`,
  `is_synthetic=True`). It is **not** written into `golden_set.jsonl`.
  - *Why this way (design call, user-approved):* an admin **edit** regenerates
    the case from the current row and a **retire** (`active=false`) drops it —
    consistency is automatic, no snapshot to drift, and the human-reviewed
    golden file stays stable. Writing into the file would need sync code that
    rewrites/deletes lines on every admin click.
  - *Honest scope:* these check "does the bot still retrieve + stay grounded in
    this curated chunk?" (the #1 RAG regression, §2) — not independent answer
    quality, since the expected text is the same admin answer we indexed.
- **Wired into both runners**, reported **separately** so the golden baseline
  stays legible: `retrieval_eval` → "21 golden + 1 live curated"; `answer_eval`
  and `eval.run` likewise. DB hiccup degrades to zero curated cases (file eval
  still runs).

**Verified live:** `eval.retrieval_eval` includes the curated case and
context-recall@5 = 100% (no misses); a DB-gated test proves the case follows an
edit (expected text updates) and disappears on retire. ruff/mypy clean;
**59 tests pass**.

---

## 2026-07-23 — Edit / Retire curated answers (closes ADR-0010 follow-up)

Made the "Published answers" tab actionable — staff can now correct or remove a
published answer from the UI, no DB access needed.

- **Retire.** `POST /admin/api/curated/retire` → `retire_curated_answer`:
  deactivates the row (`active = false`, kept for history) **and** deletes its
  vector chunk so the bot stops using it. Idempotent (retiring twice → False).
- **Edit.** `POST /admin/api/curated/edit` → `edit_curated_answer`: updates the
  row text and **re-embeds/upserts** the chunk, so retrieval reflects the edit
  immediately.
- **Store:** added `get_curated`, `update_curated_answer`,
  `deactivate_curated_answer`.
- **Safety fix:** added `retrieval.store.delete_chunk` (exact-id delete) and used
  it for retire — the existing prefix `delete_chunks("curated-1")` would also
  match `curated-10`. `delete_chunks` kept for bulk/source deletes.
- **Test-leak fix:** the curation integration test deleted the chunk but not the
  `curated_answers` row on teardown — that's what created the earlier
  `zzz-test` pile-up. Teardown now removes both.
- **UI:** each published card has **Edit** (inline question/answer editor with
  Save/Cancel) and **Retire** (confirm → card animates out, count updates).

**Verified:** live DB integration tests — edit re-indexes (old marker gone, new
marker retrievable), retire removes the chunk + deactivates the row and is
idempotent. ruff/mypy clean; **55 tests pass**. (One live curated row remains —
"How many credits is the internship??", created via the dashboard, left in place
as real content.)

---

## 2026-07-23 — "Published answers" tab + KB test-data cleanup

- **New read-only tab.** `GET /admin/api/curated` lists the curated Q&As (from
  `list_curated`, active only) so staff can see everything they've published
  without touching the database. Dashboard shows them as searchable cards
  (question · answer · author · date) with a live count badge.
- **Cleanup (a real bug found while building it).** The `curated_answers` table
  held 7 leftover **test/placeholder** rows (e.g. "zzz-test placeholder…") from
  earlier sessions, and 2 of their chunks were **live in the vector store** —
  i.e. placeholder junk was retrievable and could have been served to a student.
  Cleared all curated rows + `admin-curated` chunks (no real content existed yet)
  for a clean slate. **Verified** end-to-end over HTTP: publish → appears in the
  new endpoint → removed; 0 curated rows remain.

ruff/mypy clean; 49 tests pass (added `/admin/api/curated` coverage).

---

## 2026-07-23 — Dashboard usability + resolution state (B-3a follow-up, ADR-0010)

Reworked the admin dashboard around non-technical CDC staff, and fixed a real
workflow gap: an answered item kept re-appearing after a page refresh.

- **Resolution state (the fix).** Added `interactions.resolved_at` (nullable,
  migrated with `ADD COLUMN IF NOT EXISTS`). The attention queue and `pending`
  stat now filter `resolved_at IS NULL`. Publishing an answer calls
  `resolve_by_question` (clears every open item asking the same thing);
  new `POST /admin/api/resolve` + `resolve_interaction` let an admin *dismiss*
  an item without publishing (e.g. a 👎 that was actually fine). This completes
  the "review list with a status" anticipated in backlog B-3a.
- **Plain-language redesign.** No jargon ("chunks"/"escalated" gone from the UI).
  Split into two tabs — **Needs your attention** (action queue with a live count
  badge) and **Usage** (labelled stat cards + a deflection %). Cards show a
  friendly badge, the question, what the bot said (for 👎), a clear
  "write the answer" box, Publish + Dismiss, and technical diagnostics tucked
  into a collapsible "Why couldn't it answer?" section that explains the
  content-gap-vs-wording split in words.
- **Sign-in UX.** Access code remembered in `sessionStorage` (survives refresh,
  clears on tab close / Sign out); human-readable error messages; cards visibly
  resolve and disappear.

**Verified:** live DB check — a refused item shows in the queue (pending 6),
`resolve_by_question` clears it, and a simulated refresh does **not** bring it
back (pending 5). ruff/mypy clean; 48 tests pass (added resolve + curate-resolve
coverage).

**Still open (ADR-0010):** edit/reactivate a *curated answer* via UI (distinct
from dismissing a feedback item); auto-add curated Q&A to the golden set; SSO.

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
