# Student quality continuation — 7 October 2026

Local candidate only. Oracle, original source files and production model settings
have not been changed. This report supersedes the acceptance status in the
[earlier completion report](student_quality_completion_20261007.md); its failed
attempts and historical measurements remain intact.

## Outcome and acceptance

The general retrieval/conversation improvements pass the frozen deterministic
gates. The attribute candidate passes **493 Python tests, two skipped**; the last
small assistance-scope change also passes **127 focused generation/conversation/scope
tests**, with final strict type checks on 102 files and lint passing. Two warnings
in the full suite originate in dependencies. These overlapping suites establish
engineering regression coverage, not perfect chatbot accuracy.

Final temporary-model traces cover **164 cases**: 149 provider answers and 15
current local replies, with 124 provider answers reused only for identical full
prompts and model settings. The [manifest](student_quality_continue_final_manifest_20261007.json)
verifies current prompt/local-reply parity and the 66-file source freeze, and retains
eight failed attempts in the listed default-model attempt files. Earlier failed
variants remain separately retained. This is trace verification, not 164 correct
answers. **Production-model acceptance is still open.** The temporary
Gemini 3.1 Flash-Lite results must not be presented as verification of the serving
model. No result here establishes correctness on every future student question
or replaces independent faculty calibration.

FEAA 500 registration in the first semester and FEAA 500A in the second are a
consistent course sequence. Neither the sources nor the owner clarification
justify describing it as a KB inconsistency.

## Weaknesses, ranked by impact

| Rank | Cause | Evidence | General response |
| --- | --- | --- | --- |
| 1 | KB/chunking/retrieval: incomplete governing conditions | A credit fact could arrive without departmental academic-credit recognition; application rules could arrive without the distinct enrollment threshold; general internship evidence could omit controlling department conditions | Self-contained facts with their qualifications, reviewed bounded evidence links, preserved wrapped prose/bullet blocks and explicit department scope |
| 2 | Retrieval/intent: narrow FAQ fragments substituted for orientation | Broad internship questions previously selected a combined-placement exception; orientation was not guaranteed to retrieve ordinary topic context | Keep detailed FAQs and add verified topic overviews; reserve relevant overview evidence for broad requests without weakening the threshold |
| 3 | Conversation/ranking: short attributes lost their subject | R06 “Does the second part cost extra?” previously refused despite the handbook's second-semester fee rule; unresolved literal queries favored unrelated forms and limits | Resolve ordinal references and requested attributes from the current user topic; omit an independent literal search only for short referential attributes, preserving dual retrieval for substantive conditions |
| 4 | Scope/generation: a related process stage was treated as an answer | R05 previously invented a permanent-employment no-guarantee policy from initial CO-OP material | Reviewed process-stage metadata and a later-outcome evidence guard; preserve ordinary career-support questions; do not infer post-completion policy from entry rules |
| 5 | Conversation: stale history and unresolved references | Topic switches, switch-backs and service-menu sign-up questions can refer to materially different processes | Prefer explicit current subjects; retain only the current topic history; clarify ambiguous menu references; inherit a minimum/maximum dimension from user wording, not an earlier assistant claim |
| 6 | Retrieval: spelling mistakes can hide ordinary subjects | Informal internship wording and R13 “alumini mentro” | Bounded corpus-derived spelling candidates; genuine primary evidence still has to clear the unchanged global threshold |
| 7 | Generation: correct evidence does not ensure correct conditional reasoning | R31 still generalized a second-company condition scoped to a six-week first placement to a seven-plus-one proposal | Retain as a failure; compare reasoning configuration with identical evidence rather than hard-code a numeric plan or repeatedly add question-specific rules |

An additional general scope-guard failure was found: S01 asks whether the CDC will
help with a job search after CO-OP. Approved job-support evidence was retrieved,
but the future-tense guard prevented generation. S02 asks whether an employer
will hire the student; that genuinely unsupported outcome remains guarded. The
fix distinguishes requests for assistance from hiring decisions and preserves
explicit guarantees and hiring claims preceding an assistance phrase. Unit controls
use unrelated workshops, training and advisors, not a hard-coded CDC exception.

These causes interact. A wholesale FAQ replacement, hosted embeddings, reranker,
new query-rewriting LLM or general-purpose agent service is not justified by the
current evidence.

## Implemented scope

- Normalized Markdown preserves wrapped paragraphs and qualifying continuation
  lines within a bullet. Separate paragraphs, Q&A boundaries and different bullets
  can still split. The free-form Studio window splitter keeps its existing behavior.
- CO-OP course-credit recognition is self-contained. Application and coursework
  sections link to eligibility conditions so application and enrollment remain
  distinct. The internship/CO-OP comparison includes documented requirement,
  optionality and substitution.
