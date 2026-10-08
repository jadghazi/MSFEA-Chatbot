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

### Student-intent quality audit

The [main-model verification report](results/student_quality_main_model_20261007.md)
continues the dated audit using the configured student model. The frozen
`student_quality_timeline_holdout.jsonl` and `student_quality_transfer_holdout.jsonl`
add timeline association, hypothetical arithmetic versus approval, actor-versus-goal
attributes, explicit topic changes and report requirements. Expectations precede
live answers and do not change to accommodate the candidate.

`student_quality_dialogue_set.jsonl` contains three conversations (20 turns).
`python -m eval.student_quality_dialogue_eval --live --output <new-jsonl-path>`
retrieves from an isolated development database and passes each actual generated
reply to the next turn. It records exact prompt/context, ordered passages, resolved
query, dataset hash and stable index generation. This tests propagation through
real history; replaying canned histories is a separate diagnostic. Run one live
worker at a time, retaining failed attempts and exact-prompt reuse lineage.
The earlier Lite-model acceptance was interrupted by a provider daily-quota failure.
The [paid migration report](results/student_quality_paid_migration_20261008.md)
records the replacement candidate and its separately verified answer evidence.
A fresh main-model answer is
needed when any full prompt changes, even if an earlier answer still looks correct.
For actual-history reuse, every preceding turn must also match the current prompt;
one individual matching prompt does not certify the rest of its conversation.

`student_quality_history_task_holdout.jsonl` adds three two-turn controls for
replacement, a documented positive waiver and relationships between distinct
programs. These expectations were frozen before live answers after an
actual-history failure showed that an earlier request could replace the current
task. They are constructed transfer probes, not independent student sampling.

Fresh audit/dialogue retrieval now rejects an index whose generation does not
match normalized inputs plus active approved immutable revisions, and checks the
generation throughout the run. Do not rebuild during evaluation. Explicit frozen
retrieval replay remains available for controlled generation comparisons and must
be identified as replay rather than a fresh retrieval measurement.

The completion candidate adds `student_quality_failure_classes_set.jsonl` (30
frozen probes across scoped conditions, attributes, process stage, spelling and
topic switches) and `student_quality_comparative_validation_set.jsonl` (four
minimum/maximum/length probes). `student_quality_completion_set.jsonl` concatenates
these with the existing 80 cases. No original expected answer is changed. Q47's
generic template phrase conflicts with its ECE override and remains excluded from
phrase metrics; its answer is reviewed against the controlling source.

Audit traces record original/resolved queries, supplemental spelling queries,
primary and companion scores/roles, final context and exact provider prompt.
Companions are appended after seed retrieval, so a full-context evidence hit is
not a top-seven seed hit. Report them separately. Verify the 114 paired traces and
current prompt using `python -m eval.student_quality_finalize --completion`.
If provider quota interrupts verification, `--completion --partial` emits an
explicitly incomplete manifest with missing IDs and verifies successful live
traces plus deterministic local replies without making provider calls. It never
substitutes an earlier candidate's answers. The [completion report](results/student_quality_completion_20261007.md)
identifies the accepted final artifacts and pending verification. Final live
attempts historically used `--delay 12` (five calls/minute); budget diagnostics/retries too and
stop on daily-quota errors. `--resume` retries failed rows, retaining prior errors.
Failures and interim trials remain retained; phrase hits and citations are not
answer-accuracy measurements.

The user-authorized temporary Gemini 3.1 run is a separate model diagnostic. Set
`LLM_MODEL=gemini-3.1-flash-lite` only on the evaluation command, with the same
historical five/minute pacing and daily budget. That trial did not change production.
`python -m eval.student_quality_finalize --completion --alternate --scoped`
pairs the retained 3.1 trial with the final scoped candidate, verifies exact prompt
parity, and records hashes. It cannot substitute for production-model acceptance.
`python -m eval.student_quality_report --completion --scoped --retrieval-only`
compares first-candidate retrieval with final scoped retrieval independently of
the model change. Retain failed provider attempts and rank gates explicitly;
correct-looking answers do not turn a failed deterministic gate into a pass.

For the paid student migration, local `.env` selects `gemini-3.8-flash`, omits
deprecated sampling fields and sets medium thinking with a 4096-token ceiling.
The student audit/dialogue commands now default to `--delay 0`; the old pacing
limit is removed. Provider limits and transient failures still require handling.
Use a single evaluation worker with a shared ledger, for example:

```bash
python -m eval.student_quality_audit --cases <frozen-cases> --output <new-trace> \
  --live-ids all --replay-retrieval <frozen-evidence> \
  --budget-ledger <shared-ledger> --budget-usd 3 \
  --input-usd-per-million 0.75 --output-usd-per-million 3.75
```

