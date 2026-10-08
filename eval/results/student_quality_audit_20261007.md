# Student assistant quality audit — 7 October 2026

**Historical first-candidate evidence.** The [completion investigation](student_quality_completion_20261007.md)
supersedes its current candidate status; measurements and failed attempts below
remain unchanged.

This is dated local evidence, not a deployment or independent human accuracy claim.
Baseline code: `a0caa4d`; file-backed corpus: 253 chunks / six normalized files.
The serving Oracle index and active staff revisions have not been changed.

## Initial diagnosis, before candidate changes

1. **Broad requests have poor evidence composition (KB representation + retrieval).**
   Q01 retrieved internship contacts, deliverables, reporting exceptions and a
   heading-only parent; Q02 retrieved two-company rules without the ordinary topic
   overview. The screenshot's answer was reproduced verbatim in substance. Q54
   (support besides internships) retrieved only internship material and refused.
   Raising depth to 12 did not recover the required overview dimensions for Q01,
   Q02, Q03 or Q54. Generic query expansions also failed these probes. Do not
   assume that a larger top-k or another rewriting call solves this class.
2. **The generation contract over-prioritizes narrowness (prompt + generation).**
   Q01 produced an unsolicited full deliverables list. Q10 refused a whole-process
   question despite receiving course description, timeline and application FAQ
   evidence. The prompt requires the context to "fully" answer the question,
   defaults to under 90 words, and gives detailed decision/confirmation cues but
   no broad-orientation contract. Useful supported partial summaries need explicit
   treatment; unsupported exact facts must still be withheld.
3. **Ambiguity becomes escalation (routing + refusal UX).** Q33 (unspecified
   deadline) refused instead of asking which deadline. Q34 (no referent) failed the
   similarity gate and escalated. Q58 resolves a multi-topic service list to CDC,
   even though "is that mandatory?" has no unique subject.
4. **Typo tolerance has a boundary (threshold + embeddings).** Q44 retrieved the
   correct MentorPlus+ passage but scored just below 0.60 and never reached the
   model. This is a pre-generation refusal, not missing KB content. Do not lower
   the global threshold from one probe; preserve the frozen off-topic calibration.
5. **Source coverage is uneven (KB).** IAESTE/mentorship are short but can answer
   basic introductions. Current IAESTE fees, individual approval status and future
   exact dates are genuinely unavailable and must not be synthesized as facts.

## Corpus observations

89 of 253 chunks contain explicit Q&A markers; most chunks are not FAQ entries.
The corpus already contains ordinary narrative guidelines, rubrics and a CO-OP
handbook. FAQ format is useful for precise exceptions; it is not sufficient as
the only representation for broad orientation. Seven chunks contain headings only.
No current chunk exceeds the BGE model's 512-token embedding input limit.
Current section paths and department inheritance are retained; global document
`program` metadata is too coarse for multi-topic documents. Hybrid retrieval
already exists (vector + PostgreSQL English full-text RRF); there is no reranker.

## Candidate direction and KB structure

Low complexity: remove non-evidence heading-only chunks, improve the answer
contract for overviews/partial answers/clarifications, and add reviewed topic-level
context assembled only from existing verified facts. Preserve detailed rules and
department exceptions. Recommended document layout: overview and purpose → normal
path → requirements → procedures/deliverables → explicitly scoped exceptions →
contacts/links → focused FAQs. Keep original source references for every added
summary and verify them against current approved clarifications.

Larger options (parent/child retrieval, content-derived typo recovery, reranking,
and topic metadata) require separate measured trials. No second LLM rewriting
layer, provider swap or blanket threshold relaxation is justified yet.

## Measurement contract

The 60 authored cases cover exact facts, paraphrases, typos, overviews, synthesis,
reasoning, follow-ups, switches, switch-backs, contamination, ambiguity and unknowns.
Raw artifacts include resolved/literal query, ordered canonical chunks, cosine
scores, exact model context/prompt and selected live answers. Scores are cosine,
not RRF fusion scores. Phrase coverage is a strict evidence proxy and can miss
equivalent wording; it is not answer accuracy. Semantic source review is reported
separately. Cases are synthetic diagnostic probes, not a random student sample.

## Result and release boundary

