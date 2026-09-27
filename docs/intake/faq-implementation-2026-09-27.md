# Faculty FAQ implementation — 27 September 2026

The project owner completed all 18 decision rows and authorized implementation,
Git publication, and deployment to the Oracle instance. The review covers every
one of the 177 anonymized question/approved-answer pairs across all 18 sheets.
Green question cells establish shared department scope except where an explicit
review decision preserves a department-specific rule. Sheet names and unrelated
columns do not determine policy.

## Decisions applied

| Decision | Implementation |
|---|---|
| C1a | MECH may use six company weeks plus two approved research weeks with hands-on engineering work. ECE/IEM require two approved faculty research weeks or at least four weeks at a second company after six company weeks. CHEM/CEE research requires Chair approval. CEE retains exceptional reduced six-week approvals for selected companies. |
| C1b | Dar is an example, not an exclusive eligible company. Department approval rules apply to other companies. |
| C1c | The ECE second-company minimum is four weeks with or without another summer course. |
| C2 | The main internship cannot be inside AUB. Approved faculty research at AUB remains distinct and permitted under the department rules. |
| C3 | Shared company-only Progress Report and separate research-report guidance applies where the company-plus-research arrangement is approved; eligibility follows C1a. |
| C4 | All departments receive conditional concurrent-course guidance: required approvals and work hours, and possible ten-week/time-window requirements, confirmed with the course team/Moodle. No unconditional ten-week requirement is asserted merely because another course is taken. |
| C5 | ECE retains five pages AND 1,500 words minimum, maximum 20 pages. Other departments retain the general 8–15-page template. |
| C6 | Student survey/Student Evaluation Form is required in every department, separately from the Summary Sheet and employer letter. |
| C7a | Retain the CO-OP handbook proposal rules. Do not import a universal internship Proposal requirement into CO-OP. |
| C7b | All CO-OP departments require the signed company letter in addition to both existing employer forms. |
| C7c | Retain handbook presentation rules; no universal CO-OP VOP requirement added. |
| C8 | Quiz attempts remain conditional on Moodle settings, for every department. |
| C9 | Two approved company internships use one report with distinct components. Company-plus-research uses an additional separate research report. Check Moodle for arrangement-specific confirmation. Shared across departments. |
| C10 | Early letters require course-team confirmation in every department; accepted letters state actual start, expected end, and completed work, subject to Moodle. |
| C11a–c | Retain 25% AI-generated text, mandatory disclosure and citation, and 20% similarity for all departments. |
| C12 | Leave the existing June guideline attribution unchanged; do not import the workbook's May attribution. |

## Content and provenance

The source record is `kb/source/faq-review-2026-09-27.json`. It includes original
anonymized questions and approved answers, question-cell scope, source locations,
the completed decision text, and a SHA-256 digest of the returned workbook.
Original source documents are unchanged. Updated normalized files explicitly
identify the later approved review rather than attributing new rules to old
official documents.

Existing facts are not imported as duplicate FAQs. The four distinct additions
are employer-letter template flexibility, the Progress Report deadline origin,
contents-page details, and the distinction between AI detection and similarity.
Shared formatting, report content/confidentiality, approved gaps, delayed-letter
documentation, extension timing, graduating-student deadlines, and Moodle status
guidance are consolidated into existing topics. Course wording is neutral where
shared; the existing EECE/MECH/CHEN/INDE/CIVE mapping remains authoritative.

Oracle had no active admin-authored revisions at the pre-deployment check.
Validation used a separate `faq_review_20260927` database and the production
runtime/model configuration. No student-serving vectors were edited directly.

## Validation

- 26 new golden cases: 25 answerable and one individual-approval refusal.
- Updated-policy evidence retrieval and model-context coverage: **5/25 before,
  25/25 after**. This is a comparison of evidence against the new decisions,
  not a claim that the old bot's answer accuracy was 20%.
- Expanded golden-set adaptive retrieval: **118/121 (97.5%)**, above the 90% gate.
- **42 focused tests passed**, including chunking, department scope, provenance,
  golden-source consistency, and the new FAQ boundaries. New test lint passed.
- Final regression gates passed: synthesis/model-context **47/47**, publication
  scope **9/9**, conflict candidate coverage **7/7**, and threshold acceptance
  **162/162** valid questions (12/20 off-topic questions blocked before generation).
- All 26 targeted responses were reviewed after retrying rate-limited calls:
  25 grounded answers with citations, one correct refusal, 26 AI disclaimers,
  and no false refusals in this sample. Nine initial calls returned provider
  rate-limit errors; paced retries completed them. This is a finite manual
  review, not a statistical guarantee of future generation.
- Additional answer checks verify that an unknown-department 4+4 question keeps
  MECH/CEE/ECE conditions distinct and asks the department, and that a CHEN 500
  employer-letter question does not receive EECE-specific wording.

The existing retrieval misses for grading, internship-versus-CO-OP, and a Career+
topic-switch remain visible in the golden-set report. No prompt, retrieval
algorithm, provider, or model was changed in this content update.

Compact observed answers and evidence checks are retained in
`eval/results/faq_review_20260927.json`. The original broad classification remains
an intake record; its Hold labels describe the state before this completed review.
