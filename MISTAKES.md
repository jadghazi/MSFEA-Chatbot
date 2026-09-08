# Failed approaches and debugging lessons

## 2026-09-08 — Synthesis and follow-up investigation

Evidence: `eval/synthesis_set.jsonl`, `eval/synthesis_protocol.md`, and the complete
traces/ratings under `eval/results/synthesis/`. These are experiments on this KB
and configured provider, not universal claims about RAG or Gemini.

- **Treating the first hybrid hit's cosine as the best evidence score.** RRF rank
  is not cosine order. “Explain the 6+2 arrangement” was blocked at 0.59 even with
  relevant evidence above 0.60 elsewhere in the same result set. Prompt/model
  changes cannot repair a request that never reaches generation. Evaluate the
  actual gate separately, including off-topic request savings.
- **A shorter task-first prompt alone.** Mean synthesis 3.00/5 vs baseline 3.09;
  the confirmation still became reporting instructions, and the documented
  fairness question falsely refused. Fewer tokens did not establish better answers.
- **Reducing k to 3 to remove distraction.** All-premise synthesis retrieval fell
  from 10/11 to 6/11, and an IAESTE topic switch lost its evidence. Do not trade
  away necessary premises to make generation appear more focused.
- **Increasing k to 12 alone.** Recovered the CO-OP waiver and 11/11 synthesis
  evidence coverage, but the summer-course answer incorrectly accepted 6+2 despite
  the ten-week rule. Additional context needs an answer method that preserves
  conditions; retrieval gain is not automatically an answer-quality gain.
- **Two-call fact selection then composition.** 22 successful provider requests
  instead of 11; synthesis 3.00/5. The selector retained unasked reports/forms and
  the composer repeated them. Extra calls without resolving the current intent
  do not solve extraction bias.
- **Temperature 0.4 instead of 0.0, seed unchanged.** All 12 answer texts were
  identical to the baseline, including its mistakes. Do not attribute intelligence
  or reliable variation to a temperature change without measurements.
- **Assuming a listed model is usable.** `gemini-2.5-flash` was listed but returned
  404 for generation. `model_swap` is incomplete and unscored, not a model-quality
  failure. The provider-directed `gemini-3.6-flash` trial retained the original
  1024-token budget and truncated three answers while still mishandling the
  confirmation. This rejects a drop-in swap under those constraints, not the
  model's capacity with a different reasoning/output budget.
- **Native system-role separation alone.** Moving the identical trusted policy
  to `system_instruction` still produced source dumps and misleading alternatives.
  Correct role separation is not evidence that the current intent is resolved.
- **Over-specific retrieval probes.** The initial comparison probe demanded one
  exact eight-week sentence although the Quick Reference supplied the same fact.
  Inspect missing premises individually. The audited report accepts `8 weeks`
  consistently across all saved runs; raw traces remain unchanged.
- **Potential experiment-state leakage.** A batch runner that mutates settings
  could carry temperature/model changes into the next trial. Fixed before those
  variants ran: every invocation resets from the control manifest; resuming checks
  exact manifest equality and skips only completed cases.

- **Structured resolved-question JSON.** The model labeled a confirmation as a
  request for requirements and repeated the same mistake in a different format.
  Mean synthesis 2.45/5; structure alone did not repair intent.
- **Universal source-free turn rewriting.** Improved confirmations but changed an
  unsupported WHY into an answerable confirmation, losing the correct refusal.
  Preserve the student's proposition and question type; do not universally rewrite.
- **A newline confound.** The first confirmation prototype also removed the final
  newline for unrelated questions. Responses changed despite no intended treatment.
  Version 2 preserves non-target prompt bytes; compare actual prompts, not intentions.
- **A generic WHY cue.** It falsely refused the documented fairness rationale.
  The selected combination excludes this cue; silence is not evidence of better grounding.
- **Combining all winners with fixed k=12.** Mean 4.00 but incorrectly accepted 6+2
  with another summer course. Adaptive depth (7 normally, 12 for explicit comparisons)
  retained comparison evidence and restored the ten-week conditional answer: 4.45.
- **Larger-model budget trial.** Raising the output cap to 4096 addressed truncation
  in the eight completed cases, but confirmations still rambled. The account's
  20-request daily quota stopped the run. It is incomplete and excluded from aggregate
  scores; this does not prove a stronger model cannot help with further tuning.
- **Running database tests in the evaluation container.** A final targeted test
  command accidentally used the demo DB rather than the dev overlay's test-db.
  Fixtures temporarily replaced the index during broader verification. Discarded
  that golden run, rebuilt all 206 chunks from source, and restarted verification.
  Always run pytest through the isolated dev Compose service, never this eval container.
- **A decision cue that said “apply the stated circumstances” without explicitly
  keeping source conditions attached.** It fixed the frozen summer-course case but
  a broader paraphrase mixed that ten-week rule into the ordinary 6+2 option. The
  original control answered correctly, so this was a real regression. Narrow the
  cue and test both sides of a condition boundary before release.

Retry a failed approach only with a new, explicit hypothesis and the same grounding
checks. A higher synthesis score does not excuse a fabricated or misapplied rule.
