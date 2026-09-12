# ADR-0024: Improve follow-up synthesis without changing the pilot model

**Status:** Accepted

**Date:** 2026-09-12

## Context

For an ECE student asking whether six internship weeks are enough, production
retrieval often omitted the passage defining the 6+2 option and included the
separate ten-week exception for students taking another summer course. The model
then repeated nearby facts, introduced unasked reporting instructions, or carried
the wrong ten-week premise into a follow-up. The prompt also explicitly requested
the repetitive opening `For ECE students`.

The Oracle pilot uses `gemini-flash-lite-latest` because its quota and latency are
better suited to concurrent student use. `gemini-3.6-flash` with low reasoning was
evaluated and produced strong answers, but its observed free-tier limit was only
5 requests per minute and its calls were slower. That is a poor pilot default.

## Decision

- Retain `gemini-flash-lite-latest`; do not change the deployed model or add a
  second model call per student turn.
- Include the already-selected department abbreviation in semantic ranking while
  retaining the original question vector for the calibrated similarity gate.
- Split the 6+2 definition from its reporting procedures in the normalized source,
  so retrieval can provide the answer without forcing unrelated instructions into
  the same evidence block.
- Treat previous assistant messages as fallible context and answer `what about`
  follow-ups as corrections or alternative options.
- Filter procedural side passages from option-focused follow-ups and condition-only
  passages from ordinary sufficiency questions when the student has not stated that
  condition. Retrieval and logging retain the full candidate list.
- Address a student naturally as `you`; name their department only when a real
  department comparison makes it relevant.

## Measurement

A frozen seven-case set covers the reported two-turn conversation, paraphrases,
confirmation, the distinct summer-course condition, and an unsupported-rationale
refusal. Deterministic answer checks improved from **1/7** at baseline to **7/7**
with Flash Lite. Required retrieval-evidence hits improved from **6/11** to
**11/11**. The complete synthesis retrieval gate and project test suite remain
release requirements.

## Consequences

Department-aware ranking adds one local embedding call, not an LLM call, so it does
not consume Gemini quota. Section filtering is deliberately narrow and driven by
the current task and source headings. New conditional headings and follow-up forms
must be represented in the evaluation set before this logic is broadened.
