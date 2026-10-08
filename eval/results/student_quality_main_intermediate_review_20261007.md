# Historical intermediate review

This records earlier attempts. Current acceptance status is in [the main-model report](student_quality_main_model_20261007.md).

# Main student-model verification — 7–8 October 2026

Local candidate only. Oracle has not been changed. This review continues the
[quality audit](student_quality_continue_20261007.md); previous temporary-model
results and failed experiments remain intact.

## Verification in progress

A fresh development process successfully called the configured student model,
`gemini-flash-lite-latest`, without a model override. The
[health trace](student_quality_main_key_probe_20261007.jsonl) correctly distinguishes
an ordinary duration total from approval of a two-company arrangement. This
confirms usable local credentials/model access, not remaining quota or an Oracle
configuration change. Google applies quotas per project rather than per key;
see [its rate-limit documentation](https://ai.google.dev/gemini-api/docs/rate-limits).

The [164 frozen cases](student_quality_main_cases_20261007.jsonl) cover the original
114-case completion set, 40 generalization cases, eight conditional controls and
two service/outcome controls. The main-model run uses the same frozen retrieved
evidence and current prompt as the final temporary-model candidate, with normal
student generation settings. No temporary-model answer is relabeled or counted as
a main-model answer. Live attempts are paced and failures remain recorded.

An additional [actual-history set](../student_quality_dialogue_set.jsonl) contains
20 turns across three conversations. Its expectations were written before any
answers. The [dialogue harness](../student_quality_dialogue_eval.py) passes each
actual generated reply into subsequent turns and retrieves from the isolated
candidate index. It checks attributes, topic switches, typos, assumed approval,
department rules and missing details without supplying canned earlier replies.

The [source freeze](student_quality_main_freeze_20261007.json) records 69 file
hashes. Full Python checks use a different disposable database from the stable
candidate evaluation database. Neither process targets the demo or Oracle.

## Review boundaries

Retrieval coverage, citation membership, current-prompt parity and source-based
answer correctness are separate checks. A cited answer is not automatically
correct. Relevant source contact information should remain useful even when a
requested exact amount is absent; absence never permits an invented fee.

Engineering candidate acceptance will be decided after the completed main-model
and actual-history review. Independent faculty calibration, owner review of
normalized content, pilot outcomes and deployment are separate acceptance work;
finite test results cannot establish correctness for every future question.

## Completed diagnosis and rejected experiments

The complete first main-model run has 164 healthy records: 149 provider answers
and 15 local replies, without provider errors. The
[source review](student_quality_main_baseline_review_20261007.json) grades 146
passes, 17 partials and one material failure. Partials distinguish useful answers
with relevance, completeness or actionability weaknesses from wrong policies;
these are Codex judgments, not independent faculty accuracy labels.

F21 supplies the correct CO-OP student timeline but the answer places the advisor
meeting in the application month. The supplied table says application in
July/February and the meeting in August/March. This is a generation association
failure, not missing retrieval. Four separately frozen timeline probes were added
before answering; their baseline answers are retained in
[the timeline trace](student_quality_main_timeline_before_20261007.jsonl).

| Trial, 31 identical-evidence main-model records each | Useful changes | Reason it was not accepted |
| --- | --- | --- |
| [Compact prompt](student_quality_main_compact_trial_20261007.jsonl) | Better missing-fee referrals and resource links; F21 avoids the wrong meeting month | Q10 transfers a deadline to other deliverables; T03 mistakes “only the main steps” for a one-step completion plan; P01 adds an irrelevant split rule despite assumed approval |
| [Guarded long prompt](student_quality_main_guarded_trial_20261007.jsonl) | Better partial help and direct clarification; F21 avoids the wrong meeting month | T02 assigns student application/advising months to employer advertising/interviews, which are actually April–May/May–June for that track; broad answers still include unasked details |
| [Small cues plus global table instruction](student_quality_main_small_trial_20261007.jsonl) | Correct procedure/attribute routing, useful fee referrals and direct clarification | Q10 still assigns the report's one-week deadline to the Summary Sheet and Student Evaluation Form; the global addition did not establish a reliable gain |

No trial is relabeled as an accepted default answer. The compact trial changes
both prompt length and content; it does not isolate length as the cause. Repeated
identical settings also produced different replies in a bounded
[raw-response diagnostic](student_quality_main_raw_diagnostic_20261007.jsonl).
Neither a seed nor a successful retry establishes determinism.

The smaller final candidate keeps the original global prompt, adds procedure
guidance only for procedure requests, distinguishes a response-length constraint
from an explicit sufficiency question, preserves attributes after permission
discussions, and gives missing-detail replies a source-grounded response pattern.
An overview cue groups the normal path into stages instead of interpreting the
complete-list rule as a command to reproduce every form and deadline.

A separate evidence-boundary bug was reproduced without any SDK calls: a
post-completion chunk could authorize generation after dominant-entry selection
had removed it from the supplied context. The guard now checks `prompt_chunks`,
the evidence actually given to the model. The focused regression uses synthetic
workshop facts on the isolated development path; no test policy is published.

The intermediate [72-file acceptance freeze](student_quality_main_acceptance_freeze_20261007.json)
includes runtime, normalized sources, frozen datasets and the boundary tests.
All 168 acceptance records retain identical retrieved chunks and factual context
relative to their baseline. Of these, 116 provider prompts are exactly unchanged
and 15 local replies are re-executed; 37 changed prompts receive fresh main-model
answers. Reuse never crosses model, prompt or experimental configuration.

This workflow follows Microsoft's guidance to
[evaluate retrieval and answer behavior separately](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-llm-evaluation-phase)
and [test stable versus scenario-specific prompt instructions](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-prompt-engineering).
The selected changes address intent/evidence classes; they contain no case IDs,
numeric-plan exceptions or question-to-answer map.

## Actual-history diagnosis and final candidate

The first [20-turn actual-history run](student_quality_main_release_dialogue_20261007.jsonl)
completed without provider errors but prevented acceptance of that intermediate
candidate. These failures were not hidden by the earlier isolated-question results:

| Failure class | Evidence in the run | General change |
| --- | --- | --- |
| Conditional synthesis / generation | D02.2 rejects an explicitly approved five-plus-three hypothetical using a rule triggered by a six-week first component; the proper conditions were supplied | A source-independent calculation cue distinguishes arithmetic under a hypothesis from official eligibility, still preserving explicit matching prohibitions |
| Incomplete parent context / KB retrieval | D02.4 cannot decide whether a final report replaces a progress report; revision guidance arrives without the separate graded deliverables | Reviewed report guidance links to the existing introduction; presentation discussion retains the IEM exception |
| Current-message contamination / routing | D02.5 retrieves report material after “Forget reports for a moment. What help is available for job interviews?”; no old history was passed to generation | Remove an abandoned-topic preface from search only when the remainder is self-contained, retaining the original generation question |
| Actor-versus-goal attribute / routing | D03.2 inherits “help with careers” instead of the alumni mentor and supplies an unrelated Career+ joining route | Prefer the actor of help/offer/provide clauses as the subject; generic document referents retain their precedence |
| Options replaced by a scoped exception / KB and intent | D03.3 substitutes a narrow US-remote exception for overseas internship options | Search the independent current question, recognize options intent, and restore ordinary approved locations and the student IAESTE introduction alongside restrictions/employer guidance |
| Adjacent attributes / normalized representation | D01.6 repeats an older zero-credit internship label during a CO-OP-fee answer | Separate CO-OP tuition from internship substitution; use the approved current one-credit clarification, preserving source provenance |

FEAA 500 and FEAA 500A remain the consistent first-/second-semester sequence.
Original files are unchanged. The newer normalized links reorganize existing
verified facts; no extra approval, fee, exception or student opportunity is invented.
These bounded links follow the existing implementation rather than adding a new
parent-document service. Microsoft's
[chunking guidance](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-chunking-phase)
describes the risk of losing necessary context in small chunks and introducing
noise with oversized context; the links are limited to reviewed governing sections.

The final frozen set has **179 cases**: the previous 164, four timeline probes and
11 [transfer probes](../student_quality_transfer_holdout.jsonl). Transfer expectations
were authored before live answers. They include different numerical arrangements,
policy prohibition versus hypothetical approval, new switch wording, mentorship
attributes and program-specific report follow-ups. Domain-independent boundary
tests use workshops, housing, exchanges and advisors rather than encoding policies
or frozen question IDs.

The intermediate [74-file freeze](student_quality_main_verified_freeze_20261007.json) captures
that runtime, normalized sources, datasets and boundary tests. All 179 queries
were retrieved freshly from the isolated 243-chunk candidate index in
[this trace](student_quality_main_verified_retrieval_20261007.jsonl). No index was
rebuilt during that run. Exact prompt/model parity permits reuse of 50 provider
answers; 15 local replies are re-executed and 114 changed/new provider prompts
receive fresh main-model calls. This is not 179 independent fresh model calls.

An intermediate full-suite attempt changed normalized inputs while publication
validation was running. Its stale-run safeguard correctly rejected that run
(530 passed, one failed, two skipped); the failure is retained and is not counted
as a final pass. Final checks run after freezing the inputs. The eight deterministic
[gate commands](student_quality_main_verified_gate_status_20261007.json) already
pass on that index: golden context 123/124, faculty source-document recall
198/205, valid threshold queries 165/165, synthesis premises/context 75/75,
conversation evidence 21/21, stress evidence 43/43, publication 9/9 and conflict
coverage 7/7 with zero known false positives. None is an answer-accuracy score.

### Further actual-history verification

The next [20-turn run](student_quality_main_accepted_dialogue_20261007.jsonl) has
no provider errors. It corrects the earlier wrong arithmetic refusal, interview
switch, mentorship URL scope, overseas options and outdated tuition-adjacent fact.
It nevertheless does **not** establish acceptance: D02.4 asks an unnecessary
clarification even though its retrieval query correctly identifies the final
report and the three graded deliverables reach the model. The exact prompt
reveals that the ten-word history heuristic removed the preceding student question.
The model was warned that the resolved subject was only a routing hint but could
not inspect the actual anchor. This is a conversational/generation boundary
failure (E/G/H), rather than another missing report policy.

The closing change keeps current-topic **student** questions for detailed strong
pronoun follow-ups and excludes earlier assistant claims. Independent detailed
questions retain the previous no-history behavior. Two domain-independent tests
check the positive reference and negative standalone cases; all 169 focused
conversation, generation and chunking checks pass. The in-progress full suite is
cancelled before this change, retained explicitly, and is not presented as a pass.

A separate broad career-options query exposed registration-only module retrieval.
Putting the verified module list in one paragraph alone did not fix it: a different
window containing only joining guidance still ranked highly. The closing KB
annotation uses the existing reviewed links to restore its full section and
career-support overview. No fact or policy changes. This distinguishes a measured
context-restoration change from an unproven formatting claim. The
[closing freeze](student_quality_main_closing_freeze_20261007.json) records that
intermediate identity; earlier files named `accepted` are retained intermediate
attempts, not final acceptance certificates.

The next closing conversation still refuses D02.4 despite correct student history
and report evidence. The normalized report introduction now states the separate
required reports in one self-contained paragraph, backed by the original summer
guidelines' required-deliverables table and approved grading clarification. A
source-independent substitution cue permits that supported relationship while
preserving documented optionality and replacement rules. The final six-turn D02
rerun answers the relationship correctly, switches to interview preparation and
then CV help, and preserves the ECE report limits. Two replies remain overlong or
repeat approval caveats despite an assumed approval. This is four passes and two
partials, not six perfect replies, and not a fresh final 20-turn evaluation.

The final full Python suite at this stage passes **538 tests, with two skips**.
The required-item transfer control U10 then exposes a generation selection failure:
ordinary reports and IEM exceptions are in the supplied context, but the reply
describes only special combined arrangements. The live run is stopped after 16
records, retained in the `main_final_verified_changed` trace. A general required-item
cue now asks for ordinary obligations first, retaining scoped exceptions and actual
stated conditions. Three domain-independent tests cover exchanges, housing and
workshops; the focused suite passes 154 checks. Its first attempt also included an
unrelated assertion that existing “which options” wording had an options cue;
that assertion is corrected to test non-interference with required-item routing.
No frozen policy expectation is changed.

The [U10 retest](student_quality_main_required_items_probe_20261007.jsonl) now gives
the ordinary Progress Report and Final Training Report with correct timing. It
still appends unrequested conditional routes, so it remains a partial for relevance.
The [current freeze](student_quality_main_required_items_freeze_20261007.json)
records 76 runtime/source/dataset/test hashes. All questions are retrieved again
from the unchanged isolated index, and only changed or missing exact prompts
require new main-model calls. Failed attempts and interrupted suites remain intact.