The bot's brittleness is primarily **evidence composition plus an overly narrow
answer contract**, with additional routing and policy-scope failures. It is not
simply a weak model or an all-FAQ knowledge base. The candidate improves broad
orientation across several topics while preserving the existing deterministic
retrieval gates. It is **not ready for deployment**: source review found remaining
condition errors and a deadline regression that automated evidence gates do not catch.

Original sources and approved decisions were inspected alongside all six normalized
files and serving code. This audit uses the file-backed local corpus; it does not
export Oracle's active immutable staff revisions or establish their parity with
the local index. The screenshot's behavior was reproduced on the original local
pipeline and configured Gemini model. No Oracle index, staff revision or publication
approval was changed. Existing unrelated working-tree changes were preserved.

## Ranked weaknesses and recommendations

| Impact | Weakness and evidence | Primary layer | Recommendation and complexity |
| --- | --- | --- | --- |
| High | Ordinary topic facts are scattered; Q01/Q02 retrieve reporting and split-placement details, Q54 retrieves internship material for broader support | KB representation + ranking (D/B/A) | Retain focused FAQs, add reviewed ordinary overviews, remove empty headings, reserve one relevant scoped overview for broad requests. Implemented; low/moderate complexity |
| High | Useful evidence is treated as insufficient; Q10 refuses a process summary, Q54/H05 refuse available career/alumni support | Prompt + unnecessary refusal (G/H/I) | Explicit overview and supported-partial-answer contract, answer current intent, allow genuinely supporting multiple citations. Implemented; low complexity |
| High, safety | General evidence can displace controlling department conditions; Q30 gives ECE the general presentation deadline; Q16 mentions research without its approval condition | Retrieval composition + generation scope (A/I) | Measure retrieval of a rule **and its controlling exceptions**, not just its document; test bounded scoped companion evidence and suppress unrelated alternatives. Remaining work; moderate complexity |
| Medium | Missing referents are treated as missing knowledge; Q33/Q34/Q58/H13 escalate | Conversational routing (E/H) | Ask a clarification for subjectless turns and singular references after a service menu; distinguish ordinary attribute follow-ups from proposed alternatives. Implemented; low complexity |
| Medium | Named switches can still inherit stale subjects; H11 resolves interview help against an earlier six-week plan | Contextualization/history (E/F) | Literal retrieval currently saves H11. Broaden source-independent switch recognition using a separate switch set; do not add another LLM rewriter without evidence. Remaining work; low/moderate complexity |
| Medium | Correct MentorPlus+ passage is retrieved for Q44 but its cosine is below 0.60 | Embedding/gate boundary (J) | Trial corpus-derived spelling/alias recovery or clarification under strict confidence; expand typo and off-topic controls first. Global threshold unchanged |
| Medium | Q24 misses CO-OP tuition evidence in the candidate; baseline retrieves it but still refuses. Q11 mixes generic industry internship duration with AUB course duration and omits optionality/substitution | Retrieval + prompt + source scope (A/G/I/D) | Test attribute follow-ups and comparisons separately; keep general definitions scoped apart from official course rules. Remaining work; low/moderate complexity |
| Medium | “Need a career plan before resume?” either invents an absent prerequisite rule or refuses useful adjacent help; H15 uses entry placement rules to answer employment **after** CO-OP | Generation task scope (G/I/H) | Separate documented policy status from source-backed coaching; identify the stage being asked about. Give supported help and say the precise status is unverified, without converting silence into “No.” Remaining work; low complexity, requires safety regression |
| Coverage/UX | Exact current fees, future dates and personal approval status are unavailable; six-question UI and eight-message API history bound conversation | Missing source / product boundary (C/J) | Obtain authoritative missing information where useful; consider chat limits separately using traffic/quota evidence. Do not synthesize unavailable facts or promise individual verification |

Classification follows the requested A–J taxonomy. Multiple causes are recorded
where evidence supports them; an unavailable fact is not automatically a retrieval bug.

## Implemented general changes

- Added source-grounded **internship, career-support and CO-OP overviews**. Each
  connects existing facts and has editorial provenance; it creates no new policy.
  Detailed FAQs, department exceptions and source documents remain available.
