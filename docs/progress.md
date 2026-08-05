# Progress journal

Dated log of what was built each working session and why. This is the
monitoring trail for the capstone. Newest entries at the top. Keep entries
short: what changed, why, what's next, what's blocked.

---

## 2026-08-05 — Restored lost links, new CDC rules, clickable answers (ADR-0016)

Audited the original sources against the normalized KB and found **four URLs that
existed in the .docx but were lost in normalization** — they sat behind anchor text
("here", "petition", "self-secured internship form"), which is exactly how links
vanish when Word becomes Markdown. The bot was telling students to complete a form
without being able to reach it, in a paragraph warning the internship won't count
toward graduation if mishandled.

- **Restored + added links:** CDC students page, self-secured internship form, AUB
  petition system, and the letter / convention-de-stage request form (supplied by the
  CDC). The petition link is the bare entry point, not the .docx's deep link — that
  one carried an Oracle APEX session id, which isn't durable.
- **New CDC rules** (not in the June 2026 .docx, recorded as such in the document's
  provenance footer): 90-credit eligibility minimum; remote internships not accepted;
  internships inside AUB not accepted except in special circumstances.
- **Clickable, safely.** The widget linkifies URLs and emails by building DOM nodes —
  `createTextNode` for prose, `<a>` only for a scheme-checked match — so injection is
  impossible by construction rather than escaped. Verified `javascript:`, `data:` and
  raw `<img onerror=...>` all render as inert text. Coordinator emails are now
  `mailto:` links, so escalation is one tap.
- **Prompt:** the model had the link in context and still said "linked on their
  website". One rule now requires URLs verbatim.

**Two intermediate steps were wrong and the measurement caught them.** Adding the
content *regressed* context-recall 97% -> 92%, breaking `internship-mandatory`. Then
excluding department chunks for unscoped students — which seemed principled — measured
**worse** (89%) and broke `dept-split-internship`, whose whole point is that an
unplaced student should still learn the rule depends on their department. Reverted.

The actual fixes: **top_k 5 -> 7** (swept: 5=92%, 7=95%, 10=97% — 7 is the knee), and
**excluding "About this document" provenance footers from the index** — 7 of 182
chunks were maintainer notes, one retrieved at rank 5 for "how do I submit a
petition?". One of those footers predated this work, so that was a latent bug.

**Final: context-recall@7 = 97%** (37/38), same single known `internship-vs-coop`
miss, over 38 answerable questions (was 33). The eval now reports at the *configured*
top_k — gating CI on a depth production doesn't use tests the wrong thing. Note
`.env` pinned TOP_K=5 and overrode the new default; updated there too.

Flagged for the CDC: the new "remote not accepted" rule contradicts IEM's rule
permitting remote internships with U.S.-based companies (the general rule now points
at the department exceptions rather than stating a false absolute); and ~12 named
forms still have no link in any source document. 102 tests pass; ruff/mypy clean.

---

## 2026-08-05 — Department-scoped answers + escalation routing (B-1 + B-2, ADR-0015)

Closed the two oldest backlog items. Both were raised on day one and deliberately
deferred; the audit's metadata column is what made them cheap to build now.

- **Measured before designing** (§2, retrieval-before-generation). Unscoped, "can I
  split my internship into two 4-week periods?" returns **four departments'
  contradictory rules** in the top-5. And exclusion alone is *not* enough: IEM's
  "final presentations are generally not required" sits at **vector rank 8**, so an
  IEM student would be told the general rule — wrong for them.
- **Retrieval:** chunks tagged by department from the KB's own `### ... (CEE)`
  headings (6 of 175). `search()` excludes other departments **and reserves one slot**
  for the student's own rule when it reached the candidate pool but not top-k. Only
  the reserved slot fixes the rank-8 case; it can displace at most one general chunk.
- **Routing (B-1):** refusals now name the student's coordinator — "please contact
  Hiam Khoury (hk50@aub.edu.lb), the Civil and Environmental Engineering
  coordinator." Contacts are *data* in `msfea_bot/departments.py`, with a test
  asserting every name and address still appears in the KB so the copy can't drift.
- **Widget:** asks the department once before the suggestions, remembers it in
  `localStorage` (server stays stateless — no session store, no student profile),
  shows it as a header pill that reopens the picker, and offers "Skip / not sure".
- **Untrusted by default:** the code arrives from a page we don't control, so an
  unknown value degrades to an unscoped answer. Verified: `nonsense`, an SQL-injection
  string, `""` and `null` all return 200 with a normal answer and the index intact.

