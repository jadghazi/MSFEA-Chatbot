# Main student-model quality audit — 7–8 October 2026

## Outcome

**Engineering acceptance is incomplete. Do not deploy this candidate yet.** Main-model
access is confirmed through actual student generation using the configured
`gemini-flash-lite-latest` alias, with normal production generation settings and no
override. Later, Gemini returned HTTP 429. The bounded cooldown diagnostic reports
`GenerateRequestsPerDayPerProjectPerModel-FreeTier`, quota value **500**; this is a
project/model daily quota, rather than evidence that a replacement key reset it.
See the [sanitized diagnostic](student_quality_main_quota_classification_20261007.json)
and [Google's quota documentation](https://ai.google.dev/gemini-api/docs/rate-limits).
Generation stopped; provider errors are retained separately from knowledge refusals.
The replacement credentials were usable for substantial main-model evaluation;
this later exhaustion does not mean those earlier successful calls failed.
Google documents daily reset at midnight Pacific time. The returned retry hint
alone is not proof that the daily budget will reset after that delay.

The candidate improves whole failure classes, not the attached internship question
alone. Nevertheless, some current answers still omit relevant conditions or include
unasked material, and the final main-model set is incomplete. Passing evidence gates
and valid citations cannot establish full answer correctness. Oracle, original
`kb/source/` documents and production deployment settings have not been changed.
FEAA 500 followed by FEAA 500A remains a consistent two-semester sequence.

## Main weaknesses, ranked by impact

| Rank | Primary cause | Observed evidence | General improvement |
| --- | --- | --- | --- |
| 1 | KB representation / chunking / retrieval | Narrow rules could arrive without governing duration, department exceptions or separate required deliverables. An abbreviated alternative was incorrectly read as two additions forming one route. | Preserve coherent paragraphs and bullet continuations; make normal rules and each complete alternative self-contained; link reviewed controlling sections and named definitions. |
| 2 | Retrieval / answer intent | Broad questions selected a combined-placement FAQ rather than the topic's ordinary purpose and process. Some current overviews still volunteer exceptional paths. | Retain detailed FAQs, add source-backed topic overviews and bounded overview retrieval; distinguish orientation from decisions, requirements and requested attributes. |
| 3 | Conversation / attribute ranking | Fee, duration, contact and link follow-ups lost their program or actor; alumni-mentor link retrieval inherited the goal of career help. | Resolve the current student subject, actor and ordinal; add an attribute-focused lexical path; reserve literal-plus-resolved retrieval for substantive ambiguity. |
| 4 | Wrong process / generation boundary | Entry or placement evidence supported invented claims about employment after CO-OP. One guard checked passages removed from final context. | Reviewed process-stage metadata, conservative later-outcome evidence checks, and authorization against actual supplied context. Documented job-search support remains available. |
| 5 | Conversation routing / stale context | An explicitly abandoned reports topic still contaminated interview retrieval, despite no old generation history; a detailed pronoun follow-up lost its student anchor. | Remove abandoned-topic framing only from self-contained searches; prioritize new subjects; retain current-topic student anchors for genuine references without treating assistant claims as authority. |
| 6 | Generation / conditional synthesis | Correct evidence did not ensure correct arithmetic, deadline-row association, ordinary requirements or applicable exceptions. | Source-independent task cues separate hypotheses from official eligibility, procedures from deadlines, substitutions from personal verification, and normal obligations from exceptional routes. Remaining failures require live verification. |
| 7 | Retrieval / spelling | Informal spelling such as “alumini mentro” could hide ordinary knowledge. | Conservative corpus-derived correction with unique nearby spellings and retrieval support; unchanged global cosine threshold. |

This is a combination of causes. The existence of Q&A is not itself a defect:
**isolated, incomplete and ambiguously scoped Q&A is the defect**. More text alone
also failed: joining guidance still outranked the full online-module description
until a reviewed link restored its complete governing section.

## What changed and why it is general

The local candidate uses existing local BGE embeddings, PostgreSQL full-text/vector
fusion and reviewed one-hop evidence links. Ordinary top-k remains 7; comparisons
have a larger bounded depth. The cosine threshold remains 0.60. Spelling matches,
lexical additions and companion passages cannot independently authorize generation.
Department isolation, source labels, citation checks, privacy and publication gates
remain in force. No question IDs or numerical proposals dispatch to canned answers.

Normalized content now includes topic-level orientation plus precise facts. Report
clarifications link to the introduction stating separately required Progress and
Final Training Reports and the applicable presentation exception. Restricted formats
retain ordinary duration/location context. Employer IAESTE instructions retain the
distinct student introduction. CO-OP tuition is separate from internship substitution;
the approved current one-credit clarification supplies internship credit/billing.

Each alternative now repeats its complete shared starting component. The existing
six-company-week prefix belongs to both the research and second-company routes;
the additions must not be combined into a new route. A named procedure, such as
progress reporting for an arrangement, links to the arrangement's approved
definition. This repaired an observed synthesis-gate miss after the representation
change. The initial failed gate and interrupted stale-index run remain recorded.
No new approval, exception, fee, deadline or policy rationale was introduced.

Conversation and answer cues describe language tasks rather than university policy.
Domain-independent tests use housing, workshops, exchanges and advisors. Broad
orientation, exact permissions, hypothetical totals, required-item lists and
substitution questions need different answer styles even when they share evidence.

These bounded changes follow established RAG practice: keep enough governing
context without indiscriminate expansion, and evaluate retrieval separately from
answer generation. See Microsoft's [chunking guidance](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-chunking-phase),
[evaluation guidance](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-llm-evaluation-phase)
and [scenario-specific prompt guidance](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/rag/rag-prompt-engineering).

## Measured results and their limits

The current [77-file freeze](student_quality_main_named_route_freeze_20261007.json)
and [179-case retrieval trace](student_quality_main_named_route_retrieval_20261007.jsonl)
identify the exact runtime, normalized sources and frozen questions. The disposable
candidate index contains 243 chunks, including 95 Q&A chunks, no heading-only
passages and no embedding-input truncation. Tests use a separate disposable DB.
No index is rebuilt while live evaluation runs.

| Check | Result | Meaning / limitation |
| --- | --- | --- |
| Required evidence in original diagnostic subset | 91/94 retrieved and in supplied context; 152/155 phrases | Original 250-chunk baseline: 74/94 retrieved, 71/94 context, 132/155 phrases. Phrase matching is not semantic accuracy. |
| Golden adaptive context gate | 123/124 | Passes the existing floor; one miss remains. |
| Faculty source-document gate | 199/205 | Passes 95% floor. Six expected-document misses remain; equivalent core facts appear in other approved sources. Not 205/205 and not live answer verification. |
| Valid similarity / off-topic blocking | 165/165 valid; 13/20 off-topic blocked before generation | Remaining off-topic cases still require grounded generation/refusal. Threshold unchanged. |
| Synthesis premises in retrieval and final context | 75/75 | Earlier alternative-path attempt was 74/75 and failed; named-definition link repairs it. This is evidence coverage, not correct reasoning. |
| Conversation evidence / independent parity | 21/21; 9/9 | Deterministic supplied-history probes. |
| Stress evidence / independent parity | 43/43; 19/19 | Deterministic supplied-history probes; not actual generated conversations. |
| Publication / conflict gates | 9/9; 7/7 with zero known false-positive fixtures | Existing guard expectations preserved. |
| Final main-model trace verification | 82/179 current records: 67 exact provider-prompt reuses and 15 freshly replayed local replies | 97 current prompts still require main-model calls. Exact reuse is not an independent repeat. |
| Source review of those 82 | 74 pass, 8 partial, zero material failures in this subset | Codex source judgments, not faculty calibration or full-set accuracy. |
| Paired main-model subset, 75 common cases | Before: 66 pass / 8 partial / 1 fail. After: 68 pass / 7 partial / 0 fail | Five improved grades and three regressions to partial. This is not a complete before/after result. |

Artifacts: [coverage](student_quality_main_named_route_coverage_20261007.json),
[gate status](student_quality_main_named_route_gate_status_20261007.json),
[corpus](student_quality_main_named_route_corpus_20261007.json),
[trace manifest](student_quality_main_named_route_manifest_20261007.json),
[source review](student_quality_main_named_route_review_20261007.json),
[paired review](student_quality_main_named_route_paired_review_20261007.json).
The generic Q47 phrase expectation is retained unchanged but excluded from the
phrase score because an ECE-specific rule controls. Q04/Q09/Q18 remain lexical
phrase misses. No frozen policy expectation was edited to make a candidate pass.

The first complete main-model run was 164 healthy records, graded 146 pass,
17 partial and one material failure: CO-OP application and advisor-meeting months
were confused despite correct supplied evidence. Three 31-record global-prompt
trials were rejected because they transferred deadlines to unrelated deliverables
or actors. Their useful wording did not justify accepting wrong policy answers.
The smaller local candidate keeps the prior global prompt and uses task cues.
See the [baseline review](student_quality_main_baseline_review_20261007.json),
[compact trial](student_quality_main_compact_trial_20261007.jsonl),
[guarded trial](student_quality_main_guarded_trial_20261007.jsonl) and
[small global trial](student_quality_main_small_trial_20261007.jsonl).

Actual-history tests found problems that isolated questions missed. The original
20-turn run had 13 pass, three partial and four material failures. Later runs
corrected hypothetical arithmetic, the interview switch, mentorship scope,
overseas options and outdated adjacent credit information. A six-turn report
conversation then had four pass and two partial, with the previously unnecessary
report-substitution refusal corrected. That intermediate six-turn result is not a
fresh final 20-turn acceptance run.

The newest actual-history run stopped at D01.5 on quota failure, after four healthy
answers: three pass and one partial. Its duration follow-up gives the correct
minimum but adds an employer response estimate and unasked extension guidance.
The [offline prefix check](student_quality_main_named_route_offline_verify_20261007.json)
confirms source/index identity and exact current prompts for only D01.1–D01.3.
D01.4's prompt changed with the final KB link, so its earlier answer is not accepted
as a current result. Remaining turns are unverified. Earlier generated history is never replaced with
invented replies. See [interrupted trace](student_quality_main_alternative_paths_dialogue_20261007.jsonl)
and [review](student_quality_main_alternative_paths_dialogue_review_20261007.json).

## Remaining work before engineering acceptance

The final current-input regression suite passes **543 tests, with two skips** and
two dependency deprecation warnings. [Full-suite output](student_quality_main_named_route_all_tests_20261007.log),
[lint](student_quality_main_named_route_lint_20261007.log) and
[strict types](student_quality_main_named_route_mypy_20261007.log) all pass; type
checking covers 110 source/evaluation files. The final offline check verifies all
77 frozen hashes and canonical/index equality without provider calls. Documentation
links and `git diff --check` pass. The unrelated CI edits are preserved, originals
have no diff, and none of these checks changes Oracle. Passing these checks does
not complete the remaining live answer evaluation.

1. Finish the 97 pending current main-model prompts and all three final actual-history
   conversations, retaining provider errors and every retried attempt.
2. Address demonstrated answer-selection weaknesses through controlled, identical-evidence
   trials: P02 omits the applicable second-component minimum; P04 adds an unrelated
   duration rule; H01/Q02 volunteer exceptions or exhaustive detail in orientation;
   D01.3 borrows a quantity from another process. U04's approval qualification is
   confusing after a standard-scope prohibition. R34 contains an invented word.
   R02/R04 remain incomplete against the frozen review criteria.
3. Review complete paired results and new transfer probes before accepting any further
   cue/model change. Do not silently discard regressions or report best-of retries.
4. Run final source/index/prompt parity and regression checks after any further change.
   Independent faculty calibration and policy-owner source review remain separate
   institutional acceptance work, not substitutes for finishing engineering checks.

Rubric relevance also needs calibration. R02 directly answers whether course credit
automatically counts toward the degree; its missing full-time-status facet is not
explicitly requested. R04 directly addresses the stated credit barrier, rather than
certifying all eligibility. Keep the recorded completeness labels and expectations,
but do not pad answers with unasked facts merely to improve a benchmark score.
The controlling-condition omission and unrelated quantities are stronger evidence
of actual student-facing defects than those two completeness labels.

No extra rewriter, hosted embeddings, reranker or agent architecture is justified
yet. The remaining examples already supply their decisive evidence; first test
conditional answer selection and relevance. A controlled reasoning/model comparison
may be warranted if these errors persist, but it must use the same frozen evidence
and normal supported provider configuration. Metadata identifies the configured
“Latest” alias, not a resolved underlying weight version; it does not establish
that the serving model is a particular 2.5 or 3.1 release.

The earlier “four months against a six-month minimum” remark refers to frozen
negative control P05, not an introduced policy: it asks whether four months of
paid full-time work qualifies as MSFEA CO-OP. The handbook states a minimum of
six months for MSFEA; pay and full-time status alone do not satisfy duration.
This control is separate from Approved Experience internships and from the
consistent FEAA 500/500A registration sequence.

The [pending-case manifest](student_quality_main_named_route_pending_20261007.json)
records the exact outstanding IDs and frozen retrieval source. Resume on the
isolated `msfea-quality-next` Compose project, with one SDK worker, only after
model quota is available and the source/index identity still matches:

```powershell
$pending = Get-Content eval/results/student_quality_main_named_route_pending_20261007.json -Raw | ConvertFrom-Json
docker compose -p msfea-quality-next -f docker-compose.yml -f docker-compose.dev.yml run --rm -e OMP_NUM_THREADS=1 -e MKL_NUM_THREADS=1 dev python -m eval.student_quality_audit --cases $pending.cases --replay-retrieval $pending.retrieval --ids $pending.live_ids --live-ids all --delay 12 --output eval/results/student_quality_main_named_route_changed_20261008.jsonl
```

Do not run the dialogue worker concurrently. A changed runtime/source identity
requires a fresh trace/delta calculation, not blind reuse of this pending list.
Completing these calls also does not by itself resolve the known partial answers.

## Recommended KB structure and change priority

Keep each topic's ordinary overview, governing facts, requirements, procedures,
conditional exceptions, contacts and focused FAQs. Distinguish application,
enrollment, placement, participation and completion when they have different rules.
Write each allowed alternative as a complete independent path. Attach department
and triggering conditions to the fact they qualify, and retain editorial source
provenance. Synthetic connective text may reorganize verified facts only.

High-impact, low-complexity work is this source-backed restructuring, bounded
context links, current-topic attribute resolution and measured answer-task cues.
Larger parent/child retrieval, learned reranking or a different generation model
are architectural options requiring additional evidence; they are not prerequisites
merely because other RAG systems use them.

The [historical intermediate review](student_quality_main_intermediate_review_20261007.md)
retains the earlier measurements and rejected attempts. The earlier
[temporary-model report](student_quality_continue_20261007.md) remains historical
for acceptance; none of its answers is relabeled as a main-model answer.
