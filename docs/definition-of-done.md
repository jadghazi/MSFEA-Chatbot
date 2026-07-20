# Definition of Done — Phase 0

**Status:** DRAFT — awaiting department confirmation on the numbers marked `[CONFIRM]`.
**Owner:** Jad Ghazi
**Last updated:** 2026-07-20

This is the Phase 0 deliverable from [CLAUDE.md](../CLAUDE.md) §5.0: turn the
department's success criteria into concrete pass/fail acceptance conditions,
written down. Every later phase is measured against this document. If a change
does not move us toward one of these criteria, we question whether to do it.

---

## 1. The problem, in one sentence

AUB MSFEA internship-course students email professors the same questions over
and over, even though **the answers already exist** in the internship
guidelines / FAQ / forms. The professors get spammed.

## 2. What success means (the outcome)

**Fewer repetitive student emails, because students get a correct answer from
the chatbot instead of emailing.**

The bot succeeds by *deflecting* questions that the source material already
answers, and by *safely escalating* the ones it doesn't — never by guessing.

---

## 3. Acceptance conditions

Grouped into three tiers. Tier A is non-negotiable and binary. Tier B is the
measurable quality bar. Tier C is the real-world outcome, measured at pilot.

### Tier A — Product behaviors (binary, must all pass)

These come straight from [CLAUDE.md](../CLAUDE.md) §1 and are pass/fail. A single
failure here blocks release regardless of metrics.

| ID  | Condition | How we verify |
|-----|-----------|---------------|
| A1  | Every answer is grounded in the retrieved source documents. The bot never answers from the LLM's general knowledge. | Eval set: answer-groundedness check on every golden question. |
| A2  | When the retrieved context does not contain the answer, the bot refuses gracefully and escalates to a human contact. It does not guess. | Eval set: `should_refuse` cases must all refuse. |
| A3  | Every answer cites its source (which document / section). | Automated check: citation field present and non-empty on every non-refusal answer. |
| A4  | Every answer carries a visible "AI-generated, verify with official sources" disclaimer. | Automated check on the response payload / widget render. |
| A5  | The bot stays scoped to internship questions and resists off-topic / jailbreak use ("write my essay"). | Eval set: adversarial/off-topic cases are refused. |

### Tier B — Quality gates (measured against the golden set, §4)

Two metrics kept strictly separate, per [CLAUDE.md](../CLAUDE.md) §4. Thresholds
below are **proposed starting targets** — we ratify or adjust them once the real
golden set exists; they are not guesses to ship blindly.

> **Note on the numbers.** There is no universal industry-standard value for
> these. The standard *practice* is baseline-first: measure the real golden set
> once, then set each target relative to that baseline and improve it. Until
> then these are directional placeholders. B3 (correct-refusal) is a **safety
> north-star** — treat any leak as a P0 bug rather than a number we expect to
> cleanly hit on a large set.

| ID  | Metric | Proposed target | Notes |
|-----|--------|-----------------|-------|
| B1  | **Retrieval recall@k** — is the correct chunk in the top-k retrieved? | `[CONFIRM] ≥ 0.90 recall@5` | Tuned independently of the LLM. This is the first thing we check when an answer is wrong. |
| B2  | **Answer correctness & grounding** — answer is correct and supported by retrieved context. | `[CONFIRM] ≥ 0.90` on answerable questions | Judged against `expected_answer_or_behavior`. |
| B3  | **Correct-refusal rate** — of questions the docs don't answer, how many did the bot correctly refuse? | `[CONFIRM] 100%` on the `should_refuse` set | A wrong eligibility answer can harm a student; we bias hard toward refusal. |
| B4  | **False-refusal rate** — answerable questions the bot wrongly refused. | `[CONFIRM] ≤ 10%` | Over-refusing kills usefulness; this guards against B3 being gamed by refusing everything. |

### Tier C — Pilot outcome (measured at Phase 11)

| ID  | Condition | How we verify | Depends on |
|-----|-----------|---------------|------------|
| C1  | Measurable drop in repetitive internship emails to professors during the pilot cohort. | Compare email volume vs. a pre-pilot baseline. | `[CONFIRM]` department provides a baseline + a target (e.g. "−X% over N weeks"). |
| C2  | Healthy deflection: a majority of asked questions are answered from the KB rather than escalated. | Deflection rate = answered / total, from the interaction log (§9). | Proxy we control even without C1's baseline. |
| C3  | The unanswered-questions log exists and is reviewed — it's the roadmap for what KB content to add next. | Log surfaced per §9. | — |

### Tier D — Operational / handover (from §3, §6, §10, §12)

| ID  | Condition |
|-----|-----------|
| D1  | Whole system stands up from `docker-compose up` with config via environment variables only — no secrets baked into the image. |
| D2  | Knowledge base rebuilds from source documents with **one command**. The vector store is never hand-edited. |
| D3  | Swapping the LLM provider is a one-file change (the provider abstraction). |
| D4  | The widget embeds on the AUB page as a single `<script>` tag. |
| D5  | Handover package exists: how to update content, redeploy, env vars, ownership. |
| D6  | Golden-set eval runs in CI; a metric regression can't merge silently. |

---

## 4. Open questions for the department

These block finalizing the numbers above. Tracked here so the monitor can see
what's provisional and why.

1. **Baseline email volume** — roughly how many internship emails/week does the
   course currently receive? Without this we can't measure C1.
2. **Target reduction & timeframe** — what drop, over how long, counts as
   success? (e.g. −50% over the first month of a term.)
3. **Pilot cohort** — which course section / how many students / which term?
4. **Go-live date** — is there a term deadline the pilot must hit?
5. **Escalation contact(s)** — who / what channel does a refusal point students
   to (email, form, office hours)? The bot needs a real endpoint to escalate to.
   Also: a **topic→owner map** (who owns which kind of question) if we later do
   smart escalation routing — see [backlog.md](backlog.md) B-1.
7. **Department-conditional rules** — which questions have different answers by
   department, and how is that marked in the source docs? See
   [backlog.md](backlog.md) B-2. We reserve a metadata field for this in Phase 4.
6. **Source material** — the actual guidelines / FAQ / forms, and ideally a
   batch of real past student questions for the golden set.

---

## 5. What "done" is NOT

To resist scope creep ([CLAUDE.md](../CLAUDE.md) §1, §7): done does **not** include
career-center features, student logins/accounts, analytics dashboards beyond the
interaction log, or multi-course support. Phase 1 is the internship course only.