- Excluded seven empty heading chunks and empty windows. Added an explicit reviewed
  `content_role: overview` marker rather than guessing from headings such as
  “Organization Overview” in a report template. The frozen candidate has 250 chunks.
- Used title plus first purpose sentence as an overview's compact embedding text;
  its complete paragraph remains canonical evidence and full-text input. Broad
  retrieval can reserve one relevant overview within the normal bounded context,
  the same department scope, the unchanged threshold and 0.10 cosine proximity.
  Precise questions retain normal ranking; the existing department slot is preserved.
- Changed the generation contract to summarize and combine supported facts at the
  requested level, identify missing details, and avoid arbitrary exceptional plans.
  Broad answers may use up to 180 words; focused answers normally use 90. Existing
  policy grounding, history distrust, citation checking and disclaimer remain.
- Capability questions retrieve documented services instead of relying on a fixed
  list. Ambiguous subjectless questions and singular references to a service menu
  get a local clarification. The student's literal turn accompanies a resolved
  generation query so the resolver cannot silently redefine the question.
- Kept deterministic dual retrieval, local embeddings, Gemini adapter and the
  calibrated 0.60 gate. Added no hosted embeddings, paid vector service, reranker,
  second rewriting model or new frontend framework.

The normalized source layout should continue as **purpose/overview → ordinary
requirements → process → deliverables → scoped exceptions → contacts/links →
focused FAQs**, with editorial source mapping. For example, “eight weeks” belongs
to the ordinary internship rule; six-plus-two research and two-company arrangements
retain their approval conditions in exception sections. Future topic metadata should
come from reviewed content, not a hard-coded supported-topic list. A full rewrite of
all FAQs is not justified by this evidence. Parent/child chunks and reranking are
possible later experiments, not prerequisites for this candidate.

## Paired retrieval measurements

| Check | Original | Candidate |
| --- | ---: | ---: |
| 60-case audit: all authored evidence phrases present in retrieved chunks | 28/50 | 38/50 |
| Individual evidence phrases present in retrieval | 56/99 | 86/99 |
| Broad audit requests: all authored evidence present in retrieval | 4/13 | 12/13 |
| All authored evidence present in exact context sent to the model | 27/50 | 37/50 |
| 20-case validation: all authored evidence present in retrieval | 11/16 | 14/16 |
| Validation individual phrases present | 15/22 | 19/22 |
| Validation broad requests: all authored evidence present | 1/4 | 3/4 |

These are **retrieval evidence proxies, not answer accuracy**. Denominators omit
questions without evidence phrases and invalid Q47. Q47's initial generic 8–15
page expectation conflicts with the ECE override; its original record is retained
and excluded, while the actual answer is reviewed against five pages/1,500 words,
maximum 20. No faculty/golden expected answer was edited. Q04's equivalent “at
least 6 months” can miss a literal “minimum duration of 6” probe. Good short
answers need not cover every authored overview dimension (H01/H02 illustrate this).

All 80 cases have live before/after responses with no provider errors. Final
prompt parity was checked for all 80 against the saved exact prompts/local replies.
The 20 validation cases were authored before selecting the final overview embedding
representation; they are additional synthetic probes, not independent human samples.
Gemini answers are stochastic: these paired runs do not establish repeatability or
an unbiased population accuracy estimate. Do not report an overall correctness
percentage from phrase checks or citation presence.

## Answer review: improvements across classes

| Case/class | Original behavior | Candidate behavior |
| --- | --- | --- |
| Q01/Q02 broad internship orientation | Full deliverables dump or unrelated two-company arrangement | Purpose, ordinary credits/duration, placement approval, completion and next steps |
| Q10 complete internship path | Full refusal despite useful retrieved process facts | Connected finding/approval/training/completion explanation |
| Q54 support beyond internships | Internship-only retrieval and refusal | CV/modules, Career+, alumni mentorship and full-time job channels |
| H05 alumni/work-life question | Full refusal | MentorPlus+ guidance plus documented broader support |
| Q06/Q60 work readiness / uncertainty | Narrow module or Career+ answer | Connects planning with practical CV, interview and preparation resources |
| Q29 switch from combined-placement discussion to overview | Earlier combination can dominate | Ordinary internship orientation without assuming previous exceptional plan |
| Q33/Q34/Q58/H13 ambiguity | Escalation or arbitrary CDC referent | Clarifies which deadline, topic or service |

