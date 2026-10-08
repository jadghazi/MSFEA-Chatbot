# Current architecture and project state

Reviewed 2026-10-08 against the paid student/Studio release and its bounded rollout correction.
The behavior below is deployed on Oracle; the [release receipt](archive/oracle-paid-release-20261008.md) identifies the exact application commit. This is the current checkout map.
Defaults below describe code/example configuration; a deployed `.env` can override
them. Deployment observations are dated evidence, not a live monitoring snapshot.

## State and limits

The source-backed CDC knowledge base, standalone student pilot, embeddable widget,
department scoping, bounded follow-ups, feedback/usage dashboard and guarded
Knowledge Studio are implemented. Oracle deployment was verified through the
2026-10-08 paid student/Studio release. The [October rollout record](archive/oracle-studio-deployment-20261001.md)
documents the serving topology and unchanged 253-chunk source index at that rollout.
The latest private-draft behavior is recorded in [ADR-0031](decisions/0031-advisory-ai-drafts.md).

Wider pilot/email-deflection outcomes, AUB-page integration, institutional ownership
and independent human calibration remain open. Deterministic retrieval gates have
known misses; see [evaluation](../eval/README.md) and [backlog](backlog.md).
Do not infer 100% policy correctness from passing checks.
The [main-model evaluation](../eval/results/student_quality_main_model_20261007.md)
records configured-model verification, held-out actual-history conversations and
retained failed experiments. Earlier alternate-model measurements remain separate.
The local audit and subsequent Oracle rollout are separate measurements.
The earlier Lite-model verification was interrupted by project/model daily quota.
The deployed paid student profile uses `gemini-3.8-flash` with medium thinking,
a 4096-token output ceiling and deprecated sampling fields omitted. Its constructed-set
engineering acceptance is complete; see the [paid audit](../eval/results/student_quality_paid_migration_20261008.md)
and [ADR-0032](decisions/0032-paid-student-profile-and-context.md). Local and Oracle `.env`
profiles are aligned. Policy-owner acceptance and independent calibration
remain separate. The dated reports retain earlier incomplete Lite measurements.

## Sources and ingestion

Official originals live in `kb/source/`. Reviewed Markdown in `kb/normalized/` is
the file-backed ingestion input; extracting and reviewing originals is a separate
step. Approved staff entries are immutable PostgreSQL revisions, not edits to an
official document. A rebuild reads normalized files plus each active revision.

`ingestion/chunking.py` splits by section and line-aware windows (defaults 500
characters, 150 overlap), keeps tables atomic and wrapped Markdown paragraphs or
bullet continuations intact, inherits department scope in nested
sections and excludes editorial provenance sections. Oversized lines/tables can
exceed the normal window size. `ingestion/embeddings.py` uses pinned local
`BAAI/bge-small-en-v1.5` weights with a fingerprint.

Heading-only parents, scope-only annotations and empty windows are excluded from evidence. Reviewed topic
overviews can carry `<!-- content_role: overview -->`; ingestion removes the marker
from canonical text and stores the role as metadata. Their title and first purpose
sentence supply a compact, deterministic embedding representation; the complete
canonical paragraph supplies factual evidence and full-text search. These summaries reorganize
existing verified facts and retain source provenance; detailed rules and department
exceptions remain authoritative. Broad orientation requests may reserve one relevant
overview from a small, department-scoped semantic search, subject to the existing cosine
threshold and proximity to the strongest semantic match. Focused retrieval keeps
its normal ranking and department safeguards.

`retrieval/store.py` owns PostgreSQL chunks, canonical text, optional retrieval text,
source/section metadata and generation/model identity. Embeddings are computed
before atomic replacement. Ingestion, publication and retirement share a write
lock; a stale rebuild aborts if the active generation changes. Never hand-edit vectors.

Canonical text grounds answers and supplies keyword search. A focused curated entry
can have a separate, reviewed representation for embeddings after measured search
repair. This text never becomes factual answer evidence. See [curation](curation.md).

## Student request path

1. The shared vanilla-JavaScript widget sends the question, selected department,
   ephemeral session ID and bounded page history. `frontend/` hosts the standalone
   page; `dashboard/` serves the protected staff dashboard.
2. `api/app.py` applies input/body/rate/concurrency guards and best-effort local
   redaction. Whole-message greetings/acknowledgements/noise can return locally.
   Exact effective requests in a session can replay a 30-second response.
