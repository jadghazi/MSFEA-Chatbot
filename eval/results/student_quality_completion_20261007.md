# Student quality candidate completion — 7 October 2026

> Historical snapshot: this report records an earlier local candidate and its
> retained failures. See the [continuation report](student_quality_continue_20261007.md)
> for current acceptance status, resolved rank gates and the dated source-parity check.

**The local candidate shows measured general improvement, but full success and deployment acceptance are still open. Production-model verification exhausted its daily quota; the user-authorized Gemini 3.1 diagnostic is separate. A strict conversation rank gate also fails despite complete evidence reaching the model.**

Oracle has not been changed. This report continues the [first quality audit](student_quality_audit_20261007.md); that first candidate was a partial success with known release blockers. The scope remains general student assistance across CDC topics, not the attached internship exchange.

## Main weaknesses, ranked by impact

| Weakness | Origin | Evidence and general treatment |
| --- | --- | --- |
| Conditional policy context was fragmented | KB structure + retrieval | Q30/F02 received the general Fall presentation schedule without the controlling ECE end-relative deadline. F06 retrieved a later window of the restriction section without the remote restriction in its earlier window. Restore complete reviewed policy sections and their applicable companions; preserve department filtering. |
| Broad topic composition was weak | KB representation + retrieval + prompt | The original audit reproduced a narrow two-company answer to a broad topic request. Raising depth alone did not solve it. Topic overviews plus detailed rules and an orientation answer contract remain in the candidate; all original 80 probes are rerun. |
| Attribute follow-ups lost their subject or the requested fact | Conversational routing + retrieval | Q24/F07 refused the CO-OP fee question. Fee/cost/length/contact words were treated as possible new subjects or retrieved unrelated facts. Preserve the prior substantive subject across attribute turns and add a topic-AND-attribute full-text path to the existing hybrid fusion. |
| Related evidence was used outside its scope | KB scope + retrieval + generation | H15 used a no-initial-placement guarantee to answer employment after CO-OP. Stage labels and prompting alone failed; entry filtering removed the rule but 3.1 still invented a no-guarantee outcome. Definitive later employment questions now require approved evidence addressing that stage before generation. Q11 also confused general and course-specific duration; Q50 confused bot and institution authority. |
| Informal spelling caused confident wrong matches or unnecessary refusals | Retrieval | Q44/F19 failed the 0.60 gate; F22's misspelled location question received petition advice despite approved abroad information. Use unique bounded source-vocabulary corrections, protected known words and separate confidence checks. Supplemental spelling evidence cannot authorize the gate. |
| Old conversation contaminated a new subject; genuine continuations were mis-scored | Routing + query scoring | H11/F25 inherited the six-week topic for interview help. F29/V04 inherited CO-OP but also scored unresolved literal wording because discourse words were counted as substantive content. Named subjects override history; filler alone cannot justify a literal dual query. Resolve quantity retrieval separately from actual generation intent. |
| Service directories encouraged adjacent-service advice; missing-information replies omitted escalation | Context selection + generation/output contract | H08 suggested the full-time Career Portal for internship search. A reviewed catalogue role now limits unlinked directory evidence for a single-program leading result. Q35's empty missing-information sentence now becomes the configured human escalation. Unsupported link destinations are removed; this does not fact-check the remaining prose. |

The ordinary internship minimum and approval conditions were also separated in legacy ECE/IEM bullets. They now sit together, reconciled against existing approved owner FAQs. A prompt-only quantity instruction failed twice on Q16 before this source repair. No new duration, eligibility, approval route or exception was introduced.

## Why this is a general engineering change

Runtime logic has no evaluation IDs or question-to-answer cases. The mechanisms operate on section relationships, department metadata, English attribute/intent grammar and active approved-source vocabulary. Domain-specific editorial links express genuine controlling policy relationships, not aliases for test wording.

