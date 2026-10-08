# Knowledge base — source of truth

This folder holds the **file-backed source documents** the bot answers from. The
second accepted source class is a focused CDC knowledge document created through
the guarded admin workflow and stored as an immutable database revision (ADR-0026).
The vector store (pgvector) is *derived* from reviewed normalized files plus active
admin-authored revisions — **never hand-edit the vector store**.

Official file changes still follow normalization and Git review. Dashboard-created
knowledge never edits or masquerades as an official file: it receives a stable
`KB-<entry>` citation identity, version history, author/authority labels, validation,
human conflict review, and atomic activation. Database backups preserve those source
documents and audit history; a full ingestion deterministically reads only the active
revision of each entry.

## Structure

```
kb/
  source/       original documents exactly as received (PDF/docx/etc.).
                Preserved unchanged, for provenance. TRACKED in git.
  normalized/   reviewed text derived from source/ before indexing.
                Canonical input to ingestion; cleaning is auditable. TRACKED.
```

The built vector index lives in PostgreSQL/pgvector — it is regenerated, never
hand-edited or committed.

## How normalization is done

`source/` files are converted to clean Markdown in `normalized/` in two steps:

1. **Mechanical extraction (deterministic code).** A parser using `python-docx`
   / `python-pptx` walks each document in reading order and emits a Markdown
   draft — headings, lists, and tables. This step is reproducible.
2. **Assisted curation (human/AI review).** The draft is then cleaned into the
   final file: fix encoding artifacts, split merged sentences, normalize
   headings/bullets, strip non-content (e.g. committee cover notes), and add YAML
   frontmatter (`title`, `source`, `type`, `program`, `last_updated`,
   `department`). This step involves editorial judgment, so the result is
   **verified against the original** (facts, numbers, contacts, tables) before it
   is trusted. Originals in `source/` remain the ground truth for that check.

The `normalized/` Markdown is the **canonical input to ingestion** — the vector
store is rebuilt from it, so it is version-controlled and reviewable. Known
limitation: `python-docx` does not capture hyperlink URLs (only link text).

### Topic overviews and detailed evidence

Keep both an ordinary topic overview and focused rules/FAQs. A useful overview
connects verified purpose, normal requirements, the main process and where to get
help; it must not turn an exception into the ordinary rule. Summaries can reorganize
approved facts but cannot create eligibility, dates, permission or policy rationales.
Record their supporting source sections in an editorial provenance footer.

A reviewed overview section may include `<!-- content_role: overview -->` directly
below its heading. Ingestion stores this role in metadata and omits the marker from
answer evidence. Merely naming a report section "Organization Overview" does not
make it a topic overview. Keep the summary as a coherent paragraph; confirm it fits
the embedding model's input limit. Its title and first sentence form the compact
embedding representation; the full text remains canonical answer evidence and
full-text search input. Empty heading windows are not indexed.

A service-directory section can use `<!-- content_role: catalogue -->`. The role
applies only to that section's windows, not child sections. Keep the existing
reviewed `program` scope accurate: a single-program leading primary result allows
generation to omit unlinked catalogue evidence that could confuse separate
services. Mixed or unknown program scopes and directory-led questions retain
the directory. Explicit evidence links are preserved. This is conservative
context selection, not automatic classification or a guarantee of service scope.

The local quality candidate adds internship and career-support overviews to the CDC
document and a CO-OP overview to its authoritative handbook. The change has not
published new staff revisions or changed the deployed index. Evaluation evidence
and known limits are in the [main-model evaluation](../eval/results/student_quality_main_model_20261007.md).

### Complete policy context

Keep a fact and its approval, exception or scope condition together. Reconcile
abbreviated bullets against already approved clarifications rather than leaving
the model to resolve contradictory fragments. Preserve provenance and original files.
Wrapped prose and continuation lines inside one Markdown bullet remain together
in the local candidate. Keep the ordinary governing fact self-contained; place
specific exceptions below it with their triggering conditions intact. An explicitly
linked canonical ancestor already retrieved is presented before its child. This
does not expand a scoped rule to other arrangements or guarantee correct reasoning.

