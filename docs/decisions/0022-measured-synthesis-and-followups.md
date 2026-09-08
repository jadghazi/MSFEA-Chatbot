# ADR-0022: Direct answers and confirmation follow-ups

Status: accepted.
Date: 2026-09-08

The pilot sometimes refused “Explain the 6+2 arrangement” while answering “What
is…” and interpreted “so 2 weeks of research” as a request for forms and reports.
The existing prompt already asked for intent-aware reasoning; another plausible
prompt alone was insufficient.

Before editing production, froze 12 synthetic cases with expected answer qualities,
including comparisons, conditional decisions, topic switches, confirmations and an
undocumented WHY. Full prompts, retrieved chunks, outputs and manual scores are in
`eval/results/synthesis/`. The coding assistant reviewed synthesis and grounding
separately; these are small-set measurements, not independent human evaluation.

## Decision

- Use the maximum retrieved cosine for the 0.60 gate. Hybrid RRF rank is not
  cosine order; the first result incorrectly blocked an otherwise supported question.
- Keep k=7 for normal questions; explicit comparisons use at least 12 to recover
  cross-program conditions. An explicitly supplied k still controls experiments.
- Frame explicit conversational confirmations as checks of the student's original
  proposition. Add short task cues after evidence for confirmations, definitions,
  comparisons and conditional decisions. They contain no CDC facts or topic list.
- Preserve the current Gemini model, temperature, chunking and one generation call.
- Bound provider requests to 30 seconds without SDK retries and reject truncated
  or empty responses through the existing temporary-unavailability path.

The final combination scores 4.64/5 vs 3.09 on the 11 answerable cases, with
zero observed unsupported answers or false refusals (baseline: two and one).
All-premise retrieval rises from 10/11 to 11/11. A precursor repeat produced
identical answer text, citations and refusal behavior for all 12 cases. The final
production prompts were then rerun after a broad-set condition-boundary regression
was found and corrected.

## Tradeoffs and limitations

Total input tokens rise from 25,572 to 29,163, including one extra question now
reaching generation. The max-score gate skips 11/20 off-topic calls vs 14/20
previously; the generation refusal remains essential. All 109 valid calibration
queries pass. No chunk/index format or external service was added.

Definitions still sometimes include one unasked report detail. The fairness answer
does not fully connect its rationale to the student's wait-time concern. The model
swap was constrained by output budget and a daily quota; it is not a verdict on
the alternative model's general reasoning capacity. Latency measurements were
collected at different times and should not be interpreted as causal speed gains.

## Reproduction

`python -m eval.synthesis_eval --variant baseline --name baseline_recheck`

`python -m eval.synthesis_eval --variant combined_adaptive --name candidate_recheck`

Run against the source-built demo index, with configured provider credentials.
Review actual outputs and grounding, then update ratings and run
`python -m eval.synthesis_report`. CI runs the synthesis retrieval/gate checks;
live answer reviews remain explicit because they consume provider quota.
Run database-mutating pytest only with the dev Compose overlay's isolated test-db.
