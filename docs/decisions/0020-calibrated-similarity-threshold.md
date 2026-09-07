# ADR-0020 — Calibrated pre-LLM similarity threshold of 0.60

**Status:** Accepted
**Date:** 2026-09-07
**Decision owner:** Jad Ghazi

## Context

The answer pipeline already had a cosine-score gate before Gemini, but it remained
disabled at `SIMILARITY_THRESHOLD=0.0` because no score distribution had been
measured. Guessing a threshold could refuse legitimate student questions. The KB and
golden set are now large enough to establish a pilot baseline, and avoiding obviously
off-topic Gemini calls preserves free-tier quota.

The production gate uses the cosine score attached to the first hybrid/RRF-ranked
chunk. Calibration therefore measured that exact value rather than a different pure
semantic score. The persisted set contains all 64 answerable golden questions, 30
additional terse or misspelled valid questions, and 20 varied off-topic prompts.

## Options considered

1. **Keep 0.0 (disabled).** No false refusals, but every unrelated question consumes
   Gemini quota.
2. **Use 0.50.** Safe on the measured valid set, but blocked only 4/20 off-topic
   prompts and provided little quota protection.
3. **Use 0.60.** Kept all 94 valid queries above the gate and blocked 14/20 off-topic
   prompts. The lowest measured valid score was 0.6329.
4. **Use 0.65.** Blocked more unrelated prompts but falsely refused two misspelled,
   valid internship questions. Rejected.

## Decision

Set the default and pilot environment to **0.60**. A score strictly below 0.60 returns
the normal grounded escalation without calling the LLM. Keep the prompt-based
`INSUFFICIENT_CONTEXT` refusal because topical but unanswerable questions—such as a
specific company's approval status—can have high similarity scores.

Version the supplemental calibration cases separately from the golden answer set so
running the threshold evaluation never invokes Gemini. CI rebuilds the index and runs
`python -m eval.threshold_eval` after the normal retrieval evaluation.

## Consequences

- The pilot avoids an LLM call for 70% of the varied off-topic stress set with zero
  measured false refusals across 94 valid queries.
- Prompt injection and some generic/off-topic text can still score above 0.60; the
  existing prompt refusal remains the second guardrail.
- The score depends on the KB, embedding model, and retrieval ordering. Any change to
  those must pass the threshold evaluation; pilot logs should still be reviewed for
  false refusals from real student language.
