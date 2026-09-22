# KB Publication Guard — senior engineering review and implementation plan

Date: 2026-09-15. Reviewed local HEAD: `6a7695e`.

## 1. Decision

**Build guarded curation with self-hosted n8n Community Edition as the required workflow coordinator. Conflict review by a human is the primary publication safeguard. Preserve the current student-answer behavior and limit KB work to demonstrated metadata/provenance gaps.**

The proposal fits the existing CDC content-maintenance scope. Drafts, source review, department checks, and safe publishing address real deficiencies. They do not require a new student portal, provider, or hosted vector database.

The user has selected n8n for practical workflow coordination and experience with a new tool. Implement the Python validation/publication functions first, then connect them through n8n before deployment. This is implementation order, not an optional n8n phase. FastAPI owns authorization, results, and publication; n8n sequences steps and handles workflow retries. Do not build a parallel Python workflow orchestrator. A bounded Python job executor and webhook dispatcher support n8n without duplicating its sequencing.

### Confirmed user priorities

- Include n8n in the delivered feature, behind the existing admin dashboard and outside student chat.
- Flag potential conflicts and require a recorded human decision before publishing; do not promise automatic detection of every contradiction.
- Use no paid services for required publication checks. Verify existing Oracle headroom; if insufficient, report the constraint rather than provisioning paid resources.
- Preserve the bot's current answer style, model, grounded citations, refusals, and follow-up handling.
- Perform targeted KB repairs, with isolated evaluation and rollback, rather than a wholesale content rewrite.

### Scope clarification accepted on 2026-09-19

The dashboard supports two deliberately separate kinds of focused entry:

1. A correction/restatement backed by an existing reviewed official source. It must
   identify the exact normalized document, section, and excerpt.
2. New CDC knowledge that is not present in an existing file. The immutable submitted
   revision is itself a first-class, database-backed source document with a stable
   `KB-<entry>` identity, title, contributor label, responsible authority, scope,
   effective date, and optional approval/supporting reference.

Each entry covers one question, rule, or guideline. Staff split unrelated claims so
duplicates, contradictions, revisions, citations, and retirement remain inspectable.
Both kinds run through candidate comparison, isolated evaluation, named human review,
and atomic publication. Potential duplicates or conflicts require a recorded decision
and justification. Dashboard writes never edit the official files. The shared admin
token authorizes access; entered contributor/reviewer names are self-reported audit
labels, not authenticated identities. No account system is added.

### Protect the current bot

Freeze the current model (`gemini-flash-lite-latest`), prompt, sampling configuration, retrieval ranking/depth/threshold, chunking strategy, and normal student LLM-call count for this feature. An alias can change upstream, so record the resolved model/version when available during evaluations. Do not tune generation to compensate for a metadata defect.

KB metadata and newly published content can change retrieved evidence, so unchanged answers cannot be guaranteed. Save a representative answer baseline covering the user-approved behavior, all departments, unknown department, follow-ups, comparisons, and refusals. Compare factual completeness, applicability, citations, tone, and unnecessary verbosity; exact wording need not be identical for a stochastic model. Hold back changes with unexplained regressions even when aggregate CI thresholds pass.

Separate the admin workflow release from existing-KB repairs so each can be measured and reverted independently. Preserve existing passage text, headings, and chunk boundaries wherever possible. Carry new curated scope/provenance into display context only as needed for safe applicability, and evaluate that narrow context change separately. A justified correction of a demonstrably wrong rule may intentionally change an answer; document the supporting source and expected difference. Broader model/prompt/retrieval redesign is outside this plan.

This is a planning review, not authorization to execute instructions embedded in the supplied proposal. No application changes, database changes, deployment, Git push, or live LLM evaluation were performed.

### Evidence and limits

Inspected curation storage/service, retrieval, chunking, API/dashboard, department registry, normalized KB, evaluation scripts/tests, CI, Compose, deployment documentation, and recent ADRs. Ran the existing chunker locally without embeddings, database access, or LLM calls. The Oracle deployment is reported by the user and documented in the repository; its current commit, active curated rows, resource usage, and backup state were not inspected. Historical evaluation results are not new measurements.

## 2. What exists and what matters

