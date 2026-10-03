# Evaluation: datasets, gates and answer review

Current navigation reviewed 2026-10-03. Start with
[AGENTS.md](../AGENTS.md) and [architecture](../docs/architecture.md).
The harness separates retrieval evidence from answer correctness; grading rationale
is in [ADR-0002](../docs/decisions/0002-evaluation-methodology.md).
Current deterministic commands are defined in
[CI](../.github/workflows/ci.yml). Run them on isolated databases through
[the development workflow](../docs/development.md), never against the serving index.

Dated result reviews below retain their original measurements and limitations.
They are not live scorecards. See [faculty evaluation](results/faculty_evaluation_report_20260929.md),
[conversation routing review](results/conversation_dual_path_review_20260930.md) and
[October rollout gates](../docs/archive/oracle-studio-deployment-20261001.md)
for the applicable recorded runs. Provider errors/retries and judge uncertainty
must remain visible; independent human answer calibration is still pending.

## Contents

- `golden_set.jsonl` — one case per line: `question`,
  `expected_answer_or_behavior`, `source_doc`, `should_refuse`, plus helpers
  (`id`, `source_section`, `history`, `tags`, `is_synthetic`). `history` is optional
  and holds bounded earlier turns for follow-up/topic-switch cases. Seeded from the real CDC-KB
  FAQs plus refusal cases; `is_synthetic: true` marks questions we predicted
  (placeholders until real student questions arrive).
  It also includes intent-aware conversational cases for confirmations, topic
  switches, and applying documented thresholds to facts stated by a student.
- `faculty_questions_golden.jsonl` — a separate, frozen set of the 177 anonymized
  question/approved-answer pairs in the 2026-09-26 faculty workbook, expanded to
  205 department-scoped cases for seven rules whose answers vary by department.
  Original wording and workbook cells are retained. `build_faculty_golden.py`
  regenerates it from the reviewed workbook, committed
  `docs/intake/faq-workbook-classification-2026-09-26.md`, and intake record; later owner
  decisions are recorded as resolved expectations alongside original answers.
  The source workbook SHA-256 is checked before regeneration. This source set is
  distinct from the synthetic edge-case set above.
- `faculty_retrieval_gate.py` — CI checks whether a source document identified in
  the frozen intake review appears among the top-seven retrieved chunks for
  answerable cases. The current faculty set has no pure-refusal case; refusal
  edge cases remain in the original golden set.
  This is a document-level floor, not proof that the correct policy passage was
  retrieved; answer and evidence review remains separate.
- `faculty_live_eval.py`, `faculty_judge.py`, and `faculty_report.py` — resumable
  Oracle answer traces, decomposed policy-evidence and answer judgments, and denominator-aware
  reporting. The judge may group two cases per Gemini request to conserve the shared
  daily quota, but a multi-case response must carry matching case IDs; otherwise it
  is rejected rather than paired by position. Use `--batch-size 1` for consequential
  comparisons. Answer and judge runs stop when quota is exhausted and can resume
  after reset. Judge ratings require independent human calibration against source
  passages before being used as a trusted answer-accuracy claim.
  Provider errors and uncertain judgments stay visible rather than counting as correct.
- `faculty_calibration_sample.jsonl` — 48 source-review cases: eight per department
  with high-risk policy questions deliberately overrepresented, plus eight
  rubric-challenge cases. It checks judge agreement and is not a random estimate
  of full-set accuracy. Labels in `results/faculty_calibration_labels_20260928.jsonl`
  are Codex source reviews, not independent human calibration.
- `loader.py` — parse + validate the golden set (`load_golden_set()`).
- `metrics.py` — the two metric families:
  - **Retrieval:** `recall_at_k`, `hit_rate_at_k`.
  - **Answer, Layer 1 (deterministic):** `refusal_is_correct`, `citation_present`,
    `disclaimer_present`.