- Ordinal follow-ups, shared fee/duration/contact/link attributes and bound
  follow-ups use general language features. Unit probes also use unrelated courses,
  invoices, certificates and workshops; source topics and test IDs are not encoded
  as policy decisions.
- Later-employment scope recognizes ordinary employment inflections and
  completion wording. It does not turn a placement guarantee into a later policy.
- Answer intent separates ordinary orientation, quantities, activity permission,
  exact combinations, approval and confirmation. Safe arithmetic is allowed;
  arithmetic alone cannot authorize a policy exception.
- Reviewed links can supply a governing ancestor with its scoped detail. When an
  explicitly linked canonical ancestor is already supplied, it is presented before
  its child. This changes presentation only, never retrieval scores, department
  filtering or threshold authorization. This did **not** eliminate R31 on the
  default-thinking temporary model; it is not claimed as a proven reasoning cure.
- Live audit runs stop on quota errors and repeated consecutive service failures.
  Reused answers require the same complete prompt and model; current deterministic
  replies and output guards are replayed, and reuse lineage stays explicit.
- Requested attributes get a focused answer cue: acknowledge the specific missing
  value and offer verified help for that topic. No price is invented from credits.
  H14 previously answered a membership-price question with a program description;
  it now states that the price is absent and supplies the verified program page
  and CDC contact. Q35/F12/R25 similarly provide the IAESTE contact while preserving
  the missing price. Known CO-OP fees, department contacts and links stay correct.

No answer is keyed to the screenshot, a frozen question ID or a numeric test plan.
Department/course rules remain in reviewed source-backed content.

## Recommended KB shape

Retain both useful narrative and focused Q&A:

1. Topic overview: purpose and ordinary path.
2. Governing facts and requirements with their qualifications.
3. Application/enrollment/placement/completion stages.
4. Procedures and deliverables.
5. Scoped exceptions, with the department and triggering circumstances explicit.
6. Verified contacts and links.
7. Focused FAQs and reviewed evidence links to controlling conditions.

Synthetic connective text may reorganize already approved facts; it must never
introduce permission, dates, policy reasons or new contacts. A fact such as “three
credits” should not lose “department decides whether it counts toward the degree.”
Source-backed summaries address orientation; detailed evidence still addresses
specific questions. A more extensive rewrite would need measured gains and source
review, rather than assuming the existence of Q&A is itself the problem.

## Final deterministic measurements

| Check | Final candidate | Interpretation |
| --- | --- | --- |
| Original 114-case diagnostic: all required evidence in retrieved/full context | 90/94 eligible cases | Original 250-chunk baseline: 74/94 retrieved, 71/94 supplied context |
| Individual evidence phrases | 151/155 | Original baseline 132/155; phrase coverage is not correctness |
| Overview presence | 16/17 | Original baseline 15/17 |
| Golden adaptive context recall | 123/124 | Previous candidate 122/124; remaining CEE lexical miss already contains the equivalent “six-week” condition |
| Faculty source-document recall | 198/205 | Unchanged; passing the 95% floor does not erase seven misses |
| Valid-query similarity gate | 165/165 | Existing threshold preserved |
| Off-topic pre-model block | 13/20 | Remaining seven need grounded generation/refusal |
| Synthesis evidence and supplied-context gate | 75/75 | Premise coverage, not live synthesis correctness |
| Conversation evidence / independent parity | 21/21; 9/9 | Previously failing strict rank-one credit probes now pass without changing their expectations |
| Conversation evidence top one | 16/21 | Not every probe requires rank one |
| Stress evidence / independent parity | 43/43; 19/19 | All gate requirements pass |
| Stress all evidence in top three | 41/43 | Previous 242-chunk variant 42/43; retain this ranking trade-off |
| Publication evidence guard | 9/9 | No publication authorized |
| Conflict candidate coverage | 7/7; zero known false-positive fixtures | Bounded constructed checks, not general conflict accuracy |

Q47's original generic report-length expectation conflicts with its ECE override
and remains transparently excluded from phrase aggregates; the authored expectation
has not been changed. Other literal phrase misses can contain equivalent numbers,
phrasing or contact information. They stay misses in the metric.

[All eight gate statuses](student_quality_continue_release_gate_status_20261007.json),
[gate log](student_quality_continue_release_gates_20261007.txt),
[full attribute check run](student_quality_continue_attribute_full_checks_retry_20261007.txt),
[final scope checks](student_quality_continue_service_checks_20261007.txt)
and [corpus inspection](student_quality_continue_release_corpus_20261007.json)
are retained. The final corpus has 243 chunks, 95 containing Q&A, no heading-only
evidence and no embedding inputs exceeding the pinned model's 512-token limit.
The last changes affect answer intent/guarding only. All 114 final frozen retrieved
chunks and supplied context blocks are identical to the gate-tested corpus's traces;
final prompt/local-reply parity is verified independently. The earlier 491-test
run and failed checks remain retained. A diagnostic script's two type errors were
fixed using a scoped provider patch; the retry passes rather than hiding the attempt.