**Measured:** department cases **2/4 -> 4/4** context-recall@5; general questions
**unchanged at 97%** with the same known `internship-vs-coop` miss (33 answerable
questions, was 29). **Verified live:** same question, CEE -> "may be split if at
least one period is in civil or construction engineering"; MECH -> "cannot be
split"; no department -> CEE's rule, which is exactly the old behaviour this fixes.

Note: updating `generate_answer`'s signature broke a stale test stub, and the
endpoint's broad `except` turned that TypeError into a graceful refusal rather than
a failure — a reminder that the never-500-the-student handler can mask a programming
error. Stubs now take `**kwargs`. 102 tests pass; ruff/mypy clean.

---

## 2026-07-30 — RAG practice audit + remediation (ADR-0012/0013/0014)

Audited the whole pipeline against a 32-item RAG practice checklist
(`rag-audit-checklist.md`), then fixed what it found. Every load-bearing claim was
**measured** rather than reasoned about, which changed the conclusion three times.

- **Audit result:** 16 PASS, 10 PARTIAL, 5 INTENTIONAL, 1 FAIL. Five items are
  deliberate documented decisions (reranker declined, query rewriting deferred,
  single-turn design, prompt-layer injection defence, disabled similarity gate) and
  are explicitly *not* things to fix.
- **The FAIL — no sampling params at all (ADR-0012).** The provider passed only
  model+contents, so generation ran at Gemini's ~1.0 default. Fixed first because it
  is the *measuring instrument*: at that temperature two `answer_eval` runs over
  identical code disagree, so nothing else could be validated. Testing the fix
  disproved my own assumption — temperature 0 alone still gave 2 distinct answers in
  3 runs; **temperature 0 + a pinned seed** gave 3 identical, confirmed end-to-end.
- **Curated answers silently half-indexed (ADR-0013).** They skipped windowing, and
  bge-small truncates at 512 tokens — so a max-size 8000-char answer had **only ~39%
  embedded** (1302 tokens in, 512 kept) and its tail was unreachable by any query.
  Windowing alone wouldn't have fixed it: `split_windows` only breaks on newlines, so
  a run-on paragraph came back as one 5,520-char window. Now sentence-normalized then
  windowed → 17 chunks, max 110 tokens, tail searchable. Found and fixed a
  **test-teardown leak** in the process (teardowns deleted `curated-<id>`, which no
  longer matches windowed ids — two orphans were live in the dev DB).
- **Table headers restored at zero retrieval cost (ADR-0014).** 14 of 174 chunks held
  table rows with no column labels. The obvious fix *hurt*: folding the header into
  chunk text dropped context-recall@5 97%→93% (reviving the exact `int-skills-quiz`
  miss ADR-0006 fixed), and keeping it in `text` for display dropped @1 90%→83%
  because `tsv` is generated from `text`. Solution: a `display_prefix` column
  re-attached at read time. All metrics identical to baseline.
- **Also fixed:** citations are now verified against the context actually supplied
  (an invented label used to reach the student *and* pass the citation-presence
  metric); chunk frontmatter is persisted (`metadata JSONB` — backlog B-2's reserved
  slot); the embedding model is pinned to an exact HF revision with its fingerprint
  recorded in `index_meta`, and the Dockerfile bakes that same revision; the index
  rebuild is now atomic.
- **Documented, not changed:** the `SIMILARITY_THRESHOLD=0.0` gate is deliberate
  (prompt marker is the active refusal layer; the gate waits on calibration) and the
  absence of a vector index is correct at this size — both now carry their rationale
  and a revisit trigger. Stale status lines in `eval/README.md`, `eval/run.py` and
  `ingestion/__init__.py` corrected.

**Still open:** ADR-0002's **Layer 2 faithfulness judge** was never built, so nothing
checks that an answer's claims are supported by the retrieved context — the one
substantive gap left. Also worth a decision: the CI floor is 0.90 while actual
context-recall is 0.97, so a drop to 91% would pass unnoticed.

Metrics unchanged throughout: doc-recall 90/97/97%, context-recall 90/93/97%, same
tracked `internship-vs-coop` miss. 82 tests pass; ruff/mypy clean.

---

## 2026-07-27 — Security review + production hardening

Pre-exposure pass on the public LLM endpoint, plus turnkey deploy assets. Full
write-up in [deployment.md](deployment.md) §6.

- **Security review — no critical issues.** Verified safe: parameterized SQL (no
  injection), widget/dashboard output escaping (no XSS), PII anonymized before LLM
  + logging, prompt-injection hardening, graceful errors, `pip-audit` clean.
- **Fixed:** CORS was `*` → **strict-by-default** (empty = deny cross-origin;
  set the real page origin in prod). Rate-limiter map could grow unbounded under
  many distinct IPs → **periodic sweep** of stale keys (+ test).