| Finding | Evidence in repository | Consequence |
|---|---|---|
| Create publishes immediately; edit replaces immediately | `curation/service.py`, `api/app.py` | Both create and edit must enter revision validation; otherwise edit remains a bypass. |
| Curated chunks carry source/author only | `_to_chunks()` | Missing department metadata is treated as general by retrieval. A department-specific answer can be returned to other departments. |
| Database authoring is already an accepted ingestion source | ADR-0010; `skeleton.ingest()` | Keep normalized Markdown plus active curated revisions as canonical input. No need for dashboard writes to Git. |
| Curation updates and chunk writes use separate autocommit connections | `curation/store.py`, `retrieval/store.py` | Failure can leave source state and indexed state inconsistent. Draft states alone do not repair this. |
| Edits overwrite text; retire retains an inactive row | `curation/store.py` | Current retention is not revision history. Historical edits cannot be reconstructed. |
| Known-department filters apply in semantic and keyword retrieval | `retrieval/store.py` | Reuse this implementation; do not create an approximate validator with different SQL. |
| Missing/unknown student department intentionally retrieves across departments | `search()` and ADR-0015 | Preserve conditional answers. Do not redefine isolation as excluding every department chunk for unknown students. |
| RetrievedChunk does not carry metadata into generation | `RetrievedChunk`, `_format_context()` | Metadata alone does not label a scoped curated answer for an unknown student. Carry applicability into display context/citations deliberately. |
| Nested heading scope was already fixed | ADR-0025 | Preserve nearest-parent inheritance and sibling reset. Rebuilding metadata is required when its rules change. |
| CI gates retrieval, threshold, synthesis; live answer evaluation is separate | `.github/workflows/ci.yml` | Do not claim that passing CI proves semantic correctness or that full live answer evaluation is free of quota costs. |
| Curated eval cases derive expectations from the same answer | `eval/curated_cases.py` | Useful retrieval checks, not independent evidence of correctness. They also omit department and can silently skip on DB failure. |
| API invalidates a process-local answer cache on curation | `api/app.py`, deployment docs | Preserve invalidation for publish, retire, compensation, and rebuild, including callbacks initiated by a worker. |
| Caddy currently proxies all paths | `deploy/Caddyfile` | New internal routes are publicly reachable through Caddy unless explicitly denied or served separately. A private container port alone is insufficient. |

## 3. Does the KB need restructuring?

### Measured structural inventory

The local chunker produced **210 document chunks**, excluding database-curated content:

| File | Chunks | Department metadata | Program metadata |
|---|---:|---|---|
| CDC knowledge base | 35 | 35 general | Every chunk inherits six comma-separated programs |
| Email clarifications | 47 | 29 general, 16 ECE, 2 MECH | Missing |
| Presentation template | 5 | General | Internship |
| Report templates/rubrics | 36 | General | Internship |
| CO-OP handbook | 50 | General | CO-OP |
| Summer guidelines | 37 | 31 general, 1 MECH, 1 ECE, 1 CHEM, 2 IEM, 1 CEE | Internship |

These counts are a structural baseline, not a quality score. Fewer department chunks can reflect shorter source sections. They do not establish that a department's guidance is incomplete. A simple scan found no general chunk containing the literal parenthesized department abbreviations; that does not prove semantic scope is correct.

### Recommended repairs

