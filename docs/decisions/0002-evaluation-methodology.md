# ADR-0002 — Evaluation methodology: layered hybrid

**Status:** Accepted
**Date:** 2026-07-20
**Decision owner:** Jad Ghazi

## Context

We need to grade "is an answer correct and safe?" both offline (the Phase 2
evaluation harness, [CLAUDE.md](../../CLAUDE.md) §4) and online once deployed
(Phase 9 observability). The naive options each fail on their own:

- **Exact / keyword matching (BLEU/ROUGE/F1):** simple and free, but brittle —
  it punishes correct answers that are worded differently. Production
  assistant-style bots have largely abandoned it for open-ended answers.
- **A single vague "is this good?" LLM-judge call:** flexible but unreliable and
  unauditable — one fuzzy verdict hides *why* an answer failed.

Real deployed RAG systems don't pick one method; they **layer** several, which
also matches this project's need to separate retrieval failures from generation
failures and to keep the safety-critical behaviors deterministic.

## Options considered

1. Exact/keyword matching only — rejected (brittle, obsolete for this use).
2. Single LLM-judge only — rejected (unreliable, not decomposable, no free
   deterministic guarantee on safety behaviors).
3. **Layered hybrid** — deterministic checks + decomposed LLM-judge + human
   calibration + production feedback. Chosen.

## Decision

Adopt the layered hybrid used by production RAG teams (RAGAS / DeepEval /
LangSmith-style). Four layers:

**Layer 1 — Deterministic checks (free, no LLM).** Plain-code, pass/fail checks
for the mechanical Tier-A behaviors: did it refuse when `should_refuse` is true?
is a citation present? is the disclaimer present? is it within length limits?
These never use an LLM call and never give a flaky verdict.

**Layer 2 — Decomposed LLM-as-judge (semantic correctness).** Break "correct"
into separately-scored sub-metrics rather than one vague score:
- **Faithfulness / groundedness** — is every claim supported by the *retrieved
  context*? This is reference-free (grades against retrieved docs, not a
  hand-written golden answer) and directly measures our #1 requirement:
  no hallucination.
- **Answer relevance** — does the answer actually address the question?
The judge may be a cheaper/smaller model than the bot itself.

**Layer 3 — Human calibration (the anchor).** Hand-label a small sample
(~30–50 answers) as correct/incorrect and confirm the LLM judge agrees with the
humans (target high agreement, e.g. ~90%+). Humans are ground truth; the LLM
judge is a *scalable approximation* we only trust once calibrated. Re-check when
the judge model or prompt changes.

**Layer 4 — Production feedback (online, post-deploy).** Real-world signals once
live: per-answer 👍/👎 ratings, escalation rate, deflection rate, and the
unanswered-questions log.
> **Important — how feedback improves the bot.** Ratings do **not** retrain the
> model automatically. They produce a **signal for a human** to fix the
> underlying cause — update/add source content, fix retrieval, or adjust the
> prompt. The loop is human-in-the-loop by design: we never want the bot
> "learning" unofficial facts from user input. It must stay grounded in official
> docs.

## Consequences

- **Phase mapping.** Layers 1–3 are the offline harness built in Phase 2
  (structure now on placeholder questions; Layer 2 judge wired once the LLM
  provider + real questions exist). Layer 4 is built in Phase 9 (observability)
  and surfaced to admins per [backlog.md](../backlog.md) B-3.
- **Cost.** Only Layer 2 spends tokens, and only on occasional eval runs over
  ~50–100 questions — cents, not a live-traffic cost. Cheap enough for a solo
  student.
- **Separation preserved.** Retrieval metric (recall@k) stays independent of all
  of the above, so a wrong answer is still diagnosed as retrieval-vs-generation
  first ([CLAUDE.md](../../CLAUDE.md) §2, §4).
- **What we watch.** If the LLM judge drifts from human labels, Layer 3 catches
  it; we fix the rubric before trusting Layer 2 again.