Knowledge-supported full refusals Q10/Q24/Q44/Q54 reduced from four to two
(Q24/Q44) on the diagnostic set. Ambiguity escalations Q33/Q34/Q58 became
clarifications. These specific counts do not equate all non-refusals with correctness.

## Remaining weak/failed answers and source review

| Cases | Evidence-based diagnosis | Status / recommended next check |
| --- | --- | --- |
| Q16 | Both original and candidate volunteer exceptional arrangements for an ordinary duration question. Candidate gives explicit prior approval for two-company work but omits the research alternative's approval condition | I/G; suppress unasked alternatives and test that any mentioned alternative retains all conditions |
| Q18 | Duration typo is understood, but candidate adds an unasked summer-course caveat | I; relevance weakness, not a missing duration answer |
| Q24 | Original exact context has tuition evidence yet refuses; candidate no longer supplies the appropriate tuition passage | G/H then A; retrieve program + asked attribute and retest fee follow-ups across programs |
| Q30 | ECE completion reply adds general first-two-weeks-of-Fall presentation timing; controlling ECE timing is absent from retrieved context | A/I; **candidate regression**, blocks release. Avoid unsolicited dates and retrieve scoped exceptions with their general rule |
| Q11 | Useful duration/pay comparison, but optionality and course substitution are omitted; “one or two months” is a generic industry description, not the AUB eight-week course rule | D/I; source-scope disambiguation and comparison completeness |
| Q44 | Correct mentorship evidence is available but rejected before generation because max cosine is below 0.60 | J/H; measured typo recovery needed, not invented KB content |
| Q46 | Correct remote restriction but vague “some departments” exception when ECE is selected | I; source-backed scoped answer needed, no claim that a petition authorizes an ECE exception |
| Q50 | Correctly says the bot cannot approve; then assumes self-secured placement and volunteers that form | I; current-intent relevance and approval route scope |
| H11 | Resolved query inherits an old six-week subject; literal query retrieves interview preparation and saves the answer | E/F; successful final answer does not clear routing defect |
| H15 | Entry acceptance/placement guarantee is used to answer employment after completing CO-OP | I; wrong stage. Do not extend “no placement guarantee” into an unsupported official hiring policy |
| H16 | Original refuses. Relaxed trial said unsupported “No” to a prerequisite; hardened final still refuses instead of offering useful documented CV/planning support with a precise limitation | G/H; safety retained, helpfulness still incomplete |
| Q35–Q39/Q57 and H14/H19 | Fees/year-specific dates/company approval/salary ranking or out-of-scope requests lack evidence | C/J; retain honest limits. No fabricated fees, dates, approvals or policy rationales observed in these final probes |

Unknown-answer correctness is not fully established: H15 specifically remains a
wrong-stage response. Citation labels being valid does not prove claims are supported.
This table is Codex source review, not independent policy-owner calibration.

## Alternatives tested and rejected

- **Top-k 12:** all-evidence retrieval only 28→30/50; broad coverage stayed 4/13.
  More narrow facts did not create an ordinary topic explanation.
- **Generic query expansion:** definition/guide/process variants for broad probes
  did not reliably recover the missing connected overview dimensions. Retained
  traces show the failures; no universal rewrite layer was added.
- **Prompt only:** Q02 still answered a split-placement exception; Q54 still
  refused. Instructions cannot synthesize evidence that was not supplied.
- **Overview with a long all-facts embedding:** mixed procedural vocabulary diluted
  broad semantic matching. Compact purpose representation plus full canonical
  evidence worked better. Incomplete intermediate indexes are not final measurements.
- **Automatically tag any “Overview” heading:** would classify report-template
  Organization Overview as student-topic context; rejected in favor of explicit markers.
- **Outcome-certainty cue:** a trial extended entry-placement evidence to “or hire”
  for H15. Rejected; the final trace uses the earlier prompt for this class. Remaining
  wrong-stage behavior is recorded rather than counted as a fixed unknown response.

## Regression verification