1. **Keep the current source/normalized layout.** Copying common rules into five department folders introduces duplicated policy that can drift. General rules and department exceptions should remain separately identifiable.
2. **Audit high-risk rules across all five departments:** duration, 6+2 and 4+4 arrangements, concurrent summer courses, eligibility, remote work, reports, presentation requirements, and deadlines. Produce a matrix of rule, scope, source passage, effective date if known, and unresolved ambiguity. Ask the policy owner to resolve ambiguity; engineers must not invent a rule.
3. **Repair email-clarification provenance.** Its frontmatter currently has only title and department. Add verified source identity, program, approval reference, and update information. Missing dates remain explicitly unknown; do not manufacture dates from file timestamps.
4. **Treat `all` as a positive applicability claim.** It must mean the source supports general applicability, not that scope was omitted. New curated content with missing/invalid department must fail validation. Review legacy general content rather than automatically assigning it to a department.
5. **Add a small version-controlled section metadata manifest where document defaults are inadequate.** Use stable document/section IDs mapped to heading paths, department, program, and source locator. Validate that each referenced heading resolves uniquely. Preserve current heading inference as a fallback during migration; conflicting explicit metadata and inferred scope should fail the audit. Use the same resolved metadata for all child windows. Avoid a bespoke policy language.
6. **Program means CDC offering/topic**, such as internship or CO-OP, not the student's degree. Use a data-backed registry populated from reviewed content. The current comma-separated frontmatter is not a structured list and retrieval does not filter by program. Clean section-level program labels for provenance/testing; do not add a hard program filter in this change. It could break internship-versus-CO-OP comparisons.
7. **Preserve general-rule/exception relationships.** The general presentation guidance and ECE voice-over guidance, and general remote-work prohibition with IEM exceptions, need clear applicability. Do not erase one side as a duplicate. Add explicit reviewed exception/supersession links only where useful; do not infer universal precedence from a newer date.
8. **Preserve measured chunking decisions**, including atomic tables, overlap, and nested scope. File splitting or heading renaming can change chunk IDs and rankings. Evaluate any such change independently before combining it with curation changes.
9. **Correct KB maintenance documentation.** `kb/README.md` incorrectly mentions a vector index in `data/`; storage is PostgreSQL. Its update instructions must explicitly include normalization/review before ingestion. Ingestion currently rebuilds from normalized Markdown plus curated database rows; it does not automatically re-extract original documents.

**No broad rewrite is justified by this audit.** The most concrete immediate scope defect is curated-answer metadata, not the department folder structure. An exhaustive source-fidelity review of the original PDF/DOCX/PPTX is still separate work.

## 4. Revised publication contract

### Draft and source review

Required fields on a publishable revision:

- Question, proposed answer, department, program/topic ID(s).
- Supporting source reference(s), stable section/page locator, and evidence excerpt/hash.
- Representative test question plus a paraphrase; expected supporting evidence and applicability.
- Change reason and linked feedback item IDs, when applicable.
- Recorded source-review decision and reviewer label at final publication.

Support more than one evidence reference when an answer combines documented conditions. A source dropdown plus arbitrary page text does not prove grounding. Validate source existence, evidence location, and version/hash. Do not fetch arbitrary administrator-provided URLs server-side.

An authorized clarification can itself be an approved source, consistent with ADR-0010. Record its authority/approval evidence explicitly. Do not force an unrelated document citation when the rule came from a new clarification. For MVP, register that approved clarification through the existing reviewed content intake; defer document-upload integrations.

The shared admin token authenticates an admin role, not an individual. A reviewer name entered in the dashboard is self-reported. Preserve that limitation in the audit record; do not claim individual attribution or two-person approval. No new account system is required here.

### Logical data model

Extend the curation subsystem with these responsibilities; final table names can follow existing conventions:

- Stable curated entry with an active-revision pointer.
- Immutable submitted revisions containing text, applicability, evidence, hashes, and predecessor.
- Validation runs and individual step results with errors, case IDs, and tested fingerprint.
- Publication/audit events recording state transitions, actor type, reason, and timestamps.
- Durable pending work, attempts, and retry timing. Use an outbox for n8n webhook dispatch and durable validation-run records for bounded Python step execution.

Fingerprint the revision, source content, active KB generation, embedding fingerprint, relevant retrieval/generation configuration, evaluation-set hash, application commit, and validator version. Any change that affects a check invalidates its result. A workflow execution ID is diagnostic metadata, never publication authority.

Suggested states: Draft → Validating → Blocked or Ready → Publishing → Active → Retired. Failed publication returns to Blocked with a failure event. Keep run failures/timeouts distinct from content failures. An existing Active revision remains active while its replacement is Draft/Validating/Blocked. An edit creates a new revision; it never mutates the active one.

### What each check actually proves