Prices must be checked against [Google's current pricing](https://ai.google.dev/gemini-api/docs/pricing).
The guard reserves counted input plus maximum output before each generation
attempt, including retries, then settles successful usage including reasoning.
Failed attempts retain their reservation. This is a conservative evaluation
estimate, not an account balance reader; unrelated account usage is excluded.
Do not run simultaneous writers against the same ledger. Staff curation budgets
and its model remain separate and unchanged. Oracle migration remains separate.

For the final catalogue/output-contract diagnostic, use `--contextual` together
with `--completion --alternate --scoped` on the finalizer and reporter. The
completion report identifies the exact final traces. `student_quality_delta`
can reuse a successful answer only when its entire prompt, model and recorded generation profile are identical
to frozen candidate retrieval; it replays current local replies and deterministic
output guards without provider calls. Changed prompts and service failures remain
pending for fresh live evaluation. Preserve the reuse lineage and failed source
attempts. Cached prompt parity is not an independent repeat or production-model
acceptance. For example, on the temporary evaluation model:

```bash
python -m eval.student_quality_delta --retrieval <frozen-candidate-jsonl> --prior <prior-trace-jsonl> --output <new-jsonl-path>
python -m eval.student_quality_finalize --completion --alternate --scoped --contextual --after-traces <answer-trace-filename-under-results>
python -m eval.student_quality_report --completion --scoped --contextual --retrieval-only
```

The historical [continuation report](results/student_quality_continue_20261007.md)
records the October 7 runtime, gate results, failures and source parity. The additional
`student_quality_generalization_set.jsonl` contains 40 frozen semantic probes,
and `student_quality_condition_holdout.jsonl` contains eight conditional-reasoning
controls across departments and numerical bounds. These use source-reviewed
`expected_behavior`; empty lexical evidence lists are not automatic semantic passes.
The live audit stops on the first quota error and, by default, three consecutive
service errors (`--max-consecutive-service-errors`). Failures stay in the trace.
Historical low/medium trials with different prompts or profiles are separate
experiments. Reuse requires exact current prompt and generation-profile parity;
the earlier long-prompt medium trial is not acceptance of the final candidate.
The two `student_quality_service_scope_holdout.jsonl` probes separate future
requests for CDC assistance from an employer's later hiring decision. The earlier
164-case verification is historical. The [paid candidate report](results/student_quality_paid_migration_20261008.md)
links current 179-case verification, actual-answer conversation lineage and separate
semantic source review; reproducibility checks do not score answer accuracy.

`student_quality_audit_set.jsonl` contains 60 source-grounded diagnostic probes;
`student_quality_holdout_set.jsonl` adds 20 validation probes. They cover broad
orientation, paraphrases, informal wording, typos, synthesis, references, switches,
contamination, ambiguity and unavailable information. They are synthetic probes,
not independently sampled student questions or replacements for the frozen faculty
set. The [dated audit](results/student_quality_audit_20261007.md) records paired
measurements, source review, rejected attempts and release-blocking limitations.

Run `python -m eval.student_quality_audit --output <new-jsonl-path>` against an
isolated development Compose `test-db` / `msfea_test` index. Retrieval is recorded
without provider calls by default. Add `--live-ids all` for live answers (provider
quota applies), or `--cases eval/student_quality_holdout_set.jsonl` for validation.
Each trace retains literal/resolved queries, ordered chunks/cosines, exact model
context/prompt and final answers. `--replay-retrieval <trace>` isolates generation
against an immutable earlier retrieval result. Do not rebuild the index during a
run; pytest uses a separate database because its fixtures rebuild indexes.

Phrase coverage is an evidence proxy, not semantic accuracy. Q47's initial
generic report-length phrase conflicts with the ECE override and is explicitly
excluded from aggregate phrase metrics; its original authored record is preserved.
`student_quality_report.py` reproduces the dated coverage summary.
`student_quality_finalize.py` assembles the dated paired traces, verifies exact
final prompt/local-reply parity and records source hashes. It uses mocked generation
and makes no provider calls. Independently review conditions, scope and actual
claims before release; passing evidence and citation checks is insufficient.

```bash
python -m eval.run     # summarize the golden set
python -m eval.threshold_eval  # verify the pre-LLM 0.60 gate; no Gemini usage
python -m eval.build_faculty_golden path/to/RAG_FAQ_Questions_Answers_Updated.xlsx
pytest                 # run metric + golden-set tests
```

The faculty workbook questions are now versioned in `faculty_questions_golden.jsonl`.
Future independently sourced student questions can be added with source review;
the original `golden_set.jsonl` remains useful for synthetic edge-case coverage.