Write each alternative as a complete independent path, repeating a shared starting
component when needed. Abbreviated additions separated by "or" can otherwise be
misread as a new combined route. Check that the restatement preserves the approved
components, bounds and conditions. A named arrangement's reporting or procedure
section can link to its governing definition so its name alone is not expected to
establish the required components.

Reviewed sections can declare `<!-- evidence_links: file.md > Section > Child | other.md > Section -->`.
Targets must identify exactly one canonical section path; ingestion rejects missing
or ambiguous targets. Links inherit through child headings and stop at sibling
boundaries. Retrieval restores the linked seed section's own windows and complete
target sections once, respecting
department isolation and the context ceiling. Markers are editorial metadata,
never factual evidence or permission. Use links for actual controlling conditions
or complementary facts, not indiscriminate related-topic expansion.

The local candidate uses these existing links to restore the report introduction
alongside report-specific guidance, retaining the IEM presentation exception. A
restricted internship-format passage links to its ordinary duration/location
requirements; employer IAESTE hosting guidance links to the distinct student
introduction. These links preserve existing context and roles, without adding
new policy. CO-OP tuition and Approved Experience substitution are separate facts;
current Approved Experience credit/billing comes from the approved clarification.
Keep short service lists coherent. When a registration-only window can retrieve
without the service description, a reviewed governing-context link can restore
the section's complete windows and its overview. Paragraph grouping alone does
not guarantee that the factual description will be ranked above registration text.

Keep ordinary topic guidance separate from conditional process changes. A topic
overview should preserve the chronology of approval before training, activities
during training and submissions after completion. An overview's governing link
should restore the normal rule; late starts, changed dates and extensions belong
in separately titled sections with their existing conditions. This avoids pulling
an exceptional procedure into every ordinary topic answer. Reorganize verified
facts without creating new limits, permissions or official policy.

`<!-- process_stage: descriptive stage -->` marks existing source applicability.
Use `entry` for application/admission/initial placement facts and `post_completion`
only for approved facts about outcomes after participation ends. Other descriptive
labels can distinguish participation or course completion. Separate mixed FAQ
chapters by actual process before tagging; a chapter about entry cannot establish
later employment. Tag each factual section explicitly; its windows retain the
label, which is removed from factual text. Stage labels do not inherit to children.

Explicit later employment/retention queries exclude `entry` evidence before search
and companion expansion. Definitive later-outcome claims require retrieved
`post_completion` evidence in the final model context; without it the assistant routes to a human rather than
inventing either a guarantee or a no-guarantee policy. General career-support
questions remain answerable from documented support. Tagging must never introduce
an unsupported policy or authorize publication; unknown/implicit stages remain a
review boundary. New staff content follows the normal source and publication gates.

The local candidate also parses a single `<!-- process_stage: ... -->` line in a
focused Studio revision's answer. The immutable answer retains it for normal
source/human review; factual chunks omit it and every window carries the scope.
Conflicting or malformed stage markers fail chunk construction. An untagged
revision keeps its original behavior and provenance; no stage is guessed from
its question. A marker grants no approval and creates no active revision. There
is no separate stage control in the dashboard. Existing approved revisions may
still need reviewed successors with stage scope: inspect parity before release,
and never infer a policy from missing labels or bypass the evidence guard.

### Normalized outputs (batch 1)

| Normalized file | From |
|-----------------|------|
| `cdc-knowledge-base.md` | `msfea_cdc_kb.md` (frontmatter added; content unchanged) |
| `summer-training-guidelines-2026.md` | `Summer training guidelines - June 2026.docx` |
| `internship-report-templates-and-rubrics.md` | `Internship Templates and Rubrics- Shared with Committee.docx` (committee note stripped) |
| `final-presentation-slide-template.md` | `MSFEA_AUB_Advanced Experience template font.pptx` |

### Normalized outputs (batch 2)

| Normalized file | From |
|-----------------|------|
| `msfea-cdc-coop-handbook.md` | `msfea-cdc-coop-handbook.pdf` (extracted with `pypdf`; ToC/headers/footnotes stripped). Now the **authoritative CO-OP source** — the CO-OP section in `cdc-knowledge-base.md` was reduced to a pointer to avoid duplicate chunks. The Figure-1 application-timeline (an image) was transcribed from the batch-1 KB; the FEAA 500 syllabus appendix is not included. |

