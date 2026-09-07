# ADR-0021 — Intent-aware grounded answer planning in one LLM call

**Status:** Accepted
**Date:** 2026-09-07
**Decision owner:** Jad Ghazi

## Context

Live traces showed that retrieval could return the correct evidence while generation
still produced a weak answer. In the ECE 6+2 example, Gemini mixed in an adjacent
four-week rule that applied to a different situation. On the follow-up, “So the two
weeks are research?”, it answered the surrounding topic by listing reports and forms
instead of confirming the student's interpretation.

The pilot also needs to conserve Gemini free-tier quota. Adding a separate LLM query
rewrite, classifier, or answer-planning request would multiply requests and add latency.
Reducing `top_k` would remove distracting blocks but regress the measured retrieval
recall that justified `top_k=7`.

## Options considered

1. **Reduce retrieval depth.** Less context, but known context recall falls and the
   retrieval layer is not the observed failure.
2. **Add a second LLM planning or query-rewrite call.** More explicit control, but
   nearly doubles requests and latency for every turn.
3. **Add intent and evidence planning to the existing generation call.** Preserve one
   provider call and retrieval recall while instructing the model to reason over only
   the minimum relevant premises.
4. **Fine-tune a model.** Disproportionate for a small pilot and unsupported by the
   current data volume.

## Decision

Use option 3. Before emitting an answer, the existing prompt makes Gemini silently:

- resolve the current turn and classify its intent;
- select the smallest directly supporting evidence set;
- keep rules attached to their program, department, and conditions;
- apply explicit KB rules to facts stated by the student using basic logic or
  arithmetic; and
- verify that every output claim follows from the selected evidence.

Confirmation/correction turns must begin directly and must not volunteer forms,
reports, or deadlines unless needed for accuracy. Rule-application answers are
conditional on student-stated facts because the bot cannot verify student records.
Usually one citation is expected and two are allowed only when the conclusion combines
both sources.

The citation parser also accepts Gemini's observed two-line format (`SOURCES:` followed
by labels). If Gemini omits a usable source marker entirely, a deterministic fallback
selects the supplied block with the strongest answer-fact overlap (with extra weight
for exact numbers) instead of displaying all seven retrieval candidates. This costs no
second provider request and cannot invent a source outside the retrieved context.

## Consequences

- The production flow remains retrieve → one Gemini call → validate citations.
- Five live cases covered confirmation, two rule applications, an incomplete
  arrangement, and a topic switch; all gave the intended direct conclusion. The four
  added reasoning cases achieved context-recall@7 4/4 (100%).
- Measured calls used 2,416–2,589 input tokens, 26–80 output tokens, and 0.86–1.95
  seconds of Gemini latency. The planning instructions add prompt tokens but no request.
- Four versioned golden cases now preserve these behaviors. Retrieval and answer
  quality remain separate: prompt tuning cannot excuse missing evidence.
- This is still bounded grounded synthesis, not permission to use outside knowledge or
  expose chain-of-thought.