| Check | Required outcome |
|---|---|
| Schema and source | All required fields valid; scope canonicalized; evidence resolves to the declared source version; privacy requirements satisfied. |
| Duplicate/conflict review | Exact duplicates detected; overlapping-scope similar content surfaced for review; unresolved contradictions block. Similarity cannot prove absence of contradiction. Record explicit reviewer resolution for flagged exceptions. |
| Positive retrieval | Intended revision evidence is in production top-k and passes the existing similarity gate for representative question and paraphrase. Match revision/chunk identities and evidence, not just `admin-curated`. |
| Department isolation | Every candidate window has correct scope. Other known departments cannot return those windows through semantic, keyword, or fallback paths. |
| Unknown department | Scoped evidence stays explicitly labeled in model context and citation/display. Reviewed answers qualify applicability or ask for department when necessary. Retrieval success alone does not prove this answer behavior. |
| Regression | Existing retrieval/threshold/synthesis gates pass; report per-case before/after, with no newly lost previously passing evidence. New cases must not hide old losses in the average. |
| Human review | Reviewer checks policy truth, conditions, authority, and conflicting evidence. Mandatory independently of automated checks. |

Freeze independent high-risk cases. Current runtime-derived curated cases should remain a separate metric, carry department/evidence identity, and fail closed if unavailable during a publication gate. Do not replace the source-based golden set with self-derived expectations. One question is inadequate when an answer contains multiple rules: split the draft or cover each independent condition.

### Mandatory conflict-review workflow

For every new or edited revision, Python searches the existing normalized KB and active curated revisions using semantic and keyword retrieval. Search using the question and answer claims, deduplicate passages, and include general rules, same-department rules, explicit exceptions, and linked source/supersession passages. Do not limit this review to the student top-k: use a separately evaluated review candidate depth and include directly linked evidence regardless of rank. Other-department differences can be shown with clear scope labels; they are not automatically contradictions.

The dashboard shows the draft alongside related passages, department/program, conditions, source locator/version, and a reason for each potential-conflict flag. Exact duplicate checks and candidate retrieval are deterministic. Similarity is a relevance signal, not proof of contradiction or consistency. Show related evidence for mandatory human review even when there are no flags; label that outcome “No potential conflicts flagged,” never “Conflict-free.”

The reviewer records one of these outcomes with a reason:

- Correct the proposed answer: create a new revision and rerun affected checks.
- Reject the draft: keep it unpublished and retain the decision.
- Confirm no conflict or a valid scoped exception: retain the supporting evidence and explanation.
- Approve replacement of an outdated rule: identify the exact superseded content and authority. For a curated predecessor, replace it atomically. For a Markdown rule, first update/review the canonical source input and re-ingest through the existing process; do not leave an obsolete contradictory rule active beside its supposed replacement. Revalidate against the resulting KB generation.

Potential-conflict flags hold the revision in Blocked with reason “Human review required.” If automatic checks pass without flags, Ready means “Ready for human review and publication,” not policy-approved. Every Publish action requires recorded source/conflict review for the exact revision and KB fingerprint, whether flags existed or not. A review decision can resolve a potential conflict but cannot waive failed evidence, scope, regression, or stale-validation checks. Edits or relevant KB changes invalidate the review.

Add a frozen conflict-review evaluation set containing a same-scope contradiction, paraphrased contradiction, exact duplicate, valid department exception, differing conditions, outdated source replacement, and a no-conflict case. Measure whether the relevant conflicting passage appears in the review candidates, separately from student retrieval recall. Require every designated high-risk conflict fixture to surface its evidence; report false-positive flags and known missed cases. This measures coverage on the test set, not a guarantee about all future natural-language conflicts. Test the mandatory human gate even for unflagged drafts. No LLM conflict judge is required for MVP.

## 5. Candidate evaluation and safe publication

### Evaluate without touching live retrieval

Use a **separate validation database on the existing PostgreSQL server** for the MVP. Populate it from a consistent snapshot of normalized content plus active curated revisions, replace the previous revision of the edited entry, and add the proposed revision. Reuse the production chunker, embeddings, and retrieval functions against that database. Keep the same table names and schema to minimize SQL divergence.

This intentionally allows unpublished vectors in the isolated validation database; only active content belongs in the student-serving database. Never temporarily insert a draft into live `chunks`, run tests, and delete it afterward. Never run existing destructive DB tests against production. A dedicated Python process with its own configuration owns the validation connection; do not mutate global application settings per request.

Start with one validation job at a time and explicit CPU/memory limits. Run the expensive embedding/evaluation work outside the student API request process. This can use the existing application image with a worker command; it does not need Redis, Celery, or a second vector service. Decide whether CPU/RAM headroom supports this before Oracle deployment.

