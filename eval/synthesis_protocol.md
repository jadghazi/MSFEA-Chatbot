# Synthesis experiment protocol — 2026-09-08

Frozen before baseline or application changes. Twelve synthetic cases drawn from
the official normalized KB and the user's three-turn screenshot. Expected answer
qualities are semantic criteria, not target strings. Fixed histories isolate each
follow-up; final validation must also use actual answers in an evolving conversation.

## Scoring

Score each actual response against its current question and expected qualities:

1. Misses the intent, falsely refuses, or gives a misleading answer.
2. Mostly restates nearby material; leaves the conclusion/comparison to the student.
3. Relevant but incomplete synthesis, or answers then adds distracting material.
4. Direct, supported conclusion/comparison with only minor unnecessary detail.
5. Precisely resolves the current intent, combines all required premises, and adds
   no irrelevant content. Correct supported refusals score 5 on intent handling;
   report the answerable-only synthesis mean separately to avoid inflating it.

Grade grounding separately: supported / unsupported / incomplete. Unsupported
means any material invented policy, condition, causal rationale, or false inference;
incomplete means missing required facts, not hallucination. Also check each displayed
citation against the claims (a valid label alone is not proof), refusal, disclaimer,
all-premise retrieval recall, output length, provider latency and request/token cost.
Scores are evaluator judgments by the coding assistant with written rationales;
they are not independent human ratings or a calibrated external LLM judge.

## Candidates (one major variable each)

- Baseline: existing ADR-0021 prompt, configured model/decoding, k=7, unchanged KB.
- Task-first prompt: shorter evidence/task separation and explicit comparison and
  causal-boundary guidance. Hypothesis: fewer competing prose instructions improve
  directness. Risk: losing completeness or conservative refusal behavior.
- k=3: less distracting evidence. Risk: missing multi-hop premises.
- k=12: more evidence coverage. Risk: more copying, tokens and conflicting rules.
- Two calls: first select relevant facts (not hidden reasoning), then compose from
  original context plus the untrusted fact outline. Risk: latency/quota and propagation
  of an incorrect intermediate statement.
- Temperature 0.4: same prompt/model/seed. Hypothesis: less rigid extraction; risk:
  less repeatability and weaker grounding.
- Model swap: same prompt/context/decoding with another available Gemini model.
  Hypothesis: capacity improves synthesis; risk: quota, latency and truncation.

Inspect current chunk boundaries first. Existing Q&A units and atomic tables should
not be rechunked without evidence that required reasoning units are being lost.
Log actual failures and missing premises, not just document-level hits.

Run all candidates on these same cases; only then combine compatible winners and
repeat. Save prompts, retrieved text, actual raw/parsed answers, settings and hashes.
No student logs are read or used. Direct pipeline runs avoid polluting pilot metrics.
Provider outages are operational failures and cannot be counted as quality scores.
After selection, run the existing golden-set checks plus live chained follow-ups.
No Git commit/push or Oracle deployment is part of this task.

## Adaptive hypothesis discovered during baseline

The exact `Explain the 6+2 arrangement` case is blocked before generation: the
first RRF-ranked chunk has cosine <0.60, while another supplied chunk is >0.60.
Add a seventh diagnostic candidate, `max_gate`: keep all ranks, text and the 0.60
threshold, but use the maximum candidate cosine to decide whether evidence exists.
Recalibrate on the complete existing threshold set before accepting this change.
This is a retrieval/gate fix; a prompt or model cannot fix a call that never happens.

Metric annotation: s06's original eight-week evidence substring is too specific:
the Quick Reference and FAQ also supply that fact. Preserve raw evidence hits, but
use `8 weeks` for this premise when reporting audited all-premise recall across
all variants. This does not change expected answers, questions, or LLM inputs.
The first aggregate retrieval audit consequently marked s06 incomplete at k=12.
Inspecting the saved chunks shows k=12 DOES retrieve the waiver and eight-week rule.
Adjacent-window expansion was considered but not selected for testing: increasing
depth already recovers the required evidence without an added retrieval mechanism.

## Additional structural hypothesis after negative prompt/chain results

`native_system`: the current provider sends all instructions, evidence and the
question as a single user `contents` string. Move the exact same trusted policy
prefix to Gemini's native `system_instruction`; leave department, history,
retrieved blocks and current question as user data. No instruction text, retrieval,
model or decoding changes. Test whether role separation improves adherence before
adding more wording or changing the production provider contract.

`structured`: native role separation still source-dumps on the confirmation.
Test an explicit single-call response contract with a short `resolved_question`
field followed by `answer`, `sources`, and `refused`. This is a task interpretation,
not chain-of-thought or generated KB facts. The student sees only the answer.
Schema constraints test whether making intent resolution observable works where
silent planning did not. Keep original model, retrieval, history and sampling.

`resolve_turn`: the structured trace incorrectly turns the tentative research
confirmation into a request for requirements/details. Test a source-independent
interpretation pass using only the current message and bounded conversation,
followed by the original grounded answer prompt with that clarified question.
Keep retrieval on the original query so the only changed layer is generation task
interpretation. A fictional conversational example teaches confirmation, with no
new CDC policy facts. This costs two calls; assess whether the gain warrants it.

`model_budget`: compare against `model_current`, changing only its output budget
from 1024 to 4096. The initial current-model trial consumed its budget on three
incomplete answers. This follow-up separates a poor drop-in configuration from
the model's ability when allowed enough reasoning/output tokens. Keep k=7, the
original prompt, model `gemini-3.6-flash`, seed and temperature unchanged.

`confirmation_frame`: the source-independent interpreter fixes both terse
follow-ups but wrongly rewrites a why question into confirmation, losing refusal.
Test a narrower deterministic alternative: only explicit conversational restatements
beginning with “so”, “in other words”, or “just to confirm”, with prior user history,
are framed as “Is my understanding of our conversation correct: ...?”. Preserve the
student's words. Never rewrite complete why/how/auxiliary questions. No LLM rewrite,
no added policy facts, and no changed retrieval. Test all twelve cases unchanged.

`task_contract`: test source-independent response-mode cues placed AFTER the
evidence/current question, including the confirmation framing above. Modes are
generic language intents (confirmation, definition, comparison, why, decision),
not CDC topics or encoded policy answers. Unmatched questions remain byte-for-byte
unchanged. This is one generation-prompt intervention at baseline k/model/gate;
the cue makes the current task explicit instead of asking for silent classification
after reading FAQ-shaped evidence. Check lists and links later on the full golden set.

## Combined test

Combine k=12 (recovered all synthesis premises), the max-cosine 0.60 gate (fixed
Explain's false refusal), and the task-contract confirmation/definition/comparison/
decision cues. Exclude the `Reason` cue: it falsely refused the documented fairness
rationale, so why questions retain the original behavior. Keep the original Lite
model, temperature 0, seed 42, 1024 cap and one provider call. Repeat this combination
before accepting it; do not assume component gains are additive.

The fixed-k=12 combination still misapplies the summer-course condition. Test
`combined_adaptive` against `combined`, changing only depth selection: baseline
seven except for explicit compare/comparison/difference/versus/vs questions, which
get twelve. This is a generic query-structure cue, not a list of CDC programs.
Repeat and validate on the full golden set before promotion.