## Answer evaluation and retained failures

The original 114 probes are supplemented by **40 frozen generalization questions**
and **eight frozen conditional-reasoning controls**, plus the two frozen service-scope
probes. They cover several departments,
CO-OP, internships, IAESTE, career preparation, Career+, mentorship, ordinary
quantities, unavailable facts, topic switches and source-supported inference.
The new sets were frozen before their answers; semantic expectations were not
changed to rescue a weak answer.

The 40-question baseline was interrupted by provider service errors and contains
only a subset of healthy answers. It is not a complete paired 40-question accuracy
comparison. Before/after claims are restricted to cases with comparable healthy
attempts. R05's unsupported employment conclusion and R06's unnecessary refusal
are concrete examples that improved.

The [final 40-question source review](student_quality_continue_final_generalization_review_20261007.json)
records 35 passes, four partial answers and one scope failure. These are Codex
rubric judgments, not independently calibrated accuracy. The prior review had
34 passes, five partials and one failure; the general attribute change improves
the unknown-price referral. Remaining partials concern academic-status completeness,
other application requirements, a generic office-hours referral and unnecessary
split-placement detail on an ordinary duration question.

R31 remains a source-scope reasoning failure on default-thinking 3.1: evidence
contains the written-approval route and the six-week-specific second-placement
condition, but the answer declares the different proposed split insufficient using
that condition. The problem is neither missing retrieval nor an invented KB
contradiction. Stronger prompt wording, separated source sections and parent-first
presentation did not reliably cure it. A repeated call that ended in service
errors supplies no evidence of a fix.

The eight additional controls check a department-approved hypothetical total,
the matching six-week condition, explicit MECH/CHEM split restrictions, CO-OP's
minimum, credits above a minimum, per-slide/overall narration bounds and an
undocumented different split. All eight default-thinking answers handle their
core distinctions; some wording is stronger or less precise than ideal. This is
Codex source review, not independent human calibration or proof that the general
class is solved.

The [medium-thinking diagnostic](student_quality_continue_medium_20261007_answers.jsonl)
replays the same nine prompts and context (the eight controls plus R31). All calls
succeed. R31 now correctly explains the approval requirement without transferring
the six-week condition; P08 gives a better qualified answer. However, P01 fails to
answer the arithmetic under the student's explicitly assumed written approval and
repeats an approval warning. This is mixed evidence: stronger reasoning improves
a material scope conclusion but does not establish complete usefulness or justify
a global production setting change. Temperature, seed and output budget stay fixed;
the trial's explicit medium configuration is kept separate from default-thinking
answers and reuse inputs. No additional rewriting model was added.

Lower-severity answer issues include unnecessary exceptional details on an
ordinary duration question and generic departmental escalation where a verified
service contact would be more useful. Unknown fee amounts and office hours must
remain unknown; these are usefulness issues, not permission to invent facts.

All SDK failures, retries and rejected variants remain in dated trace/log files.
The [final verification log](student_quality_continue_final_verify_20261007.txt),
[default 114 answers](student_quality_continue_final_answers_20261007.jsonl),
[40 generalization answers](student_quality_continue_final_generalization_answers_20261007.jsonl)
and [service-scope comparison](student_quality_continue_service_scope_after_20261007.jsonl)
retain the final results. Citation membership and prompt parity validate provenance
and reproducibility, not the correctness of every sentence.

## Release boundary and source parity

A read-only Oracle inventory at **15:30 UTC on 7 October** found zero active
approved staff revisions, zero curated serving chunks and 253 serving file chunks.
The file-backed candidate therefore covers the active canonical source classes at
that snapshot. [Inventory](student_quality_continue_oracle_source_inventory_20261007.json).
This removes the earlier unknown-parity assumption; future staff revisions need a
fresh check. No Oracle writes, index rebuilds or deployments were performed.

Acceptance still requires healthy final-runtime answers on the production model,
source review of the remaining conditional reasoning class, policy-owner review
of normalized reorganization, and independent human calibration for trusted
accuracy claims. Provider quota/outages are external verification limits; they
must not be reported as chatbot refusals or counted as correct answers.

## Engineering references

The changes follow established practices, without importing an extra framework:
semantic/document-boundary chunking in [Microsoft's chunking guide](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-chunking-phase),
broader context around precise matches in [Haystack's parent/child retrieval documentation](https://docs.haystack.deepset.ai/docs/automergingretriever),
and separate grounding, relevance, completeness and correctness review in
[Microsoft's evaluation guide](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-llm-evaluation-phase).
These sources inform techniques; measured project results determine acceptance.
The temporary model's configurable thinking is described in
[Google's Gemini guide](https://ai.google.dev/gemini-api/docs/gemini-3).