### Normalized outputs (email clarifications)

| Normalized file | From |
|-----------------|------|
| `email-clarifications.md` | `email-clarifications.md` (approved reusable answers consolidated from course email information; temporary exceptions and personal/case-specific data excluded). |

## Provenance manifest

Record every document as it lands, so freshness (`last-updated`) is trackable.

| File | What it is | Source / received from | Last updated | Notes |
|------|-----------|------------------------|--------------|-------|
| `msfea_cdc_kb.md` | Curated CDC knowledge base (internship, IAESTE, CO-OP, career readiness, forms); includes FAQs | Provided by student (batch 1); Career+ section verified against the official MSFEA CDC page | 2026-09 | Clean markdown, section-split already. Broader than internship-only. |
| `Summer training guidelines - June 2026.docx` | Official Approved Experience course guidelines | Provided (batch 1) | Jun 2026 | Authoritative for course rules. Contains department contacts + department-specific rules. Tables need clean extraction (python-docx). |
| `Internship Templates and Rubrics- Shared with Committee.docx` | Report/presentation templates + rubrics | Provided (batch 1) | 2026 | Strip committee cover note; keep student-facing templates/rubrics. |
| `MSFEA_AUB_Advanced Experience template font.pptx` | Final-presentation slide template (8 slides) | Provided (batch 1) | 2022 | Template artifact; extract section structure only. |
| `msfea-cdc-coop-handbook.pdf` | Official 10-page MSFEA CO-OP (Cooperative Education) handbook | Provided by student (batch 2) | 2026-07 (received; undated in source) | Authoritative CO-OP reference. **Known extraction gap:** the application-deadline workflow is an image (Figure 1) and the FEAA 500 syllabus (Appendix 1) is not in the text — see the "About this document" note in the normalized file. |
| `email-clarifications.md` | Reusable internship-course clarifications extracted from email information | Approved during project review | 2026-09 | Contains only question/topic, answer, and department. ECE exceptions are explicitly scoped; temporary remote and CO-OP proposals were excluded. |

## Updating knowledge

Current system: [architecture](../docs/architecture.md). Staff-created entries:
[Studio](../docs/studio.md) and [curation contract](../docs/curation.md).


### Faculty FAQ review — 27 September 2026

`source/faq-review-2026-09-27.json` preserves all 177 anonymized questions and
approved answers from all 18 sheets, their question-cell scope, and the project
owner's 18 completed conflict decisions. It omits unrelated workbook columns.
The reviewed changes are consolidated into the existing normalized email,
guideline, report-template, and CO-OP documents, with provenance notes separating
the new decisions from the original official documents. Original source files
remain unchanged. Decision C12 leaves the existing June citation unchanged.

Shared rules use the Approved Experience course name; department course codes
remain in the existing course-code mapping. Department-specific headings retain
their retrieval scope. The approved review supersedes older contradictory
clarifications without creating duplicate FAQ documents in the index.

For a change to an existing official document:

1. Drop the new/updated file into `kb/source/`.
2. Add/update its row in the manifest above.
3. Extract/review the corresponding Markdown in `kb/normalized/`. Ingestion reads this reviewed text; it does not re-extract originals.
4. Re-run ingestion (full rebuild by default) and restart the app after an offline rebuild.
5. Add matching questions to the eval golden set and re-run the eval, to confirm
   the new content is retrievable and nothing regressed.

For a new focused clarification or guideline that is not in an official file, use
the admin dashboard's **Add knowledge** flow. Enter one topic, identify the
responsible CDC authority and scope, run the isolated checks, inspect related
passages, record a named review decision/justification, and only then publish. An
edit creates a successor revision; retiring or replacing it never modifies files
under `kb/source/` or `kb/normalized/`.

## Rules

- No student-identifying data in here (AGENTS.md §7).
- Originals in `source/` stay byte-for-byte as received; all cleaning happens in
  the pipeline and lands in `normalized/`.

- **2026-08-05:** `summer-training-guidelines-2026.md` gained four URLs that were lost in the original normalization (they sat behind anchor text in the .docx) plus three rules supplied by the CDC that are not in the June 2026 file. Both are recorded in that document's "About this document" footer, which is excluded from the index.