### Atomic publication

1. Administrator submits Publish for the exact Ready revision and run ID.
2. FastAPI checks admin authorization, stored review, all check results, and matching fingerprints. A changed KB/source/revision returns a specific stale-validation error and schedules revalidation.
3. Prepare embeddings outside the write transaction. Recheck fingerprints under the publication lock afterward.
4. In one database transaction, switch active revision, replace the entry's chunks, increment KB generation, and record the publication event. Refactor repository methods to accept a shared connection for this operation; current independent autocommit calls cannot provide atomicity.
5. Commit, invalidate cached answers, and run a bounded, uncached retrieval/readiness smoke check through the serving configuration. Resolve linked feedback only on successful activation; saving a draft must not resolve it.
6. On smoke failure, restore the prior revision and its chunks transactionally, or deactivate a newly created entry. Record the failed attempt, invalidate cache again, and keep/reopen feedback for review.

Serialize publish/retire/rebuild commits using a shared database lock plus a generation check. Current full ingestion reads curated rows before indexing, so a concurrent publish can otherwise be overwritten by a stale rebuild. Do not hold locks while embedding. If generation changes during preparation, retry with a fresh snapshot.

Compensation must compare the active revision: a delayed failure from publication A must never roll back a newer publication B. Treat a reactivation requested later as a new publication requiring validation against the current KB. Immediate compensation to the previous revision and later discretionary rollback are different operations.

Post-commit smoke rollback cannot retract answers already served in the short exposure window. Strong prepublication checks are essential. The MVP should document this bounded risk, use deterministic smoke checks, and persist recovery work before commit so a process crash cannot leave an untracked Publishing entry. Cache generation checks must also cover requests already in flight; invalidation alone can allow an old request to repopulate stale results.

## 6. Required n8n integration and reliability boundaries

Implement one `KB Publication Guard` workflow with a validation branch and a separate publish-event branch. Do not leave a workflow waiting indefinitely for a human click. The publish branch can execute only a publication intent already authenticated and recorded by FastAPI; an n8n token cannot create that intent or approve content.

- Browser talks only to FastAPI. Student `/chat` has no dependency on n8n or validation readiness.
- FastAPI owns outcomes. n8n requests named steps and reports execution progress; it cannot submit `passed=true` as trusted proof or assign Ready directly.
- Persist the draft and dispatch event in one transaction. A dispatcher retries lost webhook delivery. Webhook returns promptly; long evaluations return a run ID for status polling.
- Every request binds to revision/run/step and an idempotency key. Duplicate deliveries return the existing result. Stale/out-of-order callbacks cannot advance state.
- Use bounded retries for transport/transient failures. Content failures do not retry into a pass. Reconcile expired leases and abandoned runs after restarts; n8n execution history is not the audit source of truth.
- Use separate dedicated service credentials, narrow endpoint authorization, constant-time secret comparison, redacted logs, fixed destinations, and no browser exposure. Keep policy text/student feedback out of n8n payloads when IDs suffice.
- Deny internal API routes at Caddy. Keep n8n off published ports; access its editor only through an operator tunnel when needed. Confirm this from the public hostname in integration tests.
- Give n8n a separate database/user with no application-table permissions. Persist its encryption key and required state; keep sanitized workflow exports in Git. Use a pinned supported image compatible with the Oracle architecture, execution retention limits, and resource limits. No Docker socket, shell-execution nodes, community nodes, or unrelated integrations are needed.
- Back up application revisions/audit independently of n8n execution pruning. Back up n8n database and encryption key securely, and rehearse recovery. Existing backup scripts target the application database and must be reviewed for the added database.

This is a justified reliability mechanism once asynchronous publication is chosen. Do not expand it into a general workflow platform.

## 7. Implementation sequence and review gates

Each step should be a focused reviewable change. Finish its gate before moving on.

### Step 0 — freeze baseline and record the agreed architecture