3. `generation/conversation.py` deterministically resolves follow-ups. Explicit
   new subjects take precedence; ambiguous references can search literal and
   contextual queries. Assistant history is never policy authority. No second
   LLM query-rewrite call is deployed (ADR-0027). Capability orientation accepts
   conversational prefixes such as “So” or “Okay” without inserting a topic list.
   An explicit abandoned-topic preface is omitted from retrieval only when the
   remaining question is self-contained; generation retains the original wording.
   Short attribute searches retain the relevant actor or program rather than its
   goal phrase. Generic report/form follow-ups retain the current program.
   Relationship questions retain a referenced operand even when the other
   operand is named. Numbered subject identifiers remain intact; "no longer"
   means cessation, not duration. A detailed pronoun follow-up retains
   current-topic student questions for referent verification; earlier assistant claims are omitted from those longer
   restatements. Detailed independent questions still omit history.
   Required-item questions ask for ordinary applicable obligations before conditional
   arrangements; substitution questions compare explicitly required items and honor
   documented substitution rules. These cues contain no program facts.
4. `retrieval/store.py` fuses vector and PostgreSQL full-text rankings with RRF.
   Normal depth is 7; explicit comparisons use at least 12. Selected departments
   exclude other departments' rules and can reserve relevant own-department evidence.
   With unknown department, applicable department labels remain explicit.
   Attribute follow-ups add a topic-and-attribute full-text path to the existing
   fusion. Bounded spelling suggestions use active approved-source vocabulary,
   protect known tokenizer words, and require unique nearby spellings plus
   retrieval support. Supplemental spelling passages cannot authorize generation.
   Reviewed `evidence_links` restore the seed section's complete windows and
   canonical companion sections after ranking,
   applying the same department filter. These one-hop companions preserve scoped
   exceptions and conditions; they also cannot authorize the similarity gate.
   For explicit later employment/retention questions, reviewed `entry` evidence
   is excluded before vector/keyword ranking and companion expansion. Unknown
   stages remain eligible; this conservative constraint does not resolve every
   implicit stage or service boundary.
5. `generation/answer.py` builds bounded canonical evidence. The strongest retrieved
   primary cosine in the actual answer context must clear 0.60; otherwise the
   request escalates without generation. A reviewed service directory can carry
   `content_role: catalogue`. When the leading primary result has exactly one
   reviewed program scope, unrelated unlinked catalogue passages are omitted.
   Directory-led, mixed-scope and unknown-scope questions retain them; explicitly
   linked companions remain intact. This limits service bleed without a fixed
   question-to-topic map.
   A 24,000-character context ceiling asks for a narrower question rather than
   silently discarding policy conditions.
   Definitive later employment/retention questions additionally require approved
   `post_completion` evidence. Without it, the request escalates before the LLM;
   silence cannot establish either a guarantee or a no-guarantee policy. General
   career-help questions can still use documented support. A stage label establishes
   relevance, not correctness of every possible claim.
   A focused Studio revision can carry one reviewed stage marker in its immutable
   answer; chunks retain its scope and strip the marker from factual text. No stage
   is guessed for untagged revisions. A read-only Oracle inventory on 2026-10-07
   found no active approved staff revisions; this is a dated parity check, not a
   guarantee for future revisions. Review new revisions and any withheld
   legitimate later-outcome facts before release.
6. The provider in `llm/` produces the grounded answer/refusal. Citation labels are
   checked against retrieved sources. Responses display citations and disclaimer.
   Web destinations must occur in the supplied factual evidence; unsupported
   Markdown destinations become plain captions and other unsupported web URLs
   are omitted. This checks links, not the factual grounding of every sentence.
   A wholly empty missing-information acknowledgement routes to the configured
   human contact; useful partial explanations and documented negatives remain.
   Provider outages/quota errors are distinguished from knowledge refusals and give
   a retry path.

The answer contract distinguishes broad orientation from precise decisions, permits
supported partial explanations while identifying missing facts, and asks for
clarification when a referent is unclear. A wholly elliptical question without
an earlier subject can receive a local clarification before retrieval. Capability
questions retrieve a source-backed CDC service overview rather than a fixed topic
list. Policy, department, citation and similarity guards remain in force.
The student prompt explicitly distinguishes the current request from earlier user
requests: history resolves references but does not supply another task to complete.
Generic intent frames separate hypothetical arithmetic, policy relationships,
substitution decisions and requests to verify individual records. They encode
answer style and capability limits, not course facts or question-specific answers.
Quantity questions distinguish minimums, maximums and estimates. Applicability
includes process stage: an admission rule does not establish employment after
completion. Conversational filler cannot by itself justify scoring an unresolved
pronoun query. Retrieval wording and the student's generation intent remain separate.
Short fee, duration, contact and link follow-ups retain the current user topic.
Attribute answers identify a missing value and can offer a verified contact or
resource for that topic, rather than returning its definition or guessing a price.
Ordinal references and minimum/maximum follow-ups use current-topic user wording,
not an earlier assistant claim. Ambiguous service-menu sign-ups ask for a subject.
An explicitly linked canonical ancestor already in supplied evidence is presented
before its child; this changes context order, not primary scores or threshold
authorization. Correct evidence and passing gates still require live answer review.
Future requests for job-search assistance retain documented support; explicit
employment guarantees and hiring decisions still require evidence for that stage.
7. `observability/` stores anonymized interactions/retrieval labels, feedback and
   provider usage/latency. Provider failures do not become unanswered-content work.
   `experience/` separately stores anonymous experience feedback.