| Gate | Original | Candidate |
| --- | ---: | ---: |
| Golden production adaptive context recall | 122/124 | 122/124 |
| Faculty source-document recall | 198/205 | 198/205 |
| Valid threshold calibration queries passing | 165/165 | 165/165 |
| Off-topic queries blocked before model | 12/20 | 13/20 |
| Synthesis premises/context gate | — | 75/75 |
| Publication-guard preservation gate | — | 9/9 |
| Conversation gate / independent turn parity | — | 21/21; 9/9 |
| Conversation stress / independent turn parity | — | 43/43; 19/19 |

Golden misses remain `internship-vs-coop` and `faq-cee-exception`. Faculty misses
remain 007-chem, 025-ece, 045-ece, 075-ece, 125-ece, 131-mech and 158-ece. Document
recall is especially coarse when many topics share one document. Existing gates
passing while Q30 fails demonstrates why intent and conditional accuracy need
separate source review.

Full isolated Python suite: **424 passed, 2 skipped**. After the final ambiguity
and requirement-status changes: **92 focused tests passed**. Ruff and strict mypy
pass. The full suite is not claimed to have run again after the final two targeted
tests. An earlier changing-source run had failures (including stale curation source
fingerprint); stable rechecks passed. No live LLM tests used the serving database.
Widget submission tests passed 10/10; the development guide's Studio review,
preview and suggestion checks also passed. Affected guide/report Markdown links
resolve, and `git diff --check` passes.

## Reproduction and evidence integrity

Use isolated development Compose `test-db` / `msfea_test` only. Baseline, candidate
and pytest databases were separate; pytest rebuilds must not run against an audit
index. The script rejects serving database URLs and stops if a non-replay index
generation changes during an audit. Live evaluation consumes Gemini quota.

- Datasets: [60 diagnostic cases](../student_quality_audit_set.jsonl),
  [20 validation cases](../student_quality_holdout_set.jsonl).
- Authoritative combined traces: [before](student_quality_paired_before_20261007.jsonl)
  and [after](student_quality_paired_after_20261007.jsonl). Each row includes its
  original trace filename, question/history, contextual/literal query, selected
  chunks/cosines, exact prompt/context and final answer.
- Frozen original code and normalized inputs:
  `student_quality_baseline_code_20261007/` and `student_quality_baseline_kb_20261007/`.
  Original code is loaded for baseline replay, not merely its prompt template.
- Frozen candidate retrieval: `student_quality_retrieval_frozen_20261007.jsonl` and
  `student_quality_holdout_retrieval_after_20261007.jsonl`.
- [Metrics](student_quality_metrics_20261007.json),
  [final prompt parity/source hashes](student_quality_manifest_20261007.json),
  [baseline regression log](student_quality_baseline_controls_20261007.txt),
  [focused checks](student_quality_checks_20261007.txt), and
  [final static checks](student_quality_static_checks_20261007.txt).

Several early attempts were retained but excluded. `baseline_remaining` restored
only the old prompt, not old routing. `baseline_exact_remaining`, `holdout_before`
and `holdout_exact_before` ran while a background rebuild contaminated the baseline
index. The original 253-chunk corpus was restored and the authoritative baseline
remaining cases replay the first immutable retrieval trace with original code;
validation baseline was rerun on the restored corpus. `candidate_retrieval`,
`candidate_v2` and `final` are intermediate representations, not final metrics.
`status_main`/`status_holdout` contain the rejected outcome cue; only
`status_final_main` and `status_final_holdout` override the final paired traces.
No failed attempt or changed index was silently counted as a successful baseline.

To rerun retrieval use `python -m eval.student_quality_audit --output <new-path>`;
add `--cases eval/student_quality_holdout_set.jsonl` for validation or `--live-ids
all` for live answers. To isolate generation, pass `--replay-retrieval <frozen-trace>`.
To reproduce the original generation pass `--baseline-code
eval/results/student_quality_baseline_code_20261007` as well. Do not overwrite old
records or rebuild an index during a running audit.

The next measured slice should address controlling department evidence, attribute
follow-ups and coaching-versus-policy-status together, then rerun these same cases
and independently sourced student questions. Source-owner review and independent
human calibration remain required before trusted accuracy claims or release.