- Record deployed commit, image/model configuration, Oracle CPU/RAM/disk headroom, active curated count, and verified backup/restore procedure. Read secrets without printing them.
- Run existing tests/evals in the isolated development database. Save per-case outputs, not just percentages. Record current answer-suite results separately with provider/model and sampling settings.
- Write an ADR recording n8n Community as coordinator, Python as validator/publication owner, mandatory human conflict review, and legacy treatment. Record the answer-preservation baseline and zero-paid-service constraint.
- Exit: reproducible baseline and resource feasibility, with unresolved policy questions identified.

### Step 1 — scope/provenance audit and regression cases

- Build the rule matrix from section 3, with source-owner review where needed.
- Add failing tests for unscoped curated chunks, all-department matrix, unknown student department, nested scope, and scope labels reaching generation.
- Add independently grounded paraphrase, condition-boundary, and follow-up cases for risky rules. Keep existing thresholds unchanged.
- Exit: targeted source/metadata repairs measured against the baseline. No wholesale KB rewrite.

### Step 2 — revisions and safe migration

- Add explicit versioned migrations, revision/run/event storage, and constraints. Do not rely solely on scattered `CREATE TABLE IF NOT EXISTS` for this change.
- Preserve old IDs and active content as a legacy revision with `needs_review` provenance status. Do not mark it validated or silently infer `all` as approved.
- Inventory legacy entries before rollout. Review high-risk scope gaps before allowing the new guard to claim corpus-wide isolation; preservation alone does not make existing content safe.
- Backfill only history that exists. Do not fabricate past authors or overwritten versions.
- Exit: migration rehearsed on an isolated backup; content/count parity verified; old application rollback compatibility explicitly tested or ruled out.

### Step 3 — draft API/dashboard

- Change create to save draft; change edit to create replacement revision; expose revisions, evidence, status, and actionable failures.
- Preserve existing dashboard and vanilla JS. Add source/scope controls populated by FastAPI, revision diff, and final review/Publish.
- Disable old immediate-publication routes/semantics so they cannot bypass checks. Wire feedback resolution to successful publication.
- Exit: draft/edit cannot alter student retrieval, including after restart/re-ingestion.

### Step 4 — validation engine

- Implement isolated candidate database, durable job execution, shared production retrieval, source checks, overlap review, and department matrix.
- Keep deterministic checks API-free. Store reproducibility fingerprints and strict result completeness. Implement the mandatory conflict-review workflow and its independent candidate-coverage tests from section 4.
- Exit: deliberately wrong scope/evidence and stale or missing runs block with precise reasons. Preview generation is optional and explicitly quota-budgeted.

### Step 5 — transactional publish, retire, recovery

- Implement final authorization, atomic revision/chunk switch, shared rebuild coordination, durable smoke recovery, and safe compensation.
- Preserve existing active revision during editing. Record retirement reasons; removal must work without n8n being healthy.
- Exit: fault-injection tests cover failures before/after commit, duplicate Publish, concurrent edit/publish/rebuild, delayed callbacks, and cache invalidation including in-flight requests.

### Step 6 — independent quality review

- Run all existing CI gates: Ruff, strict mypy, Python tests, widget tests, retrieval floor (`0.90` currently), threshold, and synthesis gates.
- Require no newly lost passing evidence cases and zero candidate cross-department retrieval in the test matrix. Report per-department results separately.
- Run/review targeted live answer cases for unknown department, exceptions, refusals, and follow-ups before releasing applicability-context changes. Maintain the selected provider/model and normal request count. Keep per-draft automatic publication checks deterministic; do not advertise them as complete answer-quality certification.
- Exit: metric report and human review attached, with known baseline failures preserved explicitly rather than hidden.

### Step 7 — required n8n integration

- Add the single workflow, protected calls, outbox delivery, timeouts, reconciliation, isolated database, and operator-only access described above.
- Exercise workflow import from Git and repeat webhook deliveries. Stop n8n during validation and after publication intent; confirm safe recovery and working chat.
- Exit: n8n adds orchestration without owning policy or creating a publication bypass.

### Step 8 — deployment and handover

