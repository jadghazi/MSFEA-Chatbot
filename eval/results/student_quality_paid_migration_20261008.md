# General student-quality candidate and paid Gemini evaluation — 2026-10-08

**Local engineering candidate accepted; not deployed.** The [acceptance receipt](student_quality_paid_reference_acceptance_20261008.json) links the final verification and semantic review.

This continues the [general audit](student_quality_audit_20261007.md) and [main-model investigation](student_quality_main_model_20261007.md). The target is source-grounded assistance across CDC topics, including broad, informal and conversational questions. The screenshot is one diagnostic, not a question-specific routing rule.

Oracle is unchanged. Staff Knowledge Studio alignment is deferred; its existing model and workflows are preserved. Curated test information is excluded: the isolated final index has **246 normalized-source chunks and zero curated chunks**. Original files in `kb/source/` are unchanged. Local `.env` changes are not deployment or a serving-index rebuild.

## Main weaknesses, ranked by impact

| Weakness and origin | Evidence | General improvement |
| --- | --- | --- |
| Fragmented topic context — KB/chunking/retrieval | Broad questions selected narrow exceptions; wrapped lists and QA facts could separate obligations from scope. | Coherent paragraphs, lists, QA pairs and tables; reviewed source-derived topic overviews alongside detailed rules. |
| Controlling evidence omitted — retrieval/KB | Generic report length could arrive without the ECE override; two-company decisions needed the scoped second-component condition. | Bounded reviewed one-hop governing links restore related rules and applicable exceptions together, with department isolation. |
| Scope mixed across processes — KB/retrieval/generation | Initial CO-OP placement competition does not establish employment after CO-OP; late-start guidance contaminated ordinary orientation. | Separate actual process scopes; later-employment assertions require corresponding evidence. Separate ordinary duration from changed dates and late starts without adding policy. |
| Follow-up attributes and stale subjects — routing/retrieval | Fee/duration/contact/link queries could pick another program's detail; previous topics survived explicit switches. | Current-subject resolution, topic-and-attribute lexical search, literal/contextual paths when useful and bounded history. |
| Extractive or misdirected answers — prompting/generation | Correct evidence did not guarantee synthesis. A live-history substitution question answered the preceding checklist instead. | Compact intent-oriented prompt; explicit current-request priority; generic arithmetic, relationship, substitution and individual-record frames. |
| Spelling brittleness — retrieval | Informal misspellings could lose relevant mentorship/internship evidence. | Conservative corpus-supported recovery, protected vocabulary and retrieval confirmation; cosine threshold stays 0.60. |
| Model condition fidelity — generation | Low thinking moved a course-enrollment credit threshold into application eligibility. | Compare reasoning profiles on identical evidence, then rerun the full frozen set and actual-history tests. |

No question IDs, screenshot wording or new university facts are encoded as answers. Domain-independent intent tests use scholarships, workshops, exchanges and assessments. Grounding, refusal, citations, privacy, provenance and publication safeguards remain active.

## Knowledge representation and complexity

Use a topic overview, ordinary key facts and ordered stages, followed by scoped requirements, procedures, exceptions, contacts/resources, related governing rules and detailed FAQ facts. Keep FAQs: precise questions benefit from them. The weakness was insufficient coherent context around them, not the mere presence of Q&A.

Internship overview stages now distinguish approval/proposal before training, arrival/professional skills/progress during training, and final submissions at completion. Descriptive 8–12-week language is not an absolute maximum. FEAA 500 and FEAA 500A remain the consistent two-semester registration sequence.

Overview retrieval text supports discovery while full canonical text grounds answers. Governing companions cannot open the similarity gate. Pinned local BGE, PostgreSQL lexical/semantic fusion and local storage remain. The 246 embedding inputs have a maximum of **466 tokens against the 512-token limit**, with zero truncation candidates.