Context restoration adapts the established pattern of retrieving focused leaves and recovering complete parent context described in [Haystack's AutoMergingRetriever documentation](https://docs.haystack.deepset.ai/docs/automergingretriever). Here it uses exact canonical section paths and one-hop reviewed companions rather than adding Haystack, a new store or a recursive graph.

Spelling recovery follows bounded edit-distance suggestions and indexed-vocabulary confidence principles illustrated in [Elasticsearch's suggester documentation](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-suggesters). The implementation retains PostgreSQL, BGE and the original query; it rejects ambiguous repairs, protects known tokenizer words, preserves identifiers, and repairs at most two unknown long words. The global cosine threshold remains 0.60.

Scope filtering follows the metadata qualification pattern described in [Microsoft's search filter documentation](https://learn.microsoft.com/en-us/azure/search/search-filters): exclude clearly inapplicable evidence before retrieval/ranking. This is implemented in the existing PostgreSQL queries, including lexical paths, typo recovery and linked companions. No Azure dependency is added. Filtering alone did not prevent unsupported later-employment conclusions, so definitive outcome requests also need approved `post_completion` evidence. The guard uses employment/retention intent and explicit later-time grammar, not a CO-OP keyword or a test ID. General career-support requests still use documented support; verified future later-stage facts permit normal grounded generation. Implicit stages and other service boundaries remain limitations.

High-impact changes with little additional complexity are the source scope clarifications, atomic fact/condition paragraphs, generic intent instructions and deterministic subject handling. The moderate representation change is reviewed section metadata with complete-section restoration. There is no additional LLM rewrite, reranker, embedding provider, framework or permanent service. An acronym alias experiment was rejected: direct CO-OP retrieval already scored about 0.81; unresolved literal scoring was the actual comparative-follow-up failure.

## Improved KB structure

Keep topic overviews and precise FAQs together. A useful topic contains:

1. Purpose and ordinary path.
2. Requirements and key facts, with scope and all conditions attached.
3. Procedures and deliverables, distinguished from permission or individual approval.
4. Department exceptions and controlling rules.
5. Contacts and verified action links.
6. Related topics and precise FAQ details.

The evidence does not justify discarding the FAQ material. Precise approved FAQs
are useful for factual retrieval. The weakness is presenting them as disconnected
answer-sized fragments, without ordinary topic context, scope or controlling
conditions. Add/reconcile those layers using existing verified facts; do not
generate a larger synthetic KB with guessed policy or repetitive filler.

Reviewed `content_role` markers identify overviews and service catalogues. `evidence_links` connect controlling or complementary sections; ingestion validates that every target identifies exactly one canonical path. For linked seeds, retrieval restores both their own windows and linked sections once; unlinked seeds do not automatically recover every parent window. Companion scores cannot authorize generation, department isolation still applies, and an oversized complete bundle triggers the existing context ceiling rather than silently dropping conditions. `process_stage` describes existing source applicability. Mixed CO-OP FAQ chapters were split into their real admission, placement, registration, substitution and degree-credit subjects before tagging. No employment-after-completion policy was invented. Markers are removed from factual text; only evidence links inherit to children, while role and stage do not.

The catalogue rule uses existing reviewed `program` metadata: only a non-directory leading primary result with exactly one program can omit unlinked directory passages. Mixed/unknown scopes and directory-led questions retain them, and explicit companions are always preserved. An overly broad prototype lost useful broad-question context on Q40/H03 (88/94 context hits); it was rejected. The conservative candidate restores 90/94. This is not universal service isolation, particularly when program scope is broad or missing.

Heading-only and scope-only parent windows supply no facts and are excluded. Original authoritative files remain unchanged. Normalized additions and reconciliations retain dated provenance; active approved immutable staff revisions remain a separate canonical ingestion input. This isolated evaluation uses the file-backed corpus and does not establish parity with Oracle's active staff revisions.

An audit of the second canonical path found that Studio revisions originally
lacked stage metadata. The local revision chunker now recognizes one reviewed
stage marker in the immutable answer, strips it from factual text and carries
scope through every window; conflicting/malformed scopes fail. The immutable
input and department/provenance metadata remain intact. This is an optional
marker, not a new publication permission or a schema migration; untagged legacy
revisions are unchanged. A database round-trip/window test covers it separately
from the frozen file-only evaluation. Existing active revisions still require
parity review: a legitimate untagged later-outcome fact could be withheld by the
guard. The whole serving KB has not been verified from this file-only index.

## Evaluation method and retained attempts

The final set contains 114 cases: the original 60 diagnostic questions, the original 20 validation questions, 30 frozen failure-class probes and four comparative attribute probes. The latter probes distinguish a minimum from a maximum and course duration from report length. Existing expected answers were not rewritten to pass the candidate. Q47's generic-template phrase conflicts with its ECE override and remains excluded from phrase metrics; its answer is reviewed against the approved ECE source.

The completion baseline is the first local candidate, using its preserved 80 paired traces plus 30 and four exact baseline-model runs on a separate immutable index/code snapshot. Thus original-to-first-candidate measurements remain historical; this comparison measures the remaining work. All index rebuilding and tests use disposable development Compose databases ending in `/msfea_test`, never the demo or Oracle.

Retrieval is frozen before answer generation. Traces preserve user wording, resolved and literal queries, spelling supplements, chunks/scores/roles, final context, exact prompt, model, answer and provider usage. Finalization checks current prompt parity and local deterministic replies, pairs identical case IDs, and records code/source/dataset hashes. Seed coverage and complete-context coverage are reported separately: appended companions are not top-seven seed hits. Phrase presence, source-document recall, citations and refusal flags do not establish answer correctness.

Retained interim attempts include:

- `student_quality_classes_candidate1_20261007.jsonl`: early 30-case trial; relative-path resolution and quantity/typo/comparative weaknesses remained.
- `student_quality_finish_smoke_20261007.jsonl` and `student_quality_quantity_smoke_20261007.jsonl`: prompt-only duration trials still volunteered an unapproved research alternative.
- `student_quality_completion_answers_20261007.jsonl`: complete 114-case trial; it exposed the missing same-section remote rule, generic comparison and actor confusion.
- `student_quality_completion_smoke_final_20261007.jsonl`: actor/comparison prompting alone still failed; source context then supplied the missing authority and disambiguated definitions.
- `student_quality_completion_checks_final_20261007.txt` and `student_quality_completion_gates_final_20261007.txt`: validation deliberately interrupted before the final source reconciliation. These partial runs are excluded from final acceptance.
- Earlier failed initialization/type-check logs remain retained. Successful retries have separate names; no error or abandoned trial counts as a pass.
- `student_quality_completion_context_delta_answers_20261007.jsonl`: partial provider trial for the overly broad catalogue prototype, stopped after evidence loss was found. Only answers with an exact final prompt/model match are eligible for explicit reuse.
- `student_quality_completion_catalogue_repeat_20261007.jsonl`: critical repeat, retaining F07's service error and Q35's missing human escalation before the final output-contract correction.

## Final candidate verification

### Retrieval, measured on all 114 frozen cases

| Evidence proxy | First local candidate | Final local candidate |
| --- | --- | --- |
| All required phrases in retrieved evidence (94 eligible cases) | 74/94 | 90/94 |
| All required phrases in actual model context | 71/94 | 90/94 |
| All required phrases in primary seed results alone | 74/94 | 79/94 |
| Individual evidence phrases present | 132/155 | 151/155 |
| Broad overview evidence | 15/17 | 16/17 |

The largest gain comes from complete policy context. Scoped-condition evidence improves from 4/6 to 6/6; attribute evidence from 7/9 to 9/9; typo evidence from 6/9 to 8/9; synthesis evidence from 7/11 to 10/11; explicit switches from 8/9 to 9/9. This is evidence coverage, not semantic answer accuracy. Four eligible cases still miss a required phrase (Q04, Q09, Q18, Q23); some involve equivalent wording such as spelled-out eight rather than the numeral. The earlier overview improvement is recorded in the first audit; linking internship-finding guidance to its reviewed parent adds one more broad-context hit here.

There are companions in 84 cases, repaired queries in eight and supplemental spelling candidates in three. The inspected index has 254 chunks from six normalized files, 94 chunks containing Q&A material, no heading-only windows and no embedding inputs above the pinned tokenizer's 512-token limit. This chunk count is not a count of unique FAQs. [Corpus inspection](student_quality_completion_scoped_corpus_20261007.json). Restoring sections increases generation context: broad comparisons can use about 7,800 input tokens. Warm local retrieval median is 294 ms, p95 1,092 ms with concurrent checks; this is not a serving-latency benchmark. Monitor context cost and latency before expanding editorial links.

Artifacts: [coverage metrics](student_quality_completion_context_retrieval_metrics_20261007.json), [114 final retrieval/context/prompt traces](student_quality_completion_catalogue_retrieval_20261007.jsonl), [actual timed retrieval](student_quality_completion_context_retrieval_20261007.jsonl). The final trace replays that immutable SQL retrieval with conservative context selection. Earlier `release` artifacts describe an intermediate 249-chunk version; `scoped` artifacts precede catalogue selection/output guards.

### Answers and model boundaries

The last complete 114-answer trial exposed three defects: a lost earlier window of the remote restriction, omitted course-level distinctions in a comparison, and confusion between chatbot authority and institutional authority. It is retained as a trial, not counted as the final candidate result. Prompt-only repairs did not reliably fix the latter two; reviewed source relationships and definition scope were necessary.

On the intermediate 249-chunk source/runtime, the three-case production-model smoke run succeeded, followed by 18 successful cases in the full run. Q11 overlaps, leaving 20 distinct live answers and nine verified local replies. That historical partial manifest leaves 85 live cases outstanding for that version. These answers must not be described as final 254-chunk production-model verification.

The production daily quota stopped further calls. The user then authorized temporary `gemini-3.1-flash-lite`, with the same 15 RPM / 500 RPD allowance. The first 114-case diagnostic trial produced 113 replies and one service timeout (H18). It exposed a stage-scope hallucination and poor vague-start orientation. A subsequent eight-case smoke trial still invented a no-later-employment-guarantee policy after the inapplicable entry rule was filtered out, motivating the evidence sufficiency gate. The next full scoped trial retained four service errors (Q36/Q40/Q51/H17). Temporary live trials used five/minute; production configuration and `.env` remain unchanged.

The final 114-case temporary-model assembly contains **102 provider answers with exact final prompt/model matches and 12 current deterministic replies**. No fresh SDK calls were required for assembly: eligible successful answers are explicitly reused from retained runs, with current link/escalation guards reapplied. The manifest records lineage, source/code/dataset hashes and five provider errors in those source runs. This is full trace/prompt coverage, not 114 fresh calls, 114 independently correct answers or production-model acceptance. The same-model before trial contains one service error, so it cannot establish paired semantic accuracy on all 114 cases.

| Critical source review | Before / retained trial | Final answer |
| --- | --- | --- |
| Q16: company duration | Volunteered research alternative without all approval conditions; prompt-only trials failed | Ordinary eight full weeks / 320 hours; six company weeks alone insufficient |
| F06: online training | Unnecessary refusal despite a documented restriction | Retrieved and answered the remote restriction; an exception requires the formal route |
| Q11: internship versus CO-OP | Baseline omitted optionality/substitution; later trial lost the MSFEA minimum | Distinguished the MSFEA eight-week minimum; included paid six-month CO-OP, optionality and FEAA 500 substitution |
| Q50: bot approval | Baseline was correct; intermediate trial attributed bot limitations to CDC | Limits chatbot authority; identifies authorized department/course personnel with CDC involvement |

The table describes intermediate production-model source reviews, not final-model acceptance. Q50 is a recovered regression, not a gain over baseline. Additional final temporary-model reviews cover the remaining general classes:

| Class | Final evidence/answer observation |
| --- | --- |
| Controlling department conditions | F01/F02 include the ECE one-week deadline alongside general deliverables; F01 includes the 15-minute voice-over maximum. These answers were already correct in the first 3.1 trial, so this is regression preservation, not an alternate-model before/after gain. |
| Attribute continuation | F07 answers FEAA 500 first-semester tuition and FEAA 500A without extra second-semester tuition; F09 retains CO-OP for six-month duration; F11 retrieves internship contacts. |
| Wrong stage/service | F13/H15 escalate unsupported later-employment guarantees; F14 still answers the documented initial-placement restriction. H08 gives internship-search channels without the full-time Career Portal claim. |
| Spelling | F19 explains MentorPlus+; F22 answers internship abroad with approval conditions rather than unrelated petition advice. |
| Topic switch/switch-back | F25 answers interview help; F28 returns to the IAESTE contact; F29 preserves CO-OP while answering a shorter-duration request. |
| Output contract | Q35's empty acknowledgement is replayed as a human escalation. Q04/H04 retain source labels as plain text instead of fabricated file links. Useful partial answers and documented negative policies are preserved. |

The eight critical repeat selections produced six successful provider replies, one F07 service error and one local H15 escalation. H08 and Q40 preserved intended scope in the repeat; F01, F19 and F25 preserved conditions/topic. Q35 again omitted a contact, justifying the final deterministic empty-acknowledgement guard; the raw unsafe-style attempt remains retained. The latest guard was checked through focused parsing tests and deterministic replay rather than another provider call. These are Codex source reviews, not independent faculty calibration or repeated-run reliability estimates.

Artifacts: [historical production partial manifest](student_quality_completion_partial_manifest_20261007.json), [temporary-model trial including timeout](student_quality_completion_alternate_answers_20261007.jsonl), [scoped smoke including unsafe outcome claim](student_quality_completion_scoped_smoke_20261007.jsonl), [final temporary-model manifest](student_quality_completion_context_alternate_manifest_20261007.json), [paired final answers](student_quality_completion_context_alternate_paired_after_20261007.jsonl), [critical repeat with failure](student_quality_completion_catalogue_repeat_20261007.jsonl). All unsuccessful/intermediate attempts remain retained.

The catalogue/output guards address observed service bleed and invented links but cannot establish every sentence's grounding. Some answers still volunteer unnecessary combined-placement details. Missing/mixed scope, implicit stages and other unsupported conclusions remain review boundaries. A favorable final answer cannot erase an earlier unsafe attempt, and the temporary model has not been promoted.

### Final deterministic checks

- Ruff passed; strict mypy passed on 94 source/eval files. Python: **470 passed, two skipped**, with two dependency deprecation warnings. [Full check log](student_quality_completion_catalogue_full_checks_retry_20261007.txt). This covers the stage/revision/catalogue/link candidate before the last empty-acknowledgement parser addition. The current generation module passed **54 focused tests**, including the five final fallback cases, with final lint/type checks in the [output-contract check log](student_quality_completion_final_contract_checks_20261007.txt).
- Frontend: **40 passed, zero failed**. [Frontend log](student_quality_completion_frontend_20261007.txt).
- Golden production context coverage: **122/124**; faculty source-document recall: **198/205**. These existing misses remain.
- Valid-query threshold pass: **165/165**; off-topic pre-model block: **13/20**. The other seven require grounded generation/refusal handling; the threshold was not relaxed.
- Synthesis premise/context gate: **75/75**. Conversation evidence: **21/21**, independent-query parity **9/9**, but **the conversation gate fails**: four degree-credit cases require the detailed phrase at rank one and receive it at rank two. The new degree-credit FAQ at rank one correctly says the department decides; both passages reach the model. The expected rank/phrase has not been relaxed or rewritten. This is a strict ordering regression, not an evidence loss, and remains open for review.
- Stress evidence: **43/43**, independent parity **19/19**. Publication evidence guard: **9/9**. Conflict candidate coverage: **7/7**, zero known false-positive fixtures. They do not authorize publication and do not erase the conversation gate failure.

[Final complete deterministic rerun](student_quality_completion_final_gates_20261007.txt)
records every command, including the conversation failure, and continues the
remaining checks. Golden coverage is above the unchanged CI floor of 90%; faculty
recall meets its 95% floor. The complete gate group is **not passing**, because the
four conversation ordering expectations remain unmet. Earlier scoped attempts,
including fresh-database initialization failure and its retry, remain retained.
The [gate status](student_quality_completion_final_gate_status_20261007.json)
records the failing case IDs explicitly. The PowerShell continuation driver's
exit status does not establish aggregate acceptance; per-command failures do.
File-backed source/retrieval/generation behavior remained frozen during final
answer assembly. The optional revision marker extension affects the separate
staff-content path, tested independently; the file-only index has no such revisions.

[Source inspection of the two golden phrase misses](student_quality_completion_final_known_misses_20261007.json)
separates them: the CEE result already contains the selected-company exception,
standard minimum and Chair-approval condition, with "six-week" rather than the
expected "6-week". That metric miss is not loss of the controlling CEE rule.
The comparison retrieves the eight-week minimum, paid six-month optional CO-OP
and substitution, but lacks the expected explicit graduation-requirement phrase.
Keep both original expectations and inspect actual grounding; do not convert an
equivalent phrase into a new passing score.

### Quota and remaining verification

The resumed attempt was paced at five requests per minute and stopped on its first 429. A full-request diagnostic identified `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, value **500**, rather than an RPM violation. The quota is shared at the project/model level; this does not establish that this audit alone consumed all 500 calls. An earlier small health check succeeded but did not prove evaluation capacity. Live calls then stopped.

[Safe quota diagnostic](student_quality_completion_quota_full_diagnostic_20261007.txt) recorded a retry delay of 45,098 seconds at 11:28 UTC on 7 October, approximately 03:00 Beirut on 8 October. This is the provider's reported delay, not a guaranteed reset. Retries and diagnostics count against the user's 15 RPM / 500 RPD budget.

To verify the production model after capacity returns, record a new 114-case retrieval/prompt freeze with the production evaluation model, then use it with `--delay 12` (five/minute) and a new answer-attempt file. The catalogue retrieval artifact records the temporary model and must not be relabeled as production. The intermediate partial manifest is not a final-version missing-ID list. Retain failed rows and stop immediately on another quota error. Verify full prompt parity, source-review scope/conditions and rerun critical probes before acceptance. `--resume` retries failed rows rather than treating provider errors as completed answers. The temporary-model comparison must remain separate; never combine model variants into a single accuracy score. No scheduled retry or deployment has been created.

## Limits and release boundary

These constructed probes diagnose and validate changes; they are not a representative real-student success rate. Codex source review is not independent human calibration. Existing golden/faculty retrieval misses, missing official information, real pilot outcomes and institutional acceptance remain separate work. Typo recovery is deliberately bounded; ambiguous references still require clarification and unsupported policy or individual status must be withheld.

**Correction following the project owner's clarification:** "FEAA 500 in both
semesters" describes registration across the course sequence, with FEAA 500A
as the second-semester code. These are consistent instructions. The earlier
characterization as a KB inconsistency was incorrect; no policy reconciliation
is required. Answers should explain the precise second-semester code when the
student asks about registration or tuition. F07/Q24 already do so. A generic
comparison's shorthand is a possible clarity issue, not an invented policy conflict.

The candidate has not been published or deployed. Any reviewed release must use the normal knowledge/source review, publication, active-revision parity and deployment checks. Synthetic test content must never be published on Oracle.

The measured next step is production-model verification of this exact source/runtime after quota returns, with source review of scope, conditions, unsupported links and escalation behavior. Decide the strict degree-credit rank regression against the actual controlling facts, without changing expected answers merely to pass. Obtain policy-owner acceptance of the reorganized normalized content and verify active staff-revision parity before release. A larger embedding model, reranker, additional rewriter or wholesale FAQ replacement is not justified by these results yet.