- Rehearse against an isolated restored database. Back up production, verify resource headroom, and deploy the exact tested commit with the documented migration.
- Rebuild through the normal ingestion path if metadata changed; coordinate curation writes and cache invalidation. Check HTTPS health/readiness and representative department answers.
- Verify no internal route is publicly accessible and no new container is unexpectedly exposed. Confirm backup timer and off-VM recovery copy.
- If deployed n8n fails, disable dispatch while keeping drafts pending and student chat available. For application rollback, use a migration-compatible tested release; do not restore an old full DB dump over new student interactions as the routine content rollback.
- Document source intake, review, draft failures, publication, retirement, compensation, recovery, secrets, and ownership. Observe actual moderation volume and chat latency before adding more infrastructure.

## 8. Acceptance checklist for the implementation agent

- [ ] Draft save, draft edit, restart, and full ingestion cannot expose unpublished content.
- [ ] Every candidate window has explicit validated applicability; all five known departments are covered.
- [ ] Unknown/missing student department retains conditional guidance; invalid admin scope is rejected.
- [ ] Evidence and approval bind to immutable revisions and source versions.
- [ ] Missing, failed, skipped, timed-out, or stale checks cannot yield Ready/Publish.
- [ ] Duplicate/conflict review handles legitimate general-rule exceptions without silently suppressing either rule.
- [ ] Every draft requires human source/conflict review, including when no potential conflicts are flagged; the reviewer decision and reason are revision-bound.
- [ ] Conflict-review candidate coverage passes the frozen high-risk fixtures; no UI claims universal contradiction detection.
- [ ] Existing answer behavior is compared against the frozen baseline; unexplained factual, scope, follow-up, or style regressions block release.
- [ ] Required n8n integration is delivered without adding paid services or coupling chat availability to n8n.
- [ ] Validation never writes production chunks or consumes normal student request counters/cache.
- [ ] Passing automatic validation does not imply policy approval.
- [ ] Publish/retire/index state changes are atomic and rebuild-safe.
- [ ] Failed smoke restores the correct previous revision, preserves audit, and cannot undo a later publication.
- [ ] Cache and linked feedback stay consistent after publish and compensation.
- [ ] Legacy content survives migration without fabricated scope/approval/history.
- [ ] Existing eval gates pass; per-case and per-department regressions are visible.
- [ ] n8n outage leaves students operational and jobs recoverable.
- [ ] Tested backup, n8n workflow restoration, and application rollback instructions exist.

## 9. Can it run without paid services?

**The publication feature can have zero additional subscription/API cost. Zero additional infrastructure cost is conditional on the existing VM and storage having capacity.**

| Component | Cost assessment |
|---|---|
| Python validation, local embeddings, PostgreSQL/pgvector | Reuses current software and compute; no paid validation API required. |
| n8n Community/self-hosted | The Sustainable Use License permits internal business and non-commercial use; this internal university workflow appears consistent with that scope. Use only Community functionality. It is source-available under a restricted license, not unrestricted open source. |
| Oracle | Current official documentation lists 1,500 A1 OCPU-hours and 9,000 GB-hours/month, equivalent to 2 OCPUs/12 GB for Always Free tenancies. Confirm the actual tenancy allocation and existing workload before adding a worker/n8n. Idle free instances may be reclaimed. |
| Gemini | Required automatic checks can make zero Gemini calls. Preview/live answer evaluation consumes project quota and can incur charges on paid usage. Keep preview off by default; the feature does not make the existing chatbot unlimited or quota-independent. |
| Operations | Disk, backups, security updates, recovery, and maintainer time remain real costs even when the invoice is zero. |

Sources checked 2026-09-15:

- [n8n repository license](https://github.com/n8n-io/n8n/blob/master/LICENSE.md): internal/non-commercial license scope and separate enterprise-code terms.
- [Oracle Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm): compute allowances and reclamation conditions.
- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing): free/paid model tiers. Verify the actual project/model quota before live evaluation.

Several n8n documentation URLs returned missing pages during this review. Do not infer exact current Community feature entitlements or environment-variable defaults from stale tutorials; verify the pinned release's documentation when implementing. This plan does not depend on enterprise collaboration, SSO, or built-in Git integration.

## Final recommendation

Build **source-backed, department-aware, versioned curation with isolated validation and atomic publication**. That is the useful project upgrade. Apply narrow metadata/provenance repairs to the current KB, establish independent scope tests, and deliver the required n8n workflow behind FastAPI. Make potential-conflict review mandatory and record the human resolution before publication. Preserve the existing measured RAG behavior throughout.