- **Accepted/documented:** admin endpoints unthrottled but protected by a
  192-bit random token + constant-time compare; in-memory limiter is per-process
  (Redis for multi-instance) — both noted with the SSO/scale follow-ups.
- **Turnkey deploy assets:** `docker-compose.prod.yml` (Caddy overlay =
  automatic HTTPS + `TRUST_PROXY_HEADERS`), `deploy/Caddyfile`, `deploy/nginx.conf`
  (IT-managed TLS), `deploy/backup.sh` + `restore.sh` (pg_dump). Documented the
  proxy↔rate-limit setting, secrets/rotation, and a pre-launch checklist.

Only IT-supplied *values* remain (domain, page origin, cert/auto-cert, LLM
provider) — no further engineering blocked. ruff/mypy clean; tests pass.

---

## 2026-07-27 — Phase 10: containerize + deploy + CI

Turned the placeholder Docker skeleton into a real, portable deployment and wired
up CI. Built and **validated the image end-to-end**, not just written.

- **Dockerfile** (python:3.12-slim): **editable install** (so `parents[3]` path
  resolution for kb/widget/dashboard points at /app — a normal install would
  break it); **models baked in** (embedding + spaCy) so the container needs no
  internet at runtime (firewall-safe, fast startup); **CPU-only torch** via the
  PyTorch CPU index (cuts the download ~10x and the image by >1 GB vs the default
  CUDA build — final image 2.81 GB); non-root user; stdlib healthcheck.
- **.dockerignore** keeps the context lean and secret-safe (excludes .env,
  .venv, kb/source, caches).
- **docker-compose**: DB healthcheck + `depends_on: service_healthy`;
  `DATABASE_URL` overridden to the `db` host so it works in-network regardless of
  the dev value in .env; restart policy; persistent pgdata volume.
- **CI** (`.github/workflows/ci.yml`): ruff + mypy --strict + pytest (DB-backed
  tests run against a Postgres **service**) + the **retrieval eval gated** on a
  0.90 context-recall floor (`EVAL_MIN_CONTEXT_RECALL`) so a retrieval regression
  fails the build (§4). Answer eval stays out of CI (needs the live LLM).
- **README**: full "run in a few commands" guide, required-env-vars table, and the
  KB-update flow.

**Validated live (containers up):** `/health` 200; in-container `ingest` → 175
chunks (models offline); `POST /chat` → correct grounded answer + citations +
logged; `/dashboard/` and `/widget/demo.html` served. 66 tests pass; ruff/mypy
clean.

**Pending (needs the department):** Phase 11 pilot — embed on the real page,
measure email deflection vs the Phase 0 Definition of Done.

---

## 2026-07-27 — Guiding refusal message (turn dead-ends into nudges)

A vague question ("what are the timelines") hit the refusal path and got a
dead-end "I don't have that, email someone" — misleading, since the bot *can*
answer once the question names a program.

- **Fix:** reworded `escalation()` to guide instead of dead-end — it names what the
  bot can help with (internships/CO-OP/IAESTE/full-time/mentorship) and asks the
  student to be more specific, while still giving the human contact for questions
  genuinely not in the docs. One message, helps every refusal (vague, out-of-scope,
  and truly-unanswerable) without misclassifying.
- **Verified live:** "what are the timelines" now returns the guiding message; the
  `refused` flag and eval refusal metric are unchanged (text-only change).
- Left as backlog: distinguishing "too vague" from "not in the docs" with separate
  markers — more precise but adds LLM-classification complexity; the single guiding
  message covers both well enough for now. 66 tests pass.

---

## 2026-07-27 — Program labeling for ambiguous questions (cheap disambiguation)

An ambiguous "what are the salary guidelines?" was answered CO-OP-only with no
signal about which program — confusing, since only the citation hinted at it.

- **Fix (prompt, no new capability):** when the question doesn't name a CDC
  program but the answer applies to only one, the bot prefixes it — e.g.
  "**For CO-OP:** …". If the question already names the program, no prefix.
- **Verified live:** "What are the salary guidelines?" → "For CO-OP: …"; "What GPA
  do I need for co-op?" → no prefix (already scoped). Refusal/citations/disclaimer
  unchanged; 66 tests pass.
- Separately confirmed the internship-salary **refusal is correct**: the KB has
  zero internship pay content (all pay text is CO-OP; internships can be paid or
  unpaid at the employer's discretion). Anti-hallucination working as designed.
- The full clarifying-question ("co-op or internship?") flow stays backlogged —
  it needs multi-turn/session state (shares machinery with B-2/B-5); deferred to a
  post-pilot decision once the unanswered-questions log shows how often ambiguity
  actually happens.

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