The protected Usage view aggregates persisted interactions over 7/30/90-day UTC
windows. Answer rate excludes provider errors; helpfulness covers submitted
ratings only. Neither establishes answer accuracy, unique students or email
deflection. Process-local usage counters are separate from durable analytics.

The browser allows six completed questions per chat. The API history limit is eight
messages of at most 1,200 characters each; questions are at most 2,000 characters.
There is no persistent student account or server conversation store.

## Staff maintenance path

Both Needs attention and Add knowledge enter the same Describe → Resolve → Preview
→ Publish workspace. The private worker retrieves related evidence, compares literal
claims, generates focused test questions and independently verifies review coverage.
Routine preparation uses four staff-model calls; clarification can stop earlier.
Structured output/quote checks and durable stage records make the advice inspectable.
The local Studio alignment retains program/process-stage labels and reviewed
controlling evidence in comparisons and optional writing. Multi-window curated
sources restore their own immutable revision bundle through the existing one-hop
expansion. Positive publication tests use the student's final answer context.

Optional answer writing normally uses two staff calls. It remains available during
policy conflicts and shows the proposed answer with highlighted changes, supporting
facts, missing details and advisory warnings. Factual/source concerns no longer hide
a usable private draft. Malformed output, privacy and stale-context failures can
still prevent a draft. Accepting/editing requires fresh main review.

Source confirmation creates an immutable draft. Seven deterministic checks run on
a separate validation database. A measured search failure can trigger one bounded
search-only repair without changing facts, scope or original tests. Actual student
model previews are separate LLM calls. Named human approval and valid checks are
required before atomic publication; linked feedback resolves after serving smoke.
Saved previews bind to the student model/settings and generation/provider code.
A changed profile requires fresh previews; valid source checks and prior attempts
are retained. This local Studio candidate is not deployed to Oracle.
[Studio guide](studio.md) explains staff actions; [curation contract](curation.md)
describes exact gates and recovery.

## Providers, budgets and topology

Student `LLM_MODEL` and staff `CURATION_LLM_MODEL` are independent configuration.
The local/example student candidate is `gemini-3.8-flash`; staff defaults to
`gemini-3.1-flash-lite`. Gemini is the only implemented production adapter.
The student API profile omits temperature/seed and explicitly sets medium thinking.
The output ceiling includes reasoning and visible text; it is not a word target.
Legacy sampling remains configurable. The aligned staff flow retains the existing
Lite review/writing profile; previews use the current student profile. This local
configuration does not update Oracle.
Admission defaults are 400 staff attempts/day/model, 12/minute, and 60 student-model
preview calls/day. These are app budgets, not provider guarantees or entry counts.
The local 500/day demo override does not change the production default.
Retries also use quota; verify the project's actual allowance before changes.

Production runs app, application PostgreSQL, private worker, self-hosted n8n,
n8n PostgreSQL and Caddy. Validation uses a separate database on the application
PostgreSQL server, not a seventh permanent container. Bootstrap jobs initialize
validation and import/publish the Git workflow, then exit. Student chat is independent
of n8n; n8n sequences checks/publication IDs and cannot approve content.

Use one application worker/instance: short-term rate limiting, request concurrency,
response cache and legacy usage counters are process-local. Daily IP/chat admission,
paid attempt/token/cost ceilings, provider concurrency and operator pause are durable
in application PostgreSQL and shared by app/worker. Every Gemini generation attempt,
including retries, is admitted before the SDK call. Complete usage includes reasoning;
uncertain attempts retain conservative reservations. A protected Paid usage & controls
tab exposes the shared ledger and pause/resume. Environment override and cooldown
remain independent. See the paid-call section in operations for bounds and Google
project controls; app estimates are not the provider balance. API admission limits and backup/recovery procedures
are in [operations](deployment.md). Persistent application records are authoritative;
n8n execution history and process counters are not audit or billing ledgers.

## Verification boundaries

CI measures retrieval/evidence preservation, thresholds, conversation routing and
publication/conflict coverage without live provider calls. Live answer correctness,
staff suggestions and previews require separate source-based review. Independent
human calibration is still pending. Best-effort redaction and natural-language AI
checks are safeguards, not guarantees. See [evaluation methods](../eval/README.md).