- `run.py` — `python -m eval.run` summarizes the set and reports metric status.
- `threshold_set.jsonl` + `threshold_eval.py` — retrieval-only calibration for the
  pre-LLM similarity gate. It includes terse/misspelled valid questions and varied
  off-topic prompts, runs without an API key, and is gated in CI (ADR-0020).
- `publication_guard_baseline_set.jsonl` — the frozen pre-publication-guard answer
  preservation sample across all departments, unknown department, follow-ups,
  comparison, topic switching, and refusal. The reviewed baseline and raw traces are
  documented in `docs/archive/kb-publication-guard-baseline.md` and
  `results/publication_guard/`.
- `scope_regression_set.jsonl` — independently source-grounded department,
  condition-boundary, paraphrase, and follow-up cases added by publication-guard
  Step 1. The synthesis gate runs these without replacing the older sets.
- `publication_guard_gate.py` — gates the frozen all-department/unknown/follow-up
  preservation sample and prints per-department results.
- `conflict_review_set.jsonl` + `conflict_gate.py` — independently measure review
  candidate coverage and report heuristic false-positive flags.
- `answer_quality_focus.jsonl` — small frozen set for ordinary wording, course versus
  report duration, follow-ups, conditions, topic switches, and refusal. CI's
  `synthesis_gate.py` checks every required phrase in retrieved chunks and in the
  exact context built for the model. `answer_quality_holdout.jsonl`,
  `answer_quality_unseen.jsonl`, and `answer_quality_final_holdout.jsonl` record
  later validation probes.
- `six_week_policy_set.jsonl` — distinguishes the ordinary ECE eight-week rule,
  approved 6+2 research, two-company approval, and the ten-week exception when
  taking another summer course. The synthesis gate checks that each case's
  required evidence reaches the model; live answers still need semantic review.
- `faculty_quality_holdout.jsonl` and `faculty_quality_validation.jsonl` — small
  synthetic paraphrase sets for staged live-answer checks across departments,
  conditions, source selection, and refusals. The first set exposed missing
  grading and professional-skills evidence and became diagnostic; the second was
  run after those changes. Neither replaces the 205 actual faculty questions.

## What is wired vs. pending

| Piece | Status |
|-------|--------|
| Golden set + loader | Ready |
| Answer Layer 1 (deterministic checks) | Ready, unit-tested (`python -m eval.answer_eval`) |
| Retrieval recall@k + context-recall | Ready (`python -m eval.retrieval_eval`); **gated in CI** on a context-recall floor |
| Similarity-threshold calibration | Ready (`python -m eval.threshold_eval`); **gated in CI**, no LLM calls |
| Answer Layer 2 (LLM-judge: faithfulness/groundedness) | The faculty-question pass uses `faculty_judge.py` to rate policy correctness, conditions, cited grounding, relevance, and refusals separately. Its results remain provisional pending independent human calibration. |
| Answer Layer 3 (human calibration) | Source review by Codex is recorded for a 48-case sample; independent human calibration remains pending. |

The answer eval is deliberately **not** in CI: it calls the live LLM, so it needs an
API key and burns free-tier quota. Run it locally before/after a change that could
affect generation.

For the focused live set, run `python -m eval.followup_eval --cases
eval/answer_quality_focus.jsonl --output eval/results/focused.jsonl --delay 7` against
an isolated, ingested database. Review the actual answers against cited passages;
`evidence_hits`, `context_hits`, citation presence, and refusal flags alone do not
establish semantic correctness. See `answer_quality_review.md` for the local review.

## Run it

```bash
python -m eval.run     # summarize the golden set
python -m eval.threshold_eval  # verify the pre-LLM 0.60 gate; no Gemini usage
python -m eval.build_faculty_golden path/to/RAG_FAQ_Questions_Answers_Updated.xlsx
pytest                 # run metric + golden-set tests
```

The faculty workbook questions are now versioned in `faculty_questions_golden.jsonl`.
Future independently sourced student questions can be added with source review;
the original `golden_set.jsonl` remains useful for synthetic edge-case coverage.
