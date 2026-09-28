# Six-week internship answer correction — 28 September 2026

## Incident and diagnosis

Oracle interactions 309–317 reproduced the report across departments. MECH
interactions 311 and 317 matched the screenshot: the approved research option was
retrieved first, but the answer omitted it and incorrectly used the prohibition
on two four-week company placements as the reason six weeks alone was insufficient.
CHEM interactions 309 and 313 used `6weeks`; the relevant departmental condition
was absent, while the spaced question retrieved it. ECE interaction 310 retrieved
a dedicated six-weeks-alone FAQ and gave the completion routes.

These were two different failures, not missing faculty decisions:

1. Joined quantities changed embedding/keyword candidates and bypassed the numeric
   decision candidate-pool expansion. Department filtering could not recover a
   rule absent from the candidate pool.
2. The `Can I do` task cue overemphasized binary rejection of the exact plan.
   The MECH research FAQ also placed a separate 4+4 restriction next to the
   six-plus-two rule, inviting an unsupported causal connection.

## Changes

- Normalize joined numeric quantities and units before both retrieval paths and
  numeric-intent detection. Preserve the original question for generation and
  logs; preserve identifiers and course codes.
- Require decision answers to distinguish partial participation from full
  completion, explain the closest documented completion option, and attach
  approval conditions. Retain the requirement for explicit source support for
  combining unlike components.
- Clarify the MECH research FAQ: six company weeks alone are short of the ordinary
  eight-week minimum; six company weeks plus two approved hands-on faculty-research
  weeks may count. Keep the 4+4 ban in a separate FAQ and the existing departmental guideline.
- Restate CEE's existing six-week exception and Chair-approval condition in a
  dedicated duration FAQ, so unrelated split/consulting rules do not dominate it.
- Clarify CHEM's existing research approval and eight-week minimum together;
  splitting within one summer is not a reduced-duration exception.
- Allow conditional answers for sufficiency questions when the source makes the
  duration conditional on course-team confirmation; do not turn “may require”
  into an unconditional rejection.
- Add 20 regression cases: ECE, IEM, MECH, CHEM, CEE, each with spaced digits,
  joined digits, spelled-out duration, and an explicit “only” question. Their
  evidence/context checks run in the existing CI synthesis gate.

No policy, provider, model, similarity threshold, or retrieval depth is changed.
The revised normalized wording is traceable to the existing approved FAQ source
record. Ingestion rebuilds the index from the canonical files.

## Validation method

Validation uses an isolated Oracle database, never the student-serving index.
The baseline is commit d1a7b2a. Evidence coverage is measured separately from
manually reviewed answer correctness. CEE evidence probes accept either existing
wording of the selected-company exception; a particular spelling of six is not
itself a policy requirement. Baseline coverage was rescored against the same
final probes.

The first prompt-only candidate still made the MECH causal error. It was rejected;
its partial answers are diagnostic evidence, not final validation results.

Reproduce retrieval checks with `python -m eval.synthesis_gate` after ingestion.
Reproduce the generated-answer review with the existing harness:

```sh
python -m eval.synthesis_eval --variant production_final \
  --cases eval/six_week_live_regression.jsonl --name six_week_live --delay 7
```

Assess actual answers against each case's expected behavior, including department
conditions, absence of the unrelated 4+4 rationale, grounded citations, and correct
handling of standalone six weeks versus an approved completion route. Citation
presence alone is not answer correctness. Provider timeouts are operational
failures and are recorded separately.

A legacy retrieval test assumed an unscoped top-five ranking must contain multiple
departments. That ranking is not a scope contract and changed with the cleaned
FAQ. The test still requires the selected department, general guidance, and no
other department; the multi-department evidence requirement remains enforced by
the synthesis/publication gates. The prompt-contract assertion now checks the
revised equivalent prohibition and explicit completion/approval instructions.

## Final validation

- Same-probe evidence coverage: **17/20 before, 20/20 after**. The original
  full-sentence CHEM probe was adjusted to its equivalent factual terms after
  the FAQ wording changed; all required duration/research/Chair-approval facts
  remain tested. This does not convert a missing fact into a pass.
- Production-depth golden context recall: **118/121 (97.5%)**, unchanged.
- Synthesis evidence + model context + threshold: **67/67**, including all
  20 new cases. Publication/scope: **9/9**. Conflict coverage: **7/7**.
- Threshold calibration: **162/162** valid questions accepted; **12/20**
  off-topic questions blocked before generation. Threshold remains 0.60.
- **301 tests passed**; lint and strict type-checking passed. An initial partial
  test checkout omitted frontend/workflow assets, and a source edit invalidated
  an in-progress publication fixture. The complete, stable checkout passed.
- Reviewed **40 final generated responses**: 20 main cases, 14 existing controls,
  and six repeated MECH/CHEM/CEE cases. All 38 answerable responses had citations;
  the two unsupported questions refused correctly; all 40 had AI disclaimers.
  Core department-specific completion/exception guidance is preserved. Some
  replies still include extra detail; this is not a perfect-style rating or a
  full golden-set answer-accuracy measurement.
- One baseline request exhausted provider retries with a service error; it is
  retained as an operational failure. Final requests completed, including
  automatic retries for transient provider timeouts.
- The reproducible normalized index contains **225 chunks**. No active curated
  revisions existed on the live instance at the pre-deployment check.

The compact before/after answers, retrieved source labels, evidence checks, runtime
settings, source hashes, and review notes are in
`eval/results/six_week_fix_20260928.json`.