This follows [Anthropic's contextual retrieval research](https://www.anthropic.com/engineering/contextual-retrieval) and [Google's RAG evaluation guidance](https://cloud.google.com/blog/products/ai-machine-learning/optimizing-rag-retrieval?hl=en): restore source context and measure retrieval separately from answers. No speculative reranker, paid embeddings or second query-rewrite model was added. Previous rewriting experiments did not justify another model call.

The source/paragraph, scoped-companion, attribute and prompt changes are focused improvements within the existing pipeline. A bulk KB replacement, new embedding provider, reranker or additional generation/verification service would be architectural work; these tests do not currently justify it. Policy-owner review of the normalized restructuring remains necessary before publication.

## Model and API profile

The accepted local profile is GA `gemini-3.8-flash` with **medium thinking**; actual paid inference access is confirmed. The real `.env` and `.env.example` both select this profile. [Google's migration guidance](https://ai.google.dev/gemini-api/docs/generate-content/latest-model) requires omission of deprecated sampling fields and supports low/medium/high thinking. Student calls omit temperature and seed, explicitly set thinking level, disable unused automatic function calling and allow 4096 tokens including reasoning and visible output. The ceiling does not request long answers. SDK 2.28.0 supports this configuration. Staff curation retains its existing profile; actual student previews use the student profile without changing Studio workflows.

| Experiment | Source-reviewed evidence | Decision |
| --- | --- | --- |
| Earlier Lite main model | 82/179 verified: 74 pass, 8 partial; daily quota interrupted the remaining 97. | Historical incomplete evidence, not a completed model comparison. |
| Paid Flash, low, long prompt | Full 179: 177 essential-policy/intent passes, 2 material errors (proposal stage and descriptive range made into maximum). | Rejected. |
| Paid Flash, medium, long prompt | 44 cases: 42 pass, 2 material errors, including overgeneralized hypothetical conditions. | Rejected; higher reasoning alone did not repair the old prompt. |
| Paid Flash, low, compact prompt | Same 44 cases: no material policy errors. | Adopt compact structure; retain the earlier failed Lite compact trial separately. |
| Compact intent frames and scope-separated KB | 179 current-profile answers verified: 102 exact-prompt reused provider answers, 62 fresh, 15 local replies. | Intermediate evidence; actual history still exposed a stale-task error. |
| Current-request-priority prompt, low | Fresh full 179: 178 essential-policy/intent passes, 1 material application-versus-enrollment error. | Rejected as final profile. |
| Current-request-priority prompt, medium | 47-case comparison: zero core policy/current-intent failures, including enrollment-stage fidelity and both history controls. | Passed controlled comparison; independently verified below. |

Actual-history testing initially found **19/20** turns addressing the requested intent. The failed substitution question repeated the earlier checklist request and failed both identical-prompt repeats. Explicit current-request priority produced correct substitution answers on both controlled repeats. Three two-turn holdouts were frozen before answers to test prohibited replacement, a documented positive waiver and distinct-program relationships. Final actual-history runs pass below. The additional transfer cases also exposed unnecessary clarifications when a named outcome caused the referenced operand to be dropped. General relational-reference routing fixes this; “no longer required” no longer becomes a duration query, and numbered subjects stay intact. No program-specific waiver is encoded.

## Retrieval and regression verification

Eight deterministic evidence gates passed on the canonical 246-chunk index:

| Check | Result and limit |
| --- | --- |
| Golden adaptive-depth evidence coverage | 123/124, above CI's 0.90 floor; one known phrase/evidence miss remains. |
| Faculty expected-source-document recall | 199/205 (97.1%), above 0.95 floor; six designated document misses remain. This is not faculty answer accuracy. |
| Similarity calibration | Valid 165/165, lowest cosine 0.6117; off-topic blocked 13/20. Related but unanswered questions need generation/scope guards. |
| Synthesis evidence | 75/75 all-premise coverage in actual model context. |
| Conversation routing | 21/21 evidence, independent-question parity 9/9. |
| Conversation stress | 43/43 evidence, independent parity 19/19; all evidence in top three for 41/43. |
| Publication evidence controls | 9/9 across departments and unknown scope. |
| Conflict controls | 7/7, five conflict fixtures flagged, zero known false-positive fixtures. |

Full isolated Python regression before the final reference refinement: **560 passed, 2 skipped**, with two dependency deprecation warnings. After that focused refinement, **139 relevant tests passed** on the frozen final code/profile, including conversation, intent, provider, budget and index guards. Widget/staff browser-unit checks: **35 passed**. Final Ruff passed; strict source/evaluation mypy passed on **114 files**. The 21/21 conversation and 43/43 stress gates were rerun for relational routing; independent parity remains 9/9 and 19/19. Fresh final retrieval for all 179 probes produced no prompt/evidence changes for their existing answers.

## Spending, provenance and retained failures

Live delay is zero. A single provider worker satisfies the spending ledger's single-writer contract; it is not the old RPM cap. Before each attempt, counted input plus maximum output is reserved. Healthy usage settles including reasoning; failed attempts keep their conservative reservation. The initial $3 ceiling was raised to $4.50, then **$4.85** for final conversation transfer verification, within the user's stated $5 credit. Final cumulative conservative ledger spending is **$4.54614**, including retained failed-attempt reservations. This estimates evaluation spending; it is not an account balance or invoice and excludes unrelated workloads.

Verified [introductory pricing](https://ai.google.dev/gemini-api/docs/pricing) is $0.75/million input and $3.75/million output tokens, including thinking, through December 31, 2026. Recheck prices for future budgets; standard pricing changes in January 2027.

The final canonical fresh retrieval is `student_quality_paid_reference_final_retrieval_20261008.jsonl`; earlier controlled generation replay of frozen evidence is explicitly identified as replay. Successive source/runtime freezes and all full SDK traces retain questions, retrieval queries, ordered chunks/cosines, exact context/prompt, configuration and answers. `.env` secrets are excluded. Exact prompt/configuration parity and citations are reproducibility checks, not semantic judging.

Rejected long-prompt low/medium runs, intermediate answers and the failed actual-history conversation remain. Provider 504s/retries are retained in sanitized logs and ledger reservations; healthy accepted answers do not imply zero failed provider attempts. Initial schema bootstrap failures, a dry evaluation started during index rebuild and a rejected Windows-codepage merge are retained. Canonical/stable-index guards rejected the index mismatch; original UTF-8 SDK traces were reassembled and verified. None changed serving data. An accidentally expanded type command included untyped test files; the documented strict `src eval` command passed separately. Static prompt-wording tests were updated for equivalent compact instructions, without changing frozen answer expectations.

## Final candidate acceptance

| Final check | Result |
| --- | --- |
| Frozen semantic probes | **179/179 core passes** in separate source review; 164 provider answers and 15 local replies. |
| Independent paid answer run | 178 healthy results initially; U02 had two 504 attempts, then passed a separately retained fresh retry. The completed run contains 179 healthy answers. |
| Current code/evidence/profile verification | All 179 verified against fresh canonical retrieval and the final source freeze; all 164 model prompts/configurations are identical to the independent answer run. No additional main-set calls were needed after the general reference refinement; actual-history transfer was tested separately with fresh calls. |
| Actual-answer conversation chains | **20/20 core passes**, covering duration, tuition, contacts, links, spelling, topic changes, report substitution and unknown fees. |
| Frozen transfer chains | **6/6 core passes**, covering required-report separation, the positive CO-OP waiver and distinct mentorship/certification requirements. Current reference queries are correct. |
| Actual-history lineage | All 26 turns verified against their frozen datasets, actual preceding answers, current queries/prompts/profile and canonical index. |

“Core pass” means the answer addresses the current request with supported essential facts and conditions; it does not mean every answer is stylistically perfect. Main-set minor notes include some unasked details, broad credit-eligibility statements that could name enrollment more explicitly, and generic escalation wording for unrelated questions. Dialogue minor notes include an extra mentorship suggestion and a registration contact that could be more specific. These are recorded rather than silently relabeled as perfect answers. FEAA 500/500A is the documented two-term sequence, not a conflict.

Successful provider-attempt latency in the completed main run is **8.82 seconds median / 18.10 seconds p95**. This excludes retrieval, input-token counting and earlier failed retry time; it is not browser end-to-end latency. Healthy main-run usage estimates **$0.00640 per generated answer** at the dated introductory rates, including reasoning. No Pro upgrade or added model call is justified by the observed essential-answer failures in this candidate.

Reproducibility artifacts and semantic review are intentionally separate:

- [Final 179-case answers](student_quality_paid_reference_final_answers_20261008.jsonl), [current retrieval](student_quality_paid_reference_final_retrieval_20261008.jsonl), [source freeze](student_quality_paid_reference_final_freeze_20261008.json), [parity verification](student_quality_paid_reference_final_verified_20261008.json), and [source-review grades](student_quality_paid_reference_main_review_20261008.json).
- [Actual 20-turn dialogue](student_quality_paid_relation_dialogue_20261008.jsonl), [final 6-turn transfer](student_quality_paid_reference_final_holdout_20261008.jsonl), [lineage verification](student_quality_paid_reference_chains_verified_20261008.json), and [conversation source-review grades](student_quality_paid_reference_chains_review_20261008.json).
- [Independent paid full attempt](student_quality_paid_medium_final_full_20261008.jsonl), [successful U02 retry](student_quality_paid_medium_retry_20261008.jsonl), and [cumulative spending ledger](student_quality_paid_spend_20261008.jsonl).
- [Final 139-test receipt](student_quality_paid_reference_frozen_tests_20261008.log), [full-suite receipt](student_quality_paid_scope_full_tests_20261008.log), [Ruff](student_quality_paid_reference_frozen_lint_20261008.log) and [strict typing](student_quality_paid_reference_frozen_types_20261008.log).

## Acceptance boundary

Engineering acceptance is met for the frozen set and actual-history transfer runs: no material policy/current-intent failures, completed Codex source review and current prompt/profile/source parity. Minor verbosity, cosmetic formatting and unnecessary related details are tracked separately. This review is by Codex, not independent faculty calibration; the sets are constructed, not representative student traffic.

Known retrieval misses, policy-owner review, independent human calibration, wider pilot outcomes, institutional ownership and AUB-page integration remain separate work. No finite evaluation proves 100% future policy accuracy. Deployment and staff Studio alignment remain separate subsequently authorized tasks.
