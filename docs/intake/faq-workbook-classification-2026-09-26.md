# FAQ workbook classification — 26 September 2026

Classification only. No KB source, normalized content, vector index, prompt, or evaluation data has been changed. This review replaces the earlier intake report for decision-making; that earlier file is preserved.

## Scope and method

- Reviewed all **18 sheets and 177 question/approved-answer pairs** in `RAG_FAQ_Questions_Answers_Updated.xlsx`. The last sheet uses question column C and answer column D; the other 17 use B and C.
- **156 question cells are green**: 118 pale green (theme accent 3) and 38 medium green (theme accent 6). Both mean all departments, as instructed. The remaining 21 are not green. There are no hidden sheets or conditional-format rules affecting these cells.
- Only the question, approved answer and question-cell fill determine the proposed content/scope. Sheet names are locators, not authority. Other columns and workbook instructions were not used to decide policy or trigger actions.
- Compared all six normalized source documents and ran the existing chunker without embeddings or database writes. It produces 212 passages: 177 all-department, 25 ECE, 3 MECH, 2 CHEM, 3 IEM and 2 CEE. Scope findings below use the actual heading-based metadata, not just the document-level `department: all` header.
- “Covered” means supported in the file-backed KB for the intended scope. It does not prove a successful live answer or retrieval hit. Local Docker/PostgreSQL is unavailable, so active admin-authored database revisions and deployed index freshness were not inspected. Check those for duplicates/conflicts before later publication.
- Green broadens department scope within the answer’s program. It does not turn CO-OP rules into ordinary internship rules, remove summer-graduate eligibility, or override a conflicting department policy without a decision.
- Workbook SHA-256: `2da2b0c75aa15c15da2a808d43f4e07a3369d2f705d3073b49fa008fdee9b07a`. Repository HEAD at review: `4e894d8`.

## Classification summary

| Classification | Rows | Proposed action |
|---|---:|---|
| Skip | 130 | Already covered in the intended scope; do not import another answer. |
| Keep exceptions | 3 | Underlying facts are known; preserve existing department exceptions when wording the answer. |
| Broaden | 11 | Known in ECE or partly general; promote the supported shared detail to all departments. |
| Add | 6 | Add only the missing fact/clarification, once after duplicate rows are collapsed. |
| Hold | 25 | Policy conflict, unsupported obligation or ambiguous change requiring your decision. |
| Correct citation | 2 | Known policy; resolve the May/June source label. |

Counts are workbook rows, not unique facts. Repeated questions remain listed so every sheet is accounted for.

## New information to add once

1. **Employer-letter format:** no fixed completion-letter template is normally required if the employer’s official format contains the required information; current Moodle templates still govern. Two workbook rows.
2. **Progress Report deadline origin:** internship weeks normally run from each student’s approved start date unless Moodle gives a shared deadline. Two workbook rows.
3. **Contents-page detail:** add page numbers and applicable lists of tables, figures and pictures. The Table of Contents requirement itself is already known. One row.
4. **AI versus similarity scores:** explicitly distinguish the two measures. Existing limits are already stored separately, but the explanation is absent. One row.

The first two are substantive administrative clarifications. The last two are small completeness improvements; they should extend existing topics rather than become duplicate FAQ documents.

## Known information to broaden

| Shared detail | Current availability | Rows |
|---|---|---|
| Earlier deadlines for summer graduates | ECE only | PR-10, EFAQ-013 |
| Final Report font/spacing/margins/page numbering | ECE only | FR-04 |
| Explicit engineering problem examples and broader-impact reflection | ECE detail; related general template exists | FR-08, FR-09, FR-10 |
| Confidentiality handling for reports | ECE report guidance; general presentation guidance exists | FR-18 |
| Approved gaps between components | ECE only; retain CHEM same-summer restriction | PLAN-09 |
| Temporary official supervisor email during delayed signed letter | ECE only | EFAQ-006 |
| Confirm final-submission timing after internship extension | ECE only | EFAQ-012 |
| Moodle red-X/activity-completion troubleshooting | ECE only | EFAQ-031 |

These are proposed scope changes under your green-cell instruction. Early letters, report length, 6+2 and concurrent-course rules are excluded from this clean expansion group because they have unresolved conditions or conflicts.

## Decisions and source corrections

### C1. Six-week placements and combinations

Resolve the general 6+2 company/research language, the Dar-only restriction, and the existing ECE inconsistency. The June guideline requires two research weeks or at least four weeks at another company; the later ECE email clarification says ten weeks is not mandatory without another summer course. MECH rejects a two-week research add-on; CEE/IEM have their own exceptions. Which statement governs each department?

**Workbook locations:** `'01_General'!B12`; `'01_General'!B13`; `'01_General'!B14`; `'01_General'!B15`.

**Current evidence:** [summer-training-guidelines-2026.md · Department-Specific Rules](<../../kb/normalized/summer-training-guidelines-2026.md:227>); [email-clarifications.md · Company internship plus research (MECH)](<../../kb/normalized/email-clarifications.md:279>); [email-clarifications.md · Combining two company internships](<../../kb/normalized/email-clarifications.md:261>); [summer-training-guidelines-2026.md · Electrical and Computer Engineering (ECE)](<../../kb/normalized/summer-training-guidelines-2026.md:240>); [summer-training-guidelines-2026.md · Industrial Engineering and Management (IEM)](<../../kb/normalized/summer-training-guidelines-2026.md:255>); [email-clarifications.md · 6+2 arrangement definition](<../../kb/normalized/email-clarifications.md:249>).

### C2. AUB-supervised experience

Does “not accepted” remove existing special-circumstance and approved research exceptions? It also conflicts with the workbook’s own Dar-plus-AUB and AUB-supervisor-documentation cases. Keep the existing exceptions until you decide.

**Workbook locations:** `'01_General'!B17`.

**Current evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Department-Specific Rules](<../../kb/normalized/summer-training-guidelines-2026.md:227>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

### C3. Making Dar 6+2 universal

The reporting detail is known for ECE, but the arrangement itself cannot silently become a MECH option. Decide eligible departments separately from the Progress Report and separate research-report requirements.

**Workbook locations:** `'01_General'!B18`; `'ece specific3'!B13`.

**Current evidence:** [email-clarifications.md · 6+2 arrangement definition](<../../kb/normalized/email-clarifications.md:249>); [email-clarifications.md · Progress reporting for a 6+2 arrangement](<../../kb/normalized/email-clarifications.md:255>); [email-clarifications.md · Reports for multiple approved components (ECE)](<../../kb/normalized/email-clarifications.md:315>); [email-clarifications.md · Company internship plus research (MECH)](<../../kb/normalized/email-clarifications.md:279>); [summer-training-guidelines-2026.md · Industrial Engineering and Management (IEM)](<../../kb/normalized/summer-training-guidelines-2026.md:255>).

### C4. Another summer course

Should the ECE ten-week minimum and before-8:30-AM/after-4:30-PM schedule now apply to every internship department, replacing or supplementing the existing MECH/CEE work-hour rules?

**Workbook locations:** `'14_Concurrent_Course'!B5`; `'14_Concurrent_Course'!B6`; `'14_Concurrent_Course'!B7`.

**Current evidence:** [email-clarifications.md · Taking another summer course (ECE)](<../../kb/normalized/email-clarifications.md:287>); [summer-training-guidelines-2026.md · Mechanical Engineering (MECH)](<../../kb/normalized/summer-training-guidelines-2026.md:231>); [summer-training-guidelines-2026.md · Civil and Environmental Engineering (CEE)](<../../kb/normalized/summer-training-guidelines-2026.md:263>).

### C5. Final Report length

Should all departments adopt the ECE minimum of five pages AND 1,500 words and maximum of 20 pages, or retain the general 8–15-page template with department overrides? The ranges overlap, but they prescribe different limits.

**Workbook locations:** `'ECE specific1'!B7`.

**Current evidence:** [email-clarifications.md · Final Report requirements (ECE)](<../../kb/normalized/email-clarifications.md:295>); [internship-report-templates-and-rubrics.md · 2. Final Training Report Template (8–15 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:86>).

### C6. Student survey versus Summary Sheet

Is every department now required to submit a student survey/self-evaluation, or does the workbook call the universal Summary Sheet a survey? The current source requires a separate Student Evaluation Form only for some departments. Even the “different from the employer letter” answer asserts that both are required.

**Workbook locations:** `'10_Surveys'!B5`; `'10_Surveys'!B6`; `'10_Surveys'!B7`.

**Current evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>).

### C7. CO-OP paperwork and final presentation

Are a generic internship Proposal on Moodle, a signed employer completion letter and a Final VOP new universal CO-OP requirements? The handbook uses a self-found-placement proposal, employer evaluation/feedback forms, a three-page final memo and student reflection; it permits department additions but does not establish these additions universally. Clarify additions versus replacements and the governing course/program.

**Workbook locations:** `'19_Co-op'!B6`; `'19_Co-op'!B9`; `'19_Co-op'!B10`; `'20_Email_Derived_FAQs '!C30`; `'20_Email_Derived_FAQs '!C32`.

**Current evidence:** [msfea-cdc-coop-handbook.md · Application and admission process](<../../kb/normalized/msfea-cdc-coop-handbook.md:144>); [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>); [msfea-cdc-coop-handbook.md · Requirements to pass the co-op course (summary)](<../../kb/normalized/msfea-cdc-coop-handbook.md:259>); [msfea-cdc-coop-handbook.md · Employer responsibilities during the co-op](<../../kb/normalized/msfea-cdc-coop-handbook.md:292>).

### C8. Quiz attempts

Is more than one attempt guaranteed for ECE, or only available when current Moodle settings permit it? The workbook contains both formulations; the existing KB uses the conditional one.

**Workbook locations:** `'ece specific2'!B7`.

**Current evidence:** [email-clarifications.md · Moodle quiz access and attempts](<../../kb/normalized/email-clarifications.md:155>).

### C9. Reports for two components

Does the current ECE one-combined-report instruction still hold for two internships? The workbook replaces it with confirmation of one versus separate reports. This is a weakened instruction, not a clear new opposite rule.

**Workbook locations:** `'ECE specific1'!B21`.

**Current evidence:** [email-clarifications.md · Reports for multiple approved components (ECE)](<../../kb/normalized/email-clarifications.md:315>).

### C10. Early employer letter

Does the early-letter allowance apply to summer graduates in every department, and must the course team approve its acceptance? Green resolves department breadth but the approved answer’s malformed opening does not establish broader student eligibility or remove approval.

**Workbook locations:** `'20_Email_Derived_FAQs '!C8`.

**Current evidence:** [email-clarifications.md · Early or temporarily delayed employer letter (ECE)](<../../kb/normalized/email-clarifications.md:127>).

### C11. AI policy freshness

Do 25% AI, mandatory disclosure/citation and 20% similarity remain approved current rules, or should numerical policy answers defer to current Moodle? The workbook supplies no new AI threshold and describes 20% historically. This is an authority/freshness question, not evidence of a different numeric cap.

**Workbook locations:** `'ece specific 5'!B6`; `'ece specific 5'!B7`; `'ece specific 5'!B13`.

**Current evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

### C12. Guideline month

Two answers name a May 2026 guideline; this repo contains the June 2026 guideline with the same Week-4 deadline. Correct the citation to the available June source, or supply the intended May revision if it is a different governing document.

**Workbook locations:** `'ece specific3'!B6`; `'15_Deadlines'!B8`.

**Current evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>).

## Recommended KB structure after decisions

Use the current file-backed intake path for this faculty workbook. Keep a traceable source record and curated, sectioned Markdown with the existing metadata and atomic `Question/topic` + `Answer` pattern. Consolidate each shared policy once under all-department scope; retain genuinely different department rules in correctly scoped headings. Do not generalize an entire ECE section to move one answer.

For shared answers, use “your Approved Experience course” and the existing course-code map: ECE/CCE → EECE 500; MECH → MECH 500; CHEM → CHEN 500; IEM → INDE 500; CEE → CIVE 400. A CHEM student’s employer-letter answer can say “required for CHEN 500.” The employer-letter obligation itself is already universal. If department context is absent, use the neutral course name rather than guessing.

Keep CO-OP material in the CO-OP source/program. Record which approved workbook rows support each new or widened assertion. Preserve original source provenance; do not attribute a newly supplied workbook rule to the older June guideline. If a received original contains identifying data, retain it outside the student KB and ingest only a reviewed anonymized derivative with a provenance reference.

Before ingestion, check active admin-authored revisions, resolve the issues above, add representative cross-department evaluation cases and record the baseline. Then rebuild through the existing pipeline, verify chunk scope and course-code rendering, measure retrieval and grounded-answer/refusal behavior separately, and review regressions. This classification makes no performance-improvement claim.

## All 177 rows

Each entry includes the exact inspected question and approved answer, source cell addresses, proposed scope, present KB coverage, decision and evidence. Workbook text is quoted as source data, not instructions to the assistant. IDs are locators only; repeated IDs are disambiguated by sheet and cell.

### Sheet: 01_General

#### 001. GEN-01 — Skip

**Question (B5):** What is EECE 500?

**Approved answer (C5), as supplied:** EECE 500 – Approved Experience is the required internship course for ECE/CCE students. It allows students to apply engineering knowledge in a professional setting and gain practical and professional experience.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; course code varies.

**Classification:** Skip. All five course codes and the purpose of Approved Experience already exist. Use the student’s own course code; do not create five copies of the same shared policy.

**Evidence:** [email-clarifications.md · Approved Experience course codes](<../../kb/normalized/email-clarifications.md:11>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>).

#### 002. GEN-01 — Skip

**Question (B6):** What is MECH 500?

**Approved answer (C6), as supplied:** MECH 500 – Approved Experience is the required internship course for MECH students. It allows students to apply engineering knowledge in a professional setting and gain practical and professional experience.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; course code varies.

**Classification:** Skip. All five course codes and the purpose of Approved Experience already exist. Use the student’s own course code; do not create five copies of the same shared policy.

**Evidence:** [email-clarifications.md · Approved Experience course codes](<../../kb/normalized/email-clarifications.md:11>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>).

#### 003. GEN-01 — Skip

**Question (B7):** What is CHEN 500?

**Approved answer (C7), as supplied:** CHEN 500 – Approved Experience is the required internship course for CHEN students. It allows students to apply engineering knowledge in a professional setting and gain practical and professional experience.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; course code varies.

**Classification:** Skip. All five course codes and the purpose of Approved Experience already exist. Use the student’s own course code; do not create five copies of the same shared policy.

**Evidence:** [email-clarifications.md · Approved Experience course codes](<../../kb/normalized/email-clarifications.md:11>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>).

#### 004. GEN-01 — Skip

**Question (B8):** What is INDE 500?

**Approved answer (C8), as supplied:** INDE 500 – Approved Experience is the required internship course for INDE students. It allows students to apply engineering knowledge in a professional setting and gain practical and professional experience.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; course code varies.

**Classification:** Skip. All five course codes and the purpose of Approved Experience already exist. Use the student’s own course code; do not create five copies of the same shared policy.

**Evidence:** [email-clarifications.md · Approved Experience course codes](<../../kb/normalized/email-clarifications.md:11>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>).

#### 005. GEN-01 — Skip

**Question (B9):** What is CIVE 400?

**Approved answer (C9), as supplied:** CIVE 400 – Approved Experience is the required internship course for CIVE students. It allows students to apply engineering knowledge in a professional setting and gain practical and professional experience.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; course code varies.

**Classification:** Skip. All five course codes and the purpose of Approved Experience already exist. Use the student’s own course code; do not create five copies of the same shared policy.

**Evidence:** [email-clarifications.md · Approved Experience course codes](<../../kb/normalized/email-clarifications.md:11>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>).

#### 006. GEN-02 — Skip

**Question (B10):** Is the internship course required for graduation?

**Approved answer (C10), as supplied:** Yes. Approved Experience is a graduation requirement. Students must complete the approved internship and all required course deliverables to pass the internship course

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Graduation requirement and completion of required deliverables are already general.

**Evidence:** [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>).

#### 007. GEN-03 — Keep exceptions

**Question (B11):** How long must my internship be?

**Approved answer (C11), as supplied:** You must complete a minimum of 8 full weeks of approved training, typically equivalent to approximately 320 work hours.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All, with department exceptions.

**Classification:** Keep exceptions. Eight weeks/320 hours is already the general rule. Retain the documented petition-based six-week exceptions and the ECE concurrent-course condition; do not import the answer as an exception-free absolute.

**Evidence:** [summer-training-guidelines-2026.md · Internship Requirements](<../../kb/normalized/summer-training-guidelines-2026.md:31>); [summer-training-guidelines-2026.md · Industrial Engineering and Management (IEM)](<../../kb/normalized/summer-training-guidelines-2026.md:255>); [summer-training-guidelines-2026.md · Civil and Environmental Engineering (CEE)](<../../kb/normalized/summer-training-guidelines-2026.md:263>).

#### 008. GEN-04 — Hold

**Question (B12):** Is a 6-week internship enough?

**Approved answer (C12), as supplied:** No. A 6-week internship alone is not enough. If, for instance, a company is only allowing a training period of 6 weeks, the student must complete an additional 2 weeks in another company or a research internship with a faculty member within or outside their department. Review further departmental regulations below. For EECE, the second company should be 4 weeks

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE/IEM routes; MECH restriction; CEE exception.

**Classification:** Hold. The proposed general 6+2 company/research route is not established for every department. MECH expressly rejects the two-week research add-on; ECE/IEM specify a four-week second-company component; CEE has a reduced-duration exception. Reconcile the existing ECE source disagreement too. See C1.

**Evidence:** [summer-training-guidelines-2026.md · Department-Specific Rules](<../../kb/normalized/summer-training-guidelines-2026.md:227>); [email-clarifications.md · Company internship plus research (MECH)](<../../kb/normalized/email-clarifications.md:279>); [email-clarifications.md · Combining two company internships](<../../kb/normalized/email-clarifications.md:261>).

#### 009. GEN-05 — Hold

**Question (B13):** What should I do if my company offers only a 6-week internship?

**Approved answer (C13), as supplied:** If, for instance, a company is only allowing a training period of 6 weeks, the student must complete an additional 2 weeks in another company or a research internship with a faculty member within or outside their department. Review further departmental regulations below. For EECE, the second company should be 4 weeks

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE/IEM routes; MECH restriction; CEE exception.

**Classification:** Hold. The proposed general 6+2 company/research route is not established for every department. MECH expressly rejects the two-week research add-on; ECE/IEM specify a four-week second-company component; CEE has a reduced-duration exception. Reconcile the existing ECE source disagreement too. See C1.

**Evidence:** [summer-training-guidelines-2026.md · Department-Specific Rules](<../../kb/normalized/summer-training-guidelines-2026.md:227>); [email-clarifications.md · Company internship plus research (MECH)](<../../kb/normalized/email-clarifications.md:279>); [email-clarifications.md · Combining two company internships](<../../kb/normalized/email-clarifications.md:261>).

#### 010. GEN-06 — Hold

**Question (B14):** Can I do 6 weeks at one company and 2 weeks at another company?

**Approved answer (C14), as supplied:** No, not as the standard EECE arrangement. If the first company internship is 6 weeks, the second company internship should be at least 4 weeks. The 2-week additional component applies to the approved Dar Al-Handasah plus AUB research arrangement.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE/IEM research route; other rules differ.

**Classification:** Hold. The answer limits the two-week research route to Dar Al-Handasah plus AUB. Current sources describe an approved six-week company placement plus MSFEA faculty research without the Dar-only restriction. Green scope also needs department exceptions. See C1.

**Evidence:** [summer-training-guidelines-2026.md · Electrical and Computer Engineering (ECE)](<../../kb/normalized/summer-training-guidelines-2026.md:240>); [summer-training-guidelines-2026.md · Industrial Engineering and Management (IEM)](<../../kb/normalized/summer-training-guidelines-2026.md:255>); [email-clarifications.md · 6+2 arrangement definition](<../../kb/normalized/email-clarifications.md:249>).

#### 011. GEN-07 — Hold

**Question (B15):** Can I combine two internships?

**Approved answer (C15), as supplied:** Yes, subject to prior approval. For the standard EECE arrangement following a 6-week internship, the second approved company internship should be at least 4 weeks. Each component must be properly approved and documented. For MECH students, it is not possible to do a 4+4 arrangement. For CIVE students, a 4+4 arrangement is possible if at least one period is in civil or construction engineering.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Department-specific.

**Classification:** Hold. MECH and CEE split rules already match. The four-week second-company rule matches the June ECE guideline, but the later ECE clarification says ten weeks is not mandatory without another summer course. This is an existing source disagreement, not wholly new information. See C1.

**Evidence:** [summer-training-guidelines-2026.md · Department-Specific Rules](<../../kb/normalized/summer-training-guidelines-2026.md:227>); [email-clarifications.md · Combining two company internships](<../../kb/normalized/email-clarifications.md:261>).

#### 012. GEN-08 — Keep exceptions

**Question (B16):** Can I split the internship into two 4-week internships?

**Approved answer (C16), as supplied:** Do not assume that a 4+4 split is automatically accepted. Any arrangement outside the standard  structure must be reviewed and approved before you start.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Department-specific.

**Classification:** Keep exceptions. Prior approval is already documented. Preserve the useful specifics: MECH prohibits 4+4, CEE permits it with its civil/construction condition, CHEM requires the same summer, and ECE needs case-specific approval.

**Evidence:** [summer-training-guidelines-2026.md · Mechanical Engineering (MECH)](<../../kb/normalized/summer-training-guidelines-2026.md:231>); [summer-training-guidelines-2026.md · Civil and Environmental Engineering (CEE)](<../../kb/normalized/summer-training-guidelines-2026.md:263>); [summer-training-guidelines-2026.md · Chemical Engineering (CHEM)](<../../kb/normalized/summer-training-guidelines-2026.md:246>); [email-clarifications.md · 4+4 company-internship split](<../../kb/normalized/email-clarifications.md:267>).

#### 013. GEN-10 — Hold

**Question (B17):** Can I do my approved experience at AUB with a professor?

**Approved answer (C17), as supplied:** not accepted

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** General prohibition with approved exceptions.

**Classification:** Hold. “not accepted” removes documented special circumstances and approved faculty-research arrangements. It also needs reconciliation with the workbook’s own Dar/AUB-research and faculty-letter answers. See C2.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Department-Specific Rules](<../../kb/normalized/summer-training-guidelines-2026.md:227>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 014. GEN-11 — Hold

**Question (B18):** What are the requirements for the Dar Al-Handasah 6+2 arrangement?

**Approved answer (C18), as supplied:** If you complete 6 weeks at Dar Al-Handasah, you must complete at least 2 additional weeks of approved research at AUB with an MSFEA faculty member. students completing a 6+2 arrangement must also submit the required separate research report for the research component.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE; IEM has a research route; MECH prohibits add-on.

**Classification:** Hold. The company-only Progress Report and separate research report are documented for ECE. Applying this arrangement to every department conflicts with the MECH prohibition. Keep the arrangement’s eligibility separate from its reporting instructions. See C3.

**Evidence:** [email-clarifications.md · 6+2 arrangement definition](<../../kb/normalized/email-clarifications.md:249>); [email-clarifications.md · Progress reporting for a 6+2 arrangement](<../../kb/normalized/email-clarifications.md:255>); [email-clarifications.md · Reports for multiple approved components (ECE)](<../../kb/normalized/email-clarifications.md:315>); [email-clarifications.md · Company internship plus research (MECH)](<../../kb/normalized/email-clarifications.md:279>); [summer-training-guidelines-2026.md · Industrial Engineering and Management (IEM)](<../../kb/normalized/summer-training-guidelines-2026.md:255>).

#### 015. GEN-12 — Skip

**Question (B19):** Can I do my internship outside Lebanon?

**Approved answer (C19), as supplied:** Yes. Approved training may take place in Lebanon or abroad, provided the organization and internship experience are approved and meet the course requirements.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Approved training in Lebanon or abroad is already supported.

**Evidence:** [summer-training-guidelines-2026.md · Internship Requirements](<../../kb/normalized/summer-training-guidelines-2026.md:31>).

### Sheet: 02_Approval_Petitions

#### 016. APR-01 — Skip

**Question (B5):** Does my internship need to be approved before I start?

**Approved answer (C5), as supplied:** Yes. Your internship must be approved according toMSFEA procedures. Do not assume an internship will count simply because you received an offer.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Self-secured placements, CDC procedure and prior departmental approval are already general. Preserve the existing petition details.

**Evidence:** [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>); [cdc-knowledge-base.md · Applying to an internship found independently](<../../kb/normalized/cdc-knowledge-base.md:32>).

#### 017. APR-02 — Skip

**Question (B6):** I found the internship myself. What should I do?

**Approved answer (C6), as supplied:** If you secured the internship independently rather than through the CDC, complete the CDC self-secured internship procedure and obtain the required departmental approval before starting.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Self-secured placements, CDC procedure and prior departmental approval are already general. Preserve the existing petition details.

**Evidence:** [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>); [cdc-knowledge-base.md · Applying to an internship found independently](<../../kb/normalized/cdc-knowledge-base.md:32>).

#### 018. APR-03 — Skip

**Question (B7):** Do I need a petition for a self-secured internship?

**Approved answer (C7), as supplied:** Follow the CDC and departmental approval procedure for self-secured internships. Where a petition is required, submit it with all supporting documents before beginning the internship.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Self-secured placements, CDC procedure and prior departmental approval are already general. Preserve the existing petition details.

**Evidence:** [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>); [cdc-knowledge-base.md · Applying to an internship found independently](<../../kb/normalized/cdc-knowledge-base.md:32>).

#### 019. APR-04 — Skip

**Question (B8):** What should the company letter for an internship-approval petition contain?

**Approved answer (C8), as supplied:** The official company letter should normally include company letterhead, a signature, internship duration, and a description of the expected training and work. Additional information may be required depending on the company status with the CDC.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Petition and official signed company letter with letterhead, duration and work description are already present.

**Evidence:** [summer-training-guidelines-2026.md · If the Company Is Already Listed with the CDC](<../../kb/normalized/summer-training-guidelines-2026.md:78>).

#### 020. APR-05 — Skip

**Question (B9):** My company is not listed with the CDC. Can I still intern there?

**Approved answer (C9), as supplied:** Potentially, but prior approval is required by submitting a petition. The supporting company letter should describe the company and industry, the type of training provided, and the internship duration.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Prior petition and company/industry, training and duration information already exist.

**Evidence:** [summer-training-guidelines-2026.md · If the Company Is NOT Listed with the CDC](<../../kb/normalized/summer-training-guidelines-2026.md:87>).

#### 021. APR-06 — Skip

**Question (B10):** Are startup internships accepted?

**Approved answer (C10), as supplied:** Startup internships may be accepted through prior formal approval. The request should clearly describe the scope of work, your responsibilities, and the technical or professional learning outcomes.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Startup petition, responsibilities, learning outcomes and approvals are already general.

**Evidence:** [summer-training-guidelines-2026.md · Internships at Startups](<../../kb/normalized/summer-training-guidelines-2026.md:95>).

#### 022. APR-07 — Skip

**Question (B11):** Who approves an internship exception?

**Approved answer (C11), as supplied:** Exceptions must follow the formal MSFEA/department approval process. The guideline requires departmental and course-instructor approval together with the required supporting documents.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Formal exception approval, supporting documents, department/instructor approval and CDC copy are already documented.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

#### 023. APR-08 — Skip

**Question (B12):** Can I start first and ask for approval later?

**Approved answer (C12), as supplied:** You should not rely on retroactive approval. Obtain the required approval before beginning an internship or alternative arrangement.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Self-secured placements, CDC procedure and prior departmental approval are already general. Preserve the existing petition details.

**Evidence:** [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>); [cdc-knowledge-base.md · Applying to an internship found independently](<../../kb/normalized/cdc-knowledge-base.md:32>).

#### 024. APR-09 — Skip

**Question (B13):** What happens if my petition is incomplete?

**Approved answer (C13), as supplied:** Submit all required supporting documentation. The MSFEA guideline states that incomplete petitions are rejected.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Formal exception approval, supporting documents, department/instructor approval and CDC copy are already documented.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

#### 025. APR-10 — Skip

**Question (B14):** My friend received approval for the same arrangement last year. Does that mean mine is approved?

**Approved answer (C14), as supplied:** No. Previous individual or exceptional approvals do not automatically apply to another student or another semester. Follow the current policy and obtain approval when required.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; individual approvals remain individual.

**Classification:** Skip. No new policy: prior approval applies to the student’s own placement. Retain current department exceptions; do not turn someone else’s past approval into a standing permission.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>).

#### 026. APR-11 — Skip

**Question (B15):** What documents are needed if the company is already listed with the CDC?

**Approved answer (C15), as supplied:** Submit the required approval request or petition and an official signed company letter on letterhead stating the internship duration and describing the expected training and work. Follow the current CDC and Moodle procedure before starting.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Petition and official signed company letter with letterhead, duration and work description are already present.

**Evidence:** [summer-training-guidelines-2026.md · If the Company Is Already Listed with the CDC](<../../kb/normalized/summer-training-guidelines-2026.md:78>).

#### 027. APR-12 — Skip

**Question (B16):** What must an internship petition include?

**Approved answer (C16), as supplied:** Explain the requested approval or exception clearly and attach all required supporting documents. Obtain the required departmental and course approvals and follow the CDC submission or copying instructions. Incomplete petitions may be rejected.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Formal exception approval, supporting documents, department/instructor approval and CDC copy are already documented.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

#### 028. APR-13 — Skip

**Question (B17):** How do I request an exception to an internship rule?

**Approved answer (C17), as supplied:** Submit a formal petition before relying on the exception. Include a clear justification and complete supporting documents, then obtain the required departmental and course approvals and follow the CDC procedure.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Formal exception approval, supporting documents, department/instructor approval and CDC copy are already documented.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

### Sheet: 03_Remote

#### 029. REM-01 — Keep exceptions

**Question (B5):** Are fully online or remote internships accepted?

**Approved answer (C5), as supplied:** fully remote internship is not accepted. Obtain formal approval before starting if the internship format requires an exception.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** General rule plus IEM exception.

**Classification:** Keep exceptions. Remote work is generally disallowed. Preserve the explicit IEM exception for approved U.S.-based remote placements when legally eligible to work in the U.S.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Industrial Engineering and Management (IEM)](<../../kb/normalized/summer-training-guidelines-2026.md:255>).

#### 030. REM-02 — Skip

**Question (B6):** Remote internships were accepted in a previous summer. Does that mean mine is accepted?

**Approved answer (C6), as supplied:** No. Temporary or exceptional approvals from previous semesters do not establish a permanent  rule. Your internship must follow the policy applicable to the current term.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; individual approvals remain individual.

**Classification:** Skip. No new policy: prior approval applies to the student’s own placement. Retain current department exceptions; do not turn someone else’s past approval into a standing permission.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>).

#### 031. REM-03 — Skip

**Question (B7):** Should I accept a remote internship first and petition later?

**Approved answer (C7), as supplied:** No. If the internship format requires an exception, obtain approval before relying on it

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; format exceptions require approval.

**Classification:** Skip. Prior approval rather than assumed retroactive acceptance is already covered.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>).

### Sheet: ece specific2

#### 032. RES-01 — Skip

**Question (B5):** Do I have to watch the EECE 500 lectures and videos?

**Approved answer (C5), as supplied:** Yes. The professional-skills and internship-learning resources on Moodle are part of the course requirements and should be completed as instructed.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All baseline; ECE also explicit.

**Classification:** Skip. Required Moodle resources, quiz and 75% passing score already exist. Non-green does not justify narrowing a rule the existing general source already supports. The learning purpose is covered by the report guidance.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>); [internship-report-templates-and-rubrics.md · 1. Progress Report Template (3–5 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:19>).

#### 033. RES-02 — Skip

**Question (B6):** Do I have to take the Moodle quiz?

**Approved answer (C6), as supplied:** Yes. The quiz is a required EECE 500 course assessment.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All baseline; ECE also explicit.

**Classification:** Skip. Required Moodle resources, quiz and 75% passing score already exist. Non-green does not justify narrowing a rule the existing general source already supports. The learning purpose is covered by the report guidance.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>); [internship-report-templates-and-rubrics.md · 1. Progress Report Template (3–5 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:19>).

#### 034. RES-03 — Hold

**Question (B7):** Can I attempt the quiz more than once?

**Approved answer (C7), as supplied:** Follow the settings and instructions on the current EECE 500 Moodle page. You are allowed multiple attempts so students can reach the required passing score.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All baseline; workbook answer is ECE.

**Classification:** Hold. Existing source says multiple attempts may be available and current Moodle settings decide. Workbook both defers to settings and states multiple attempts are allowed. Clarify whether this establishes a guaranteed ECE entitlement. See C8.

**Evidence:** [email-clarifications.md · Moodle quiz access and attempts](<../../kb/normalized/email-clarifications.md:155>).

#### 035. RES-04 — Skip

**Question (B8):** What is the passing grade for the EECE 500 quiz?

**Approved answer (C8), as supplied:** 75

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All baseline; ECE also explicit.

**Classification:** Skip. Required Moodle resources, quiz and 75% passing score already exist. Non-green does not justify narrowing a rule the existing general source already supports. The learning purpose is covered by the report guidance.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>); [internship-report-templates-and-rubrics.md · 1. Progress Report Template (3–5 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:19>).

#### 036. RES-05 — Skip

**Question (B9):** Why do I need to complete the lectures, videos, and quiz?

**Approved answer (C9), as supplied:** They prepare you to reflect on professional skills, engineering problem solving, learning strategies, and the broader global, economic, environmental, and societal impact of engineering solutions in your reports and presentation.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All baseline; ECE also explicit.

**Classification:** Skip. Required Moodle resources, quiz and 75% passing score already exist. Non-green does not justify narrowing a rule the existing general source already supports. The learning purpose is covered by the report guidance.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>); [internship-report-templates-and-rubrics.md · 1. Progress Report Template (3–5 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:19>).

#### 037. RES-06 — Skip

**Question (B10):** Why can’t I access the Moodle quiz?

**Approved answer (C10), as supplied:** The quiz may be restricted until the required lectures or videos are completed. Finish the assigned resources and check again. If access remains blocked, send the course coordinator a screenshot before the deadline.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All baseline; ECE included.

**Classification:** Skip. Access prerequisites, remaining attempts and approval to reopen the quiz are already covered.

**Evidence:** [email-clarifications.md · Moodle quiz access and attempts](<../../kb/normalized/email-clarifications.md:155>); [email-clarifications.md · Moodle submissions and corrections](<../../kb/normalized/email-clarifications.md:39>).

#### 038. RES-07 — Skip

**Question (B11):** What if I do not reach the quiz passing score?

**Approved answer (C11), as supplied:** Review the assigned resources and attempt the quiz again if the current Moodle settings allow another attempt. If the quiz is closed or no attempt remains, contact the course coordinator.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All baseline; ECE included.

**Classification:** Skip. Access prerequisites, remaining attempts and approval to reopen the quiz are already covered.

**Evidence:** [email-clarifications.md · Moodle quiz access and attempts](<../../kb/normalized/email-clarifications.md:155>); [email-clarifications.md · Moodle submissions and corrections](<../../kb/normalized/email-clarifications.md:39>).

#### 039. RES-08 — Skip

**Question (B12):** I missed the quiz deadline. Can it be reopened?

**Approved answer (C12), as supplied:** Reopening is not automatic. Contact the course coordinator promptly, explain the reason, and provide supporting information when relevant. Any reopening requires approval.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All baseline; ECE included.

**Classification:** Skip. Access prerequisites, remaining attempts and approval to reopen the quiz are already covered.

**Evidence:** [email-clarifications.md · Moodle quiz access and attempts](<../../kb/normalized/email-clarifications.md:155>); [email-clarifications.md · Moodle submissions and corrections](<../../kb/normalized/email-clarifications.md:39>).

### Sheet: ece specific3

#### 040. PR-01 — Skip

**Question (B5):** Do I have to submit a Progress Report?

**Approved answer (C5), as supplied:** Yes. The Progress Report is a required EECE 500 deliverable.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Separate Progress and Final Reports are already general requirements; replace EECE wording with the student’s course name only when presenting the shared rule.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [internship-report-templates-and-rubrics.md · 1. Progress Report Template (3–5 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:19>); [internship-report-templates-and-rubrics.md · 2. Final Training Report Template (8–15 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:86>).

#### 041. PR-02 — Correct citation

**Question (B6):** When is the Progress Report due?

**Approved answer (C6), as supplied:** Follow the deadline announced on the current EECE 500 Moodle page. The May 2026 MSFEA guideline places it by the end of Week 4 of the internship.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Correct citation. End-of-Week-4 timing is already covered. The workbook cites May 2026; the source available in this repo is June 2026. No deadline policy change is needed on the evidence available. See C12.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>).

#### 042. PR-03 — Add

**Question (B7):** Is the Progress Report deadline counted from the summer semester start or from my internship start date?

**Approved answer (C7), as supplied:** Internship-week deadlines are normally counted from your own approved internship start date unless Moodle announces a common course deadline.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Related timeline is general; explicit interpretation absent.

**Classification:** Add. Add one general clarification: internship-week deadlines normally run from the student’s own approved start date unless Moodle specifies a common deadline. Existing Week-4 wording implies this but does not explicitly resolve the semester-start question.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 043. PR-04 — Skip

**Question (B8):** What should I include in my Progress Report?

**Approved answer (C8), as supplied:** Include your name and ID, company information, internship dates, company profile, your role and responsibilities, progress and contributions so far, and the remaining tasks or objectives for the rest of the internship.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Identity, organization, dates, role, progress and remaining goals are already general report content.

**Evidence:** [summer-training-guidelines-2026.md · Progress Report Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:162>); [internship-report-templates-and-rubrics.md · 1. Progress Report Template (3–5 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:19>).

#### 044. PR-05 — Skip

**Question (B9):** How long should the Progress Report be?

**Approved answer (C9), as supplied:** Follow the EECE 500 template posted on Moodle. The MSFEA guideline describes the Progress Report as approximately 5 pages.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Approximately 1,000 words / 3–5 pages, Moodle template and possible revision already exist. Preserve the full current range rather than turning “approximately 5” into an exact length.

**Evidence:** [email-clarifications.md · Progress Report length and component](<../../kb/normalized/email-clarifications.md:171>); [internship-report-templates-and-rubrics.md · Progress Report Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:74>); [summer-training-guidelines-2026.md · Progress Report Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:162>).

#### 045. PR-06 — Skip

**Question (B10):** Can I submit the Final Report instead of the Progress Report?

**Approved answer (C10), as supplied:** No. The Progress Report and Final Training Report are separate required deliverables and serve different purposes.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Separate Progress and Final Reports are already general requirements; replace EECE wording with the student’s course name only when presenting the shared rule.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [internship-report-templates-and-rubrics.md · 1. Progress Report Template (3–5 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:19>); [internship-report-templates-and-rubrics.md · 2. Final Training Report Template (8–15 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:86>).

#### 046. PR-07 — Skip

**Question (B11):** My Progress Report is much longer than required. Will it be accepted?

**Approved answer (C11), as supplied:** A report that does not follow the required length or template may be returned for revision. Keep the report concise, cover the required sections, and follow the current Moodle template and word/page guidance.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Approximately 1,000 words / 3–5 pages, Moodle template and possible revision already exist. Preserve the full current range rather than turning “approximately 5” into an exact length.

**Evidence:** [email-clarifications.md · Progress Report length and component](<../../kb/normalized/email-clarifications.md:171>); [internship-report-templates-and-rubrics.md · Progress Report Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:74>); [summer-training-guidelines-2026.md · Progress Report Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:162>).

#### 047. PR-08 — Skip

**Question (B12):** If I have two approved internships, which one should the Progress Report cover?

**Approved answer (C12), as supplied:** The Progress Report should normally describe the approved component you are actively completing at the required reporting point. Because combined schedules vary, confirm the expected coverage with the course coordinator if it is not clear from Moodle.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Report on the approved component being completed at the reporting point, subject to coordinator direction, is already general.

**Evidence:** [email-clarifications.md · Progress Report length and component](<../../kb/normalized/email-clarifications.md:171>).

#### 048. PR-09 — Hold

**Question (B13):** For the Dar Al-Handasah 6+2 arrangement, what should the Progress Report cover?

**Approved answer (C13), as supplied:** Cover only the six-week Dar Al-Handasah company internship in the Progress Report. Submit it at the reporting point stated on the current Moodle page; the two-week AUB research component is documented separately as required.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE; IEM has a research route; MECH prohibits add-on.

**Classification:** Hold. The company-only Progress Report and separate research report are documented for ECE. Applying this arrangement to every department conflicts with the MECH prohibition. Keep the arrangement’s eligibility separate from its reporting instructions. See C3.

**Evidence:** [email-clarifications.md · 6+2 arrangement definition](<../../kb/normalized/email-clarifications.md:249>); [email-clarifications.md · Progress reporting for a 6+2 arrangement](<../../kb/normalized/email-clarifications.md:255>); [email-clarifications.md · Reports for multiple approved components (ECE)](<../../kb/normalized/email-clarifications.md:315>); [email-clarifications.md · Company internship plus research (MECH)](<../../kb/normalized/email-clarifications.md:279>); [summer-training-guidelines-2026.md · Industrial Engineering and Management (IEM)](<../../kb/normalized/summer-training-guidelines-2026.md:255>).

#### 049. PR-10 — Broaden

**Question (B14):** I am a summer graduate. Do I need to submit the Progress Report earlier?

**Approved answer (C14), as supplied:** Summer graduates may receive an earlier course deadline because grades must be processed sooner. Follow the specific Moodle announcement or coordinator email for graduating students.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE only.

**Classification:** Broaden. Move the shared summer-graduate deadline clarification to all-department scope. Keep “may receive earlier deadlines” and current Moodle/coordinator control; no fixed date is introduced.

**Evidence:** [email-clarifications.md · Summer-graduate deadlines (ECE)](<../../kb/normalized/email-clarifications.md:223>).

#### 050. PR-11 — Skip

**Question (B15):** My Progress Report was evaluated as unsatisfactory. Can I resubmit it?

**Approved answer (C15), as supplied:** A revision may be allowed or required, but resubmission is not automatic. Follow the feedback and the deadline provided by the course team, and resubmit only when the Moodle submission is reopened or you are instructed to do so.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Authorized revision and the fact that an initial Fail does not automatically cause course failure already exist. Reopening remains controlled by the course team.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>); [email-clarifications.md · Moodle submissions and corrections](<../../kb/normalized/email-clarifications.md:39>); [internship-report-templates-and-rubrics.md · Progress Report Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:74>).

#### 051. PR-12 — Skip

**Question (B16):** Will an initial unsatisfactory Progress Report automatically make me fail the course?

**Approved answer (C16), as supplied:** Not necessarily. If an authorized resubmission is allowed and the revised report is satisfactory, the initial result alone does not automatically prevent a Pass. You must still complete every other course requirement satisfactorily.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Authorized revision and the fact that an initial Fail does not automatically cause course failure already exist. Reopening remains controlled by the course team.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>); [email-clarifications.md · Moodle submissions and corrections](<../../kb/normalized/email-clarifications.md:39>); [internship-report-templates-and-rubrics.md · Progress Report Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:74>).

### Sheet: ECE specific1

#### 052. FR-01 — Skip

**Question (B5):** Is the Final Training Report required?

**Approved answer (C5), as supplied:** Yes. The Final Training Report is a required EECE 500 deliverable and must cover your approved experience activities.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Separate Progress and Final Reports are already general requirements; replace EECE wording with the student’s course name only when presenting the shared rule.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [internship-report-templates-and-rubrics.md · 1. Progress Report Template (3–5 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:19>); [internship-report-templates-and-rubrics.md · 2. Final Training Report Template (8–15 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:86>).

#### 053. FR-02 — Skip

**Question (B6):** When should I submit my Final Training Report?

**Approved answer (C6), as supplied:** Normally submit it within one week after completing the approved internship, unless a different official deadline is announced on the current EECE 500 Moodle page.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. The general Final Report deadline is already within one week after completion, with coordinator handling of exceptional/current-term schedules.

**Evidence:** [summer-training-guidelines-2026.md · Final Training Report](<../../kb/normalized/summer-training-guidelines-2026.md:195>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 054. FR-03 — Hold

**Question (B7):** How long should the Final Training Report be?

**Approved answer (C7), as supplied:** It must contain at least 5 pages and 1,500 words, excluding the cover page, references, and appendix, and it should not exceed 20 pages.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE limit; different general template.

**Classification:** Hold. Five pages AND 1,500 words minimum, 20 pages maximum is ECE-only. The general template says 8–15 pages. Green indicates a proposed scope expansion, but authority over the existing general length guidance must be resolved. See C5.

**Evidence:** [email-clarifications.md · Final Report requirements (ECE)](<../../kb/normalized/email-clarifications.md:295>); [internship-report-templates-and-rubrics.md · 2. Final Training Report Template (8–15 pages)](<../../kb/normalized/internship-report-templates-and-rubrics.md:86>).

#### 055. FR-04 — Broaden

**Question (B8):** What font and spacing should I use in the Final Report?

**Approved answer (C8), as supplied:** Use size 12 font and double spacing with appropriate margins. All pages should be numbered.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE only.

**Classification:** Broaden. Generalize size-12 font, double spacing, margins and page numbering. These exact formatting requirements are currently only in the ECE clarification.

**Evidence:** [email-clarifications.md · Final Report requirements (ECE)](<../../kb/normalized/email-clarifications.md:295>).

#### 056. FR-05 — Skip

**Question (B9):** What should be included on the Final Report cover page?

**Approved answer (C9), as supplied:** Include the course name and number, your name, major, internship term, company name and location, report submission date, and internship start and end dates.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. General Final Report cover-page guidance already covers course, student, department, organization, location and dates. Use the department’s correct course code.

**Evidence:** [internship-report-templates-and-rubrics.md · Cover Page](<../../kb/normalized/internship-report-templates-and-rubrics.md:90>).

#### 057. FR-06 — Add

**Question (B10):** Do I need a Table of Contents?

**Approved answer (C10), as supplied:** Yes. Include a Table of Contents with report sections and page numbers and, where applicable, lists of tables, figures, and pictures.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Contents required for all; extra lists absent.

**Classification:** Add. The Table of Contents already exists. Add only the explicit page-number and applicable lists-of-tables/figures/pictures detail; no need to duplicate the underlying requirement.

**Evidence:** [internship-report-templates-and-rubrics.md · Table of Contents](<../../kb/normalized/internship-report-templates-and-rubrics.md:98>).

#### 058. FR-07 — Skip

**Question (B11):** What should I write in the introduction?

**Approved answer (C11), as supplied:** Explain the purpose of the internship and briefly identify the projects and types of work completed during the approved experience.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Purpose, organization and overview of work are already general.

**Evidence:** [internship-report-templates-and-rubrics.md · 1. Introduction](<../../kb/normalized/internship-report-templates-and-rubrics.md:100>).

#### 059. FR-08 — Broaden

**Question (B12):** What should I include in the main body of the Final Report?

**Approved answer (C12), as supplied:** Describe your technical and administrative activities and the engineering/computer-related projects you worked on. Also address the required engineering problem-solving and ABET-related reflection areas specified in the EECE 500 guidelines.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE exact wording; related general rubric exists.

**Classification:** Broaden. General templates already require disciplinary application and broader-impact reflection. Promote only the additional explicit engineering/science/mathematics examples and global/economic/environmental/societal reflection from ECE. Use discipline-appropriate wording and the student’s course reference; do not retain an EECE-specific guideline pointer as universal evidence.

**Evidence:** [email-clarifications.md · Final Report requirements (ECE)](<../../kb/normalized/email-clarifications.md:295>); [internship-report-templates-and-rubrics.md · 4. Application of Engineering, Design, and Disciplinary Knowledge](<../../kb/normalized/internship-report-templates-and-rubrics.md:122>); [internship-report-templates-and-rubrics.md · Final Approved Experience Report Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:162>).

#### 060. FR-09 — Broaden

**Question (B13):** Do I need to give an example of solving an engineering problem?

**Approved answer (C13), as supplied:** Yes. Provide real examples or case studies showing how you applied engineering, science, and mathematics principles to address complex engineering problems, including challenges faced and solutions developed.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE exact wording; related general rubric exists.

**Classification:** Broaden. General templates already require disciplinary application and broader-impact reflection. Promote only the additional explicit engineering/science/mathematics examples and global/economic/environmental/societal reflection from ECE. Use discipline-appropriate wording and the student’s course reference; do not retain an EECE-specific guideline pointer as universal evidence.

**Evidence:** [email-clarifications.md · Final Report requirements (ECE)](<../../kb/normalized/email-clarifications.md:295>); [internship-report-templates-and-rubrics.md · 4. Application of Engineering, Design, and Disciplinary Knowledge](<../../kb/normalized/internship-report-templates-and-rubrics.md:122>); [internship-report-templates-and-rubrics.md · Final Approved Experience Report Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:162>).

#### 061. FR-10 — Broaden

**Question (B14):** What does 'impact of engineering solutions' mean in the report?

**Approved answer (C14), as supplied:** Discuss how an engineering solution related to your internship may have global, economic, environmental, and societal impacts, and demonstrate informed engineering judgment.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE exact wording; related general rubric exists.

**Classification:** Broaden. General templates already require disciplinary application and broader-impact reflection. Promote only the additional explicit engineering/science/mathematics examples and global/economic/environmental/societal reflection from ECE. Use discipline-appropriate wording and the student’s course reference; do not retain an EECE-specific guideline pointer as universal evidence.

**Evidence:** [email-clarifications.md · Final Report requirements (ECE)](<../../kb/normalized/email-clarifications.md:295>); [internship-report-templates-and-rubrics.md · 4. Application of Engineering, Design, and Disciplinary Knowledge](<../../kb/normalized/internship-report-templates-and-rubrics.md:122>); [internship-report-templates-and-rubrics.md · Final Approved Experience Report Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:162>).

#### 062. FR-11 — Skip

**Question (B15):** What should I write about acquiring and applying new knowledge?

**Approved answer (C15), as supplied:** Explain what new knowledge or skills you needed, how you learned them, which learning strategies or resources you used, and how you applied the new knowledge to your internship work.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All general learning requirements; ECE more explicit.

**Classification:** Skip. Acquiring new skills and explaining their application are already general report expectations. Treat learning strategies/resources as elaboration of that existing expectation, not a new policy.

**Evidence:** [internship-report-templates-and-rubrics.md · 5. Professional Skills and Workplace Learning](<../../kb/normalized/internship-report-templates-and-rubrics.md:138>); [internship-report-templates-and-rubrics.md · 6. Challenges, Problem Solving, and Adaptation](<../../kb/normalized/internship-report-templates-and-rubrics.md:142>); [email-clarifications.md · Final Report requirements (ECE)](<../../kb/normalized/email-clarifications.md:295>).

#### 063. FR-12 — Skip

**Question (B16):** What should I include in the conclusion?

**Approved answer (C16), as supplied:** Discuss the benefits gained from the training, how it enriched your knowledge, relevant deficiencies you recognized in your education, and useful suggestions for improving the training program.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Benefits, learning, gaps in preparation and recommendations already exist.

**Evidence:** [internship-report-templates-and-rubrics.md · 8. Conclusions and Recommendations](<../../kb/normalized/internship-report-templates-and-rubrics.md:150>).

#### 064. FR-13 — Skip

**Question (B17):** Do I need references in the Final Report?

**Approved answer (C17), as supplied:** Yes. Sources used in the report must be cited in the text and listed in a dedicated References section.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. In-text citations and a reference list are already general.

**Evidence:** [internship-report-templates-and-rubrics.md · References](<../../kb/normalized/internship-report-templates-and-rubrics.md:154>).

#### 065. FR-14 — Skip

**Question (B18):** Can I include drawings, calculations, or technical documents?

**Approved answer (C18), as supplied:** Yes. Supporting material such as drawings, plans, calculations, technical documents, or literature may be included in the appendix and should be referenced properly in the report.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Drawings, calculations and technical documentation in referenced appendices are already permitted.

**Evidence:** [internship-report-templates-and-rubrics.md · Appendices](<../../kb/normalized/internship-report-templates-and-rubrics.md:158>).

#### 066. FR-15 — Skip

**Question (B19):** Can two students who interned together submit the same report?

**Approved answer (C19), as supplied:** No. Each student must write and submit the report independently, even if several students worked at the same company or on the same project.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Independent authorship even for students sharing a company/project is already general.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

#### 067. FR-16 — Skip

**Question (B20):** What happens if I omit one of the required core sections?

**Approved answer (C20), as supplied:** Missing required core content can cause the report to be evaluated as unsatisfactory. Follow the report structure and rubric carefully.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Missing core content and unsatisfactory assessment are already in the rubric.

**Evidence:** [internship-report-templates-and-rubrics.md · Final Approved Experience Report Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:162>).

#### 068. FR-17 — Hold

**Question (B21):** How should I prepare the Final Report if I completed two internships or an internship plus research?

**Approved answer (C21), as supplied:** Cover every approved experience component and clearly separate the activities completed in each. For the Dar Al-Handasah 6+2 arrangement, EECE requires separate documentation for the two-week research component. For other combined arrangements, confirm whether Moodle requires one combined report or separate reports.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** ECE only.

**Classification:** Hold. Current ECE source explicitly requires one report covering two internships and a separate research report for 6+2. Workbook replaces the one-report instruction with “confirm whether” and associates separate research documentation with Dar. Clarify whether this revises the existing instruction. See C9.

**Evidence:** [email-clarifications.md · Reports for multiple approved components (ECE)](<../../kb/normalized/email-clarifications.md:315>).

#### 069. FR-18 — Broaden

**Question (B22):** What should I do if company information is confidential?

**Approved answer (C22), as supplied:** Do not disclose confidential or proprietary information. Ask your supervisor what may be included, anonymize sensitive details where possible, and explain the technical work at an appropriate level. Contact the course coordinator if confidentiality prevents you from completing a required section.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE report rule; all-department presentation rule.

**Classification:** Broaden. Promote the report-specific supervisor check, anonymization and coordinator escalation for confidentiality to all departments. General presentation confidentiality already exists.

**Evidence:** [email-clarifications.md · Final Report requirements (ECE)](<../../kb/normalized/email-clarifications.md:295>); [internship-report-templates-and-rubrics.md · Presentation Requirements](<../../kb/normalized/internship-report-templates-and-rubrics.md:178>).

### Sheet: ece specific4

#### 070. VOP-01 — Skip

**Question (B5):** Do I need to submit a Final Voice-Over Presentation?

**Approved answer (C5), as supplied:** Yes. For EECE 500, follow the current Moodle instructions for the Final Voice-Over Presentation as part of the final course deliverables.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** ECE requirement and timing.

**Classification:** Skip. ECE VOP requirement and one-week completion deadline already exist. Keep ECE scope; other departments have different presentation rules.

**Evidence:** [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>); [summer-training-guidelines-2026.md · Electrical and Computer Engineering (ECE)](<../../kb/normalized/summer-training-guidelines-2026.md:240>); [email-clarifications.md · Summer-graduate deadlines (ECE)](<../../kb/normalized/email-clarifications.md:223>).

#### 071. VOP-02 — Skip

**Question (B6):** How many slides can I use in the VOP?

**Approved answer (C6), as supplied:** The EECE 500 Voice-Over Presentation should contain a maximum of 5 slides.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** ECE VOP limit.

**Classification:** Skip. Five slides, three minutes per slide and fifteen minutes total are already explicit for ECE. Do not generalize to CHEM or IEM.

**Evidence:** [email-clarifications.md · Final Voice-over Presentation duration (ECE)](<../../kb/normalized/email-clarifications.md:323>).

#### 072. VOP-03 — Skip

**Question (B7):** How long can the audio be?

**Approved answer (C7), as supplied:** Each slide may contain audio lasting up to 3 minutes.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** ECE VOP limit.

**Classification:** Skip. Five slides, three minutes per slide and fifteen minutes total are already explicit for ECE. Do not generalize to CHEM or IEM.

**Evidence:** [email-clarifications.md · Final Voice-over Presentation duration (ECE)](<../../kb/normalized/email-clarifications.md:323>).

#### 073. VOP-04 — Skip

**Question (B8):** What should the VOP contain?

**Approved answer (C8), as supplied:** Include an introduction, the main content of your internship experience, and a conclusion. Cover key objectives, work performed, challenges encountered, and lessons learned.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All presentation guidance; ECE VOP included.

**Classification:** Skip. Concise explanation of work, challenges and learning with relevant visuals is already covered. Narrated format is separately supported for ECE.

**Evidence:** [internship-report-templates-and-rubrics.md · 3. Final Presentation](<../../kb/normalized/internship-report-templates-and-rubrics.md:174>); [internship-report-templates-and-rubrics.md · Suggested Slide Structure](<../../kb/normalized/internship-report-templates-and-rubrics.md:186>); [internship-report-templates-and-rubrics.md · Final Presentation Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:194>).

#### 074. VOP-05 — Skip

**Question (B9):** Should I include technical details in the presentation?

**Approved answer (C9), as supplied:** Yes. The presentation should clearly reflect the work and activities you performed and the technical experience gained.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All presentation guidance; ECE VOP included.

**Classification:** Skip. Concise explanation of work, challenges and learning with relevant visuals is already covered. Narrated format is separately supported for ECE.

**Evidence:** [internship-report-templates-and-rubrics.md · 3. Final Presentation](<../../kb/normalized/internship-report-templates-and-rubrics.md:174>); [internship-report-templates-and-rubrics.md · Suggested Slide Structure](<../../kb/normalized/internship-report-templates-and-rubrics.md:186>); [internship-report-templates-and-rubrics.md · Final Presentation Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:194>).

#### 075. VOP-06 — Skip

**Question (B10):** Should I use pictures, graphs, or charts?

**Approved answer (C10), as supplied:** Yes. Appropriate pictures, diagrams, graphs, charts, and other relevant visuals are encouraged to improve understanding and engagement.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All presentation guidance; ECE VOP included.

**Classification:** Skip. Concise explanation of work, challenges and learning with relevant visuals is already covered. Narrated format is separately supported for ECE.

**Evidence:** [internship-report-templates-and-rubrics.md · 3. Final Presentation](<../../kb/normalized/internship-report-templates-and-rubrics.md:174>); [internship-report-templates-and-rubrics.md · Suggested Slide Structure](<../../kb/normalized/internship-report-templates-and-rubrics.md:186>); [internship-report-templates-and-rubrics.md · Final Presentation Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:194>).

#### 076. VOP-07 — Skip

**Question (B11):** Can my presentation just be text copied from my report?

**Approved answer (C11), as supplied:** No. The presentation should concisely communicate the main internship experience and use an effective structure and relevant visuals rather than simply reproducing report text.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All presentation guidance; ECE VOP included.

**Classification:** Skip. Concise explanation of work, challenges and learning with relevant visuals is already covered. Narrated format is separately supported for ECE.

**Evidence:** [internship-report-templates-and-rubrics.md · 3. Final Presentation](<../../kb/normalized/internship-report-templates-and-rubrics.md:174>); [internship-report-templates-and-rubrics.md · Suggested Slide Structure](<../../kb/normalized/internship-report-templates-and-rubrics.md:186>); [internship-report-templates-and-rubrics.md · Final Presentation Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:194>).

#### 077. VOP-08 — Skip

**Question (B12):** What is the Final Voice-Over Presentation?

**Approved answer (C12), as supplied:** It is a narrated presentation summarizing the main approved-experience activities, technical work, challenges, lessons learned, and outcomes.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** All presentation guidance; ECE VOP included.

**Classification:** Skip. Concise explanation of work, challenges and learning with relevant visuals is already covered. Narrated format is separately supported for ECE.

**Evidence:** [internship-report-templates-and-rubrics.md · 3. Final Presentation](<../../kb/normalized/internship-report-templates-and-rubrics.md:174>); [internship-report-templates-and-rubrics.md · Suggested Slide Structure](<../../kb/normalized/internship-report-templates-and-rubrics.md:186>); [internship-report-templates-and-rubrics.md · Final Presentation Rubric](<../../kb/normalized/internship-report-templates-and-rubrics.md:194>).

#### 078. VOP-09 — Skip

**Question (B13):** Should I submit a PowerPoint with audio or a screen-recorded video?

**Approved answer (C13), as supplied:** The EECE 500 guideline specifies a PowerPoint with audio recorded on the slides. Unless the current Moodle submission instructions explicitly request another format, submit the narrated PowerPoint.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** ECE narrated PowerPoint.

**Classification:** Skip. Narrated PowerPoint is already the ECE submission format unless current Moodle requests another. The bot cannot grant an accommodation.

**Evidence:** [email-clarifications.md · Final Voice-over Presentation duration (ECE)](<../../kb/normalized/email-clarifications.md:323>).

#### 079. VOP-10 — Skip

**Question (B14):** What is the maximum total duration of the Final VOP?

**Approved answer (C14), as supplied:** The presentation may contain up to five slides, with up to three minutes of recorded audio per slide. This gives a maximum narrated duration of 15 minutes; you do not need to use the full time.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** ECE VOP limit.

**Classification:** Skip. Five slides, three minutes per slide and fifteen minutes total are already explicit for ECE. Do not generalize to CHEM or IEM.

**Evidence:** [email-clarifications.md · Final Voice-over Presentation duration (ECE)](<../../kb/normalized/email-clarifications.md:323>).

#### 080. VOP-11 — Skip

**Question (B15):** When is the Final VOP due?

**Approved answer (C15), as supplied:** Submit the Final Voice-Over Presentation within one week after completing the approved internship unless the current Moodle page announces an earlier official deadline, such as a graduation-related deadline.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** ECE requirement and timing.

**Classification:** Skip. ECE VOP requirement and one-week completion deadline already exist. Keep ECE scope; other departments have different presentation rules.

**Evidence:** [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>); [summer-training-guidelines-2026.md · Electrical and Computer Engineering (ECE)](<../../kb/normalized/summer-training-guidelines-2026.md:240>); [email-clarifications.md · Summer-graduate deadlines (ECE)](<../../kb/normalized/email-clarifications.md:223>).

#### 081. VOP-12 — Skip

**Question (B16):** Can I submit the PowerPoint without audio?

**Approved answer (C16), as supplied:** No. A Voice-Over Presentation requires recorded narration. A presentation without audio does not satisfy the requirement unless an alternative accommodation has been formally approved.

**Fill / intended scope:** Not green · ECE for this workbook entry; preserve any broader existing source rule.

**Current KB scope:** ECE narrated PowerPoint.

**Classification:** Skip. Narrated PowerPoint is already the ECE submission format unless current Moodle requests another. The bot cannot grant an accommodation.

**Evidence:** [email-clarifications.md · Final Voice-over Presentation duration (ECE)](<../../kb/normalized/email-clarifications.md:323>).

### Sheet: 09_Employer_Letter

#### 082. EMP-01 — Skip

**Question (B5):** Do I need a letter from my employer?

**Approved answer (C5), as supplied:** Yes. An official completion/evaluation letter from the employer or internship supervisor is a required part of the internship documentation.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 083. EMP-02 — Skip

**Question (B6):** What should the employer letter include?

**Approved answer (C6), as supplied:** The official letter should include the internship start and end dates, projects/tasks completed, a brief evaluation of your work, and the employer/supervisor's signature.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 084. EMP-03 — Add

**Question (B7):** Does AUB have a specific employer-letter template?

**Approved answer (C7), as supplied:** A fixed template is not required by the guideline. The employer may use the company's official letter format as long as all required information is included. Always check Moodle in case an updated template is provided.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Checklist general; no-template permission absent.

**Classification:** Add. Add once: a fixed completion-letter template is not normally required; official employer format is acceptable if all required information is included, subject to any current Moodle template. Do not confuse this with the separate CO-OP employer evaluation form.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>).

#### 085. EMP-04 — Skip

**Question (B8):** Does the employer letter need to be signed?

**Approved answer (C8), as supplied:** Yes. The employer or supervisor should sign the official completion/evaluation letter.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 086. EMP-05 — Skip

**Question (B9):** Does the employer letter need company letterhead?

**Approved answer (C9), as supplied:** The letter should be an official company document. Company letterhead is appropriate and is explicitly required for supporting approval letters in several internship-approval situations.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official completion documentation and letterhead for the specified approval-letter procedure are already present. Do not infer that every completion letter has an additional letterhead rule from the petition rule alone.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [summer-training-guidelines-2026.md · If the Company Is Already Listed with the CDC](<../../kb/normalized/summer-training-guidelines-2026.md:78>).

#### 087. EMP-06 — Skip

**Question (B10):** Can the employer simply state that I worked there?

**Approved answer (C10), as supplied:** No. The completion letter should include the required internship dates, projects/tasks completed, a brief evaluation of your work, and a signature.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 088. EMP-07 — Skip

**Question (B11):** When should I ask my employer for the letter?

**Approved answer (C11), as supplied:** Ask early. The guideline recommends requesting it approximately 2–3 weeks before your internship ends because companies often need time to prepare official documents.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Requesting the letter 2–3 weeks early and providing it at completion are already general.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>).

#### 089. EMP-10 — Skip

**Question (B12):** What is the employer completion letter?

**Approved answer (C12), as supplied:** It is an official document from the employer or approved supervisor confirming that you completed the approved experience. It may also be called the Notice of Completion or employer evaluation letter.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 090. EMP-11 — Skip

**Question (B13):** What should I do if the company refuses to issue the employer letter?

**Approved answer (C13), as supplied:** Inform the course coordinator immediately and provide written evidence of the refusal. Ask whether an official email from an authorized supervisor or another official document may be accepted for your case. Do not substitute an informal document without approval.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Employer refusal and coordinator-approved alternatives are already general.

**Evidence:** [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

### Sheet: 10_Surveys

#### 091. SUR-01 — Hold

**Question (B5):** Do I need to complete an Internship Survey?

**Approved answer (C5), as supplied:** Yes. Complete the student internship survey/evaluation required on the current Moodle page at the end of your internship.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** General Summary Sheet; evaluation only some departments.

**Classification:** Hold. All three answers imply a student survey/evaluation is a required deliverable for everyone. Current guideline separates the universal Summary Sheet from the Student Evaluation Form “for some departments.” Confirm whether the workbook expands that obligation or uses “survey” for the Summary Sheet. See C6.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>).

#### 092. SUR-02 — Hold

**Question (B6):** Is the Internship Survey the same as the employer letter?

**Approved answer (C6), as supplied:** No. The student internship survey and the employer/supervisor completion or evaluation documentation are separate course requirements.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** General Summary Sheet; evaluation only some departments.

**Classification:** Hold. All three answers imply a student survey/evaluation is a required deliverable for everyone. Current guideline separates the universal Summary Sheet from the Student Evaluation Form “for some departments.” Confirm whether the workbook expands that obligation or uses “survey” for the Summary Sheet. See C6.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>).

#### 093. SUR-05 — Hold

**Question (B7):** What student survey or self-evaluation must I submit after the internship?

**Approved answer (C7), as supplied:** Complete the student internship survey or self-evaluation listed on the current Moodle page after finishing the internship. The exact form name may vary by term, but it is a required final deliverable.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** General Summary Sheet; evaluation only some departments.

**Classification:** Hold. All three answers imply a student survey/evaluation is a required deliverable for everyone. Current guideline separates the universal Summary Sheet from the Student Evaluation Form “for some departments.” Confirm whether the workbook expands that obligation or uses “survey” for the Summary Sheet. See C6.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Course completion requirements (ECE)](<../../kb/normalized/email-clarifications.md:231>).

### Sheet: ece specific 5

#### 094. AI-01 — Skip

**Question (B5):** Can I use AI to help write my EECE 500 report?

**Approved answer (C5), as supplied:** Limited AI assistance may be allowed under the current EECE 500 policy, but the report must reflect your own internship experience, knowledge, analysis, and writing. Always follow the AI policy stated on the current Moodle page.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Original work, limited/disclosed AI assistance, revision and proper citation already apply to all departments. Do not remove the currently documented thresholds just because these short answers omit them.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>); [internship-report-templates-and-rubrics.md · References](<../../kb/normalized/internship-report-templates-and-rubrics.md:154>).

#### 095. AI-02 — Hold

**Question (B6):** What is the maximum allowed AI percentage?

**Approved answer (C6), as supplied:** Follow the AI threshold stated on the current EECE 500 Moodle page. The active course policy should be treated as authoritative because the threshold may be updated between offerings.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Hold. Current KB gives a 25% AI cap, mandatory disclosure/citation and a 20% similarity cap. Workbook defers the AI cap/disclosure to Moodle and describes 20% as historically used. No replacement number is supplied. Resolve whether the existing assertions remain current or must become dated/conditional guidance. See C11.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

#### 096. AI-03 — Hold

**Question (B7):** Do I have to disclose AI use?

**Approved answer (C7), as supplied:** Follow the current EECE 500 instructions on acknowledgment or citation of AI-assisted content. You remain responsible for the accuracy and originality of your submission.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Hold. Current KB gives a 25% AI cap, mandatory disclosure/citation and a 20% similarity cap. Workbook defers the AI cap/disclosure to Moodle and describes 20% as historically used. No replacement number is supplied. Resolve whether the existing assertions remain current or must become dated/conditional guidance. See C11.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

#### 097. AI-04 — Skip

**Question (B8):** What happens if my report has too much AI-generated content?

**Approved answer (C8), as supplied:** A submission that exceeds the permitted AI threshold may be considered unsatisfactory and may be returned for revision. The final submission must satisfy the course policy.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Original work, limited/disclosed AI assistance, revision and proper citation already apply to all departments. Do not remove the currently documented thresholds just because these short answers omit them.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>); [internship-report-templates-and-rubrics.md · References](<../../kb/normalized/internship-report-templates-and-rubrics.md:154>).

#### 098. AI-05 — Add

**Question (B9):** Is the AI percentage the same as the Turnitin similarity percentage?

**Approved answer (C9), as supplied:** No. AI detection and text-similarity/plagiarism checking measure different things and should not be treated as the same score.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Separate limits present; explicit distinction absent.

**Classification:** Add. Add a brief general explanation that AI-detection and text-similarity results are different measures and are not interchangeable. This is an explanatory clarification, not a new threshold.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

#### 099. AI-06 — Skip

**Question (B10):** Can I use Grammarly or another editing tool?

**Approved answer (C10), as supplied:** Editing tools may assist with grammar and language, but the submitted report must remain your own work and comply with the current EECE 500 AI and academic-integrity requirements.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Original work, limited/disclosed AI assistance, revision and proper citation already apply to all departments. Do not remove the currently documented thresholds just because these short answers omit them.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>); [internship-report-templates-and-rubrics.md · References](<../../kb/normalized/internship-report-templates-and-rubrics.md:154>).

#### 100. AI-07 — Skip

**Question (B11):** Can I copy company material or descriptions into my report?

**Approved answer (C11), as supplied:** Information obtained from company materials or other sources should be paraphrased appropriately where necessary and cited. Sources used in the report must be referenced.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Original work, limited/disclosed AI assistance, revision and proper citation already apply to all departments. Do not remove the currently documented thresholds just because these short answers omit them.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>); [internship-report-templates-and-rubrics.md · References](<../../kb/normalized/internship-report-templates-and-rubrics.md:154>).

#### 101. AI-08 — Skip

**Question (B12):** Can I copy parts of another student's report?

**Approved answer (C12), as supplied:** No. The report must be written independently. Copying another student's work is not permitted.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Independent authorship even for students sharing a company/project is already general.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

#### 102. AI-09 — Hold

**Question (B13):** What is the maximum Turnitin similarity percentage allowed?

**Approved answer (C13), as supplied:** The EECE 500 course has used a maximum Turnitin similarity threshold of 20%. Follow the current Moodle policy because thresholds may be updated, cite sources properly, and avoid copying company or external text without appropriate quotation and reference.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Hold. Current KB gives a 25% AI cap, mandatory disclosure/citation and a 20% similarity cap. Workbook defers the AI cap/disclosure to Moodle and describes 20% as historically used. No replacement number is supplied. Resolve whether the existing assertions remain current or must become dated/conditional guidance. See C11.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

### Sheet: 12_Grading

#### 103. GRD-01 — Skip

**Question (B5):** Is the internship course graded with a letter grade?

**Approved answer (C5), as supplied:** No. It is evaluated on a Pass/Fail basis.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Pass/Fail, satisfactory deliverables, report revision and timeliness are already general.

**Evidence:** [summer-training-guidelines-2026.md · Evaluation and Grading](<../../kb/normalized/summer-training-guidelines-2026.md:212>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>); [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

#### 104. GRD-05 — Skip

**Question (B6):** Can I be asked to revise a report?

**Approved answer (C6), as supplied:** Yes. Students may be required to revise reports that do not meet the department's expectations or required guidelines.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Pass/Fail, satisfactory deliverables, report revision and timeliness are already general.

**Evidence:** [summer-training-guidelines-2026.md · Evaluation and Grading](<../../kb/normalized/summer-training-guidelines-2026.md:212>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>); [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

#### 105. GRD-06 — Skip

**Question (B7):** What happens if my Progress Report or Final Report is unsatisfactory?

**Approved answer (C7), as supplied:** Follow the revision instructions provided by the course team. A satisfactory evaluation of the required work is necessary to pass the course.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Pass/Fail, satisfactory deliverables, report revision and timeliness are already general.

**Evidence:** [summer-training-guidelines-2026.md · Evaluation and Grading](<../../kb/normalized/summer-training-guidelines-2026.md:212>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>); [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

#### 106. GRD-07 — Skip

**Question (B8):** Are deadlines important even though the course is Pass/Fail?

**Approved answer (C8), as supplied:** Yes. Timely completion of the required deliverables is part of the course requirements.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Pass/Fail, satisfactory deliverables, report revision and timeliness are already general.

**Evidence:** [summer-training-guidelines-2026.md · Evaluation and Grading](<../../kb/normalized/summer-training-guidelines-2026.md:212>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>); [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>).

### Sheet: 13_Internship_Problems

#### 107. PROB-01 — Skip

**Question (B5):** What should I do if my internship tasks are not related to engineering?

**Approved answer (C5), as supplied:** Contact the internship coordinator/course team as soon as possible. Do not wait until the internship ends. The approved experience should provide meaningful engineering or professional work related to your field.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Promptly report irrelevant/changed work or supervisor/company problems; already general.

**Evidence:** [summer-training-guidelines-2026.md · Professional Expectations During the Internship](<../../kb/normalized/summer-training-guidelines-2026.md:119>); [email-clarifications.md · Problems or changes during an internship](<../../kb/normalized/email-clarifications.md:67>).

#### 108. PROB-02 — Skip

**Question (B6):** What if the company changes my assigned tasks after I start?

**Approved answer (C6), as supplied:** If the new work no longer matches the approved internship objectives or lacks meaningful content, contact the internship coordinator promptly.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Promptly report irrelevant/changed work or supervisor/company problems; already general.

**Evidence:** [summer-training-guidelines-2026.md · Professional Expectations During the Internship](<../../kb/normalized/summer-training-guidelines-2026.md:119>); [email-clarifications.md · Problems or changes during an internship](<../../kb/normalized/email-clarifications.md:67>).

#### 109. PROB-03 — Skip

**Question (B7):** What if I have a problem with my supervisor or company?

**Approved answer (C7), as supplied:** Raise significant internship problems promptly with the department/internship coordinator and, when applicable, the CDC.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Promptly report irrelevant/changed work or supervisor/company problems; already general.

**Evidence:** [summer-training-guidelines-2026.md · Professional Expectations During the Internship](<../../kb/normalized/summer-training-guidelines-2026.md:119>); [email-clarifications.md · Problems or changes during an internship](<../../kb/normalized/email-clarifications.md:67>).

#### 110. PROB-04 — Skip

**Question (B8):** Should I keep records of what I do during the internship?

**Approved answer (C8), as supplied:** Yes. Keep a daily or regular record of tasks, projects, skills learned, meetings, and observations. These notes will help when preparing your reports and presentation.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Daily work records to support reports already exist; no automatic log-submission requirement is introduced.

**Evidence:** [summer-training-guidelines-2026.md · Professional Expectations During the Internship](<../../kb/normalized/summer-training-guidelines-2026.md:119>); [email-clarifications.md · Current dates and daily internship records](<../../kb/normalized/email-clarifications.md:381>).

#### 111. PROB-05 — Skip

**Question (B9):** What professional behavior is expected during the internship?

**Approved answer (C9), as supplied:** Maintain punctuality, regular attendance, professional communication, respect, responsibility, accountability, and proper workplace conduct.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Professional conduct expectations are already present.

**Evidence:** [summer-training-guidelines-2026.md · Professional Expectations During the Internship](<../../kb/normalized/summer-training-guidelines-2026.md:119>).

#### 112. PROB-06 — Skip

**Question (B10):** Can I request an extension for a deadline?

**Approved answer (C10), as supplied:** Extensions are not automatic. Contact the course coordinator before the deadline, explain the reason, provide supporting evidence when relevant, and state the date by which you can submit.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Request an extension before the deadline with justification and supporting evidence; already general.

**Evidence:** [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

#### 113. PROB-07 — Skip

**Question (B11):** My supervisor is unavailable to complete a form or letter. What should I do?

**Approved answer (C11), as supplied:** Ask whether another authorized company representative, such as HR or the supervisor’s manager, can issue the official document. Confirm the alternative signatory or document with the course coordinator before submitting it.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Alternate authorized signatory and coordinator confirmation are already covered.

**Evidence:** [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

### Sheet: 14_Concurrent_Course

#### 114. CRS-01 — Hold

**Question (B5):** Can I take another summer course while completing my internship?

**Approved answer (C5), as supplied:** Students may enroll in a course alongside an internship, provided that the internship lasts a minimum of 10 weeks, is approved by the employer, and meets the required total work hours. The course must be scheduled either before 8:30 AM or after 4:30 PM.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Ten-week/time-window rule ECE only; MECH/CEE differ.

**Classification:** Hold. Green proposes ten weeks and before-8:30/after-4:30 timing for all departments. Current source makes this an ECE rule, while MECH/CEE document work-hour conditions without that minimum. Confirm the intended supersession before broadening. See C4.

**Evidence:** [email-clarifications.md · Taking another summer course (ECE)](<../../kb/normalized/email-clarifications.md:287>); [summer-training-guidelines-2026.md · Mechanical Engineering (MECH)](<../../kb/normalized/summer-training-guidelines-2026.md:231>); [summer-training-guidelines-2026.md · Civil and Environmental Engineering (CEE)](<../../kb/normalized/summer-training-guidelines-2026.md:263>).

#### 115. CRS-02 — Hold

**Question (B6):** How long must my internship be if I take another course at the same time?

**Approved answer (C6), as supplied:** 10 weeks minimum

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Ten-week/time-window rule ECE only; MECH/CEE differ.

**Classification:** Hold. Green proposes ten weeks and before-8:30/after-4:30 timing for all departments. Current source makes this an ECE rule, while MECH/CEE document work-hour conditions without that minimum. Confirm the intended supersession before broadening. See C4.

**Evidence:** [email-clarifications.md · Taking another summer course (ECE)](<../../kb/normalized/email-clarifications.md:287>); [summer-training-guidelines-2026.md · Mechanical Engineering (MECH)](<../../kb/normalized/summer-training-guidelines-2026.md:231>); [summer-training-guidelines-2026.md · Civil and Environmental Engineering (CEE)](<../../kb/normalized/summer-training-guidelines-2026.md:263>).

#### 116. CRS-03 — Hold

**Question (B7):** Can I assume an 8-week internship is enough if I am also taking another course?

**Approved answer (C7), as supplied:** No.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Ten-week/time-window rule ECE only; MECH/CEE differ.

**Classification:** Hold. Green proposes ten weeks and before-8:30/after-4:30 timing for all departments. Current source makes this an ECE rule, while MECH/CEE document work-hour conditions without that minimum. Confirm the intended supersession before broadening. See C4.

**Evidence:** [email-clarifications.md · Taking another summer course (ECE)](<../../kb/normalized/email-clarifications.md:287>); [summer-training-guidelines-2026.md · Mechanical Engineering (MECH)](<../../kb/normalized/summer-training-guidelines-2026.md:231>); [summer-training-guidelines-2026.md · Civil and Environmental Engineering (CEE)](<../../kb/normalized/summer-training-guidelines-2026.md:263>).

### Sheet: 15_Deadlines

#### 117. DEAD-01 — Skip

**Question (B5):** When are my deliverables due?

**Approved answer (C5), as supplied:** Deadlines are based on your internship timeline and the official dates posted on the current Moodle page or communicated to you. Check Moodle regularly.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Follow the approved placement timeline and current Moodle/coordinator dates; already general. The explicit Week-4 start-date clarification is tracked separately.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>); [email-clarifications.md · Current dates and daily internship records](<../../kb/normalized/email-clarifications.md:381>).

#### 118. DEAD-02 — Skip

**Question (B6):** When is the Proposal due?

**Approved answer (C6), as supplied:** Submit the Proposal once the internship is confirmed and before beginning the approved experience.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Proposal after confirmation and before the internship is already general.

**Evidence:** [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>); [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>).

#### 119. DEAD-03 — Skip

**Question (B7):** When is the Notice of Arrival due?

**Approved answer (C7), as supplied:** Submit it during the first week of the internship.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Notice of Arrival after starting, during the first week, is already general.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 120. DEAD-04 — Correct citation

**Question (B8):** When is the Progress Report due?

**Approved answer (C8), as supplied:** Follow the current Moodle deadline. The May 2026 MSFEA guideline specifies the end of Week 4 of training.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Correct citation. End-of-Week-4 timing is already covered. The workbook cites May 2026; the source available in this repo is June 2026. No deadline policy change is needed on the evidence available. See C12.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>).

#### 121. DEAD-05 — Skip

**Question (B9):** When is the Final Training Report due?

**Approved answer (C9), as supplied:** Normally within one week after completing the approved internship, unless Moodle announces another official deadline.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. The general Final Report deadline is already within one week after completion, with coordinator handling of exceptional/current-term schedules.

**Evidence:** [summer-training-guidelines-2026.md · Final Training Report](<../../kb/normalized/summer-training-guidelines-2026.md:195>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 122. DEAD-06 — Skip

**Question (B10):** When is the employer letter due?

**Approved answer (C10), as supplied:** It is required at the completion of the internship. Request it approximately 2–3 weeks before your internship ends so that it can be ready by the course deadline.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Requesting the letter 2–3 weeks early and providing it at completion are already general.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>).

#### 123. DEAD-07 — Skip

**Question (B11):** I finished my internship later than other students. Do I use their deadline?

**Approved answer (C11), as supplied:** Follow the deadline applicable to your approved internship timeline and any official course deadline posted on Moodle.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Follow the approved placement timeline and current Moodle/coordinator dates; already general. The explicit Week-4 start-date clarification is tracked separately.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>); [email-clarifications.md · Current dates and daily internship records](<../../kb/normalized/email-clarifications.md:381>).

#### 124. DEAD-08 — Skip

**Question (B12):** Can I submit something late without asking?

**Approved answer (C12), as supplied:** No. Do not assume late submissions or extensions are automatically accepted. Follow the official deadline or obtain formal approval where an exception is needed.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Deadlines remain binding unless an exception is approved; already covered.

**Evidence:** [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>); [summer-training-guidelines-2026.md · Course Description](<../../kb/normalized/summer-training-guidelines-2026.md:12>).

### Sheet: 16_Guardrails

#### 125. SAFE-04 — Skip

**Question (B5):** My friend was allowed to do this last year. Can I?

**Approved answer (C5), as supplied:** Do not treat a previous individual exception as a general rule. Explain the current policy and direct the student to obtain approval if the arrangement requires an exception.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; individual approvals remain individual.

**Classification:** Skip. No new policy: prior approval applies to the student’s own placement. Retain current department exceptions; do not turn someone else’s past approval into a standing permission.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>).

#### 126. SAFE-05 — Skip

**Question (B6):** Can the chatbot approve my internship or petition?

**Approved answer (C6), as supplied:** No. The chatbot provides information only. Formal approvals, exceptions, petitions, and extensions must be handled by authorized course/department personnel.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All; human approval.

**Classification:** Skip. Approval authority is the department/course instructor, not the chatbot. No new approval capability or policy is needed.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Internships at Startups](<../../kb/normalized/summer-training-guidelines-2026.md:95>).

#### 127. SAFE-06 — Skip

**Question (B7):** Can I skip the employer letter?

**Approved answer (C7), as supplied:** No. The employer/supervisor completion or evaluation documentation is a required deliverable.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Required documentation must be complete and satisfactory; already universal. Do not present an unconditional Fail when the source allows authorized remediation.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [summer-training-guidelines-2026.md · Evaluation and Grading](<../../kb/normalized/summer-training-guidelines-2026.md:212>).

#### 128. SAFE-07 — Skip

**Question (B8):** Can I skip the Proposal or Notice of Arrival because I already started?

**Approved answer (C8), as supplied:** No. Required forms remain required. The student should follow Moodle instructions and contact the course team if a deadline has already been missed.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Starting does not remove the Proposal/Arrival requirements. Coordinate late submissions rather than promising automatic acceptance.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

#### 129. SAFE-08 — Skip

**Question (B9):** Can I pass with one missing deliverable?

**Approved answer (C9), as supplied:** No. The internship file must be complete and required submissions must be satisfactory.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Required documentation must be complete and satisfactory; already universal. Do not present an unconditional Fail when the source allows authorized remediation.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [summer-training-guidelines-2026.md · Evaluation and Grading](<../../kb/normalized/summer-training-guidelines-2026.md:212>).

#### 130. SAFE-09 — Skip

**Question (B10):** Can I use a high amount of AI if the content is correct?

**Approved answer (C10), as supplied:** No. The submission must follow the AI threshold and academic-integrity rules stated on the current Moodle page.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Original work, limited/disclosed AI assistance, revision and proper citation already apply to all departments. Do not remove the currently documented thresholds just because these short answers omit them.

**Evidence:** [email-clarifications.md · AI use, similarity, and report revision](<../../kb/normalized/email-clarifications.md:183>); [internship-report-templates-and-rubrics.md · References](<../../kb/normalized/internship-report-templates-and-rubrics.md:154>).

#### 131. SAFE-10 — Skip

**Question (B11):** Can I submit only 6 weeks because the company does not offer more?

**Approved answer (C11), as supplied:** No. A 6-week internship alone does not meet the requirement. Follow the approved additional-experience rule or obtain formal approval for any exception.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** General eight weeks plus approved exceptions.

**Classification:** Skip. This answer already leaves room for formal exceptions. Preserve the CEE/IEM specifics rather than inventing a universal additional-experience route.

**Evidence:** [summer-training-guidelines-2026.md · Internship Requirements](<../../kb/normalized/summer-training-guidelines-2026.md:31>); [summer-training-guidelines-2026.md · Department-Specific Rules](<../../kb/normalized/summer-training-guidelines-2026.md:227>).

### Sheet: 18_Search_Scheduling

#### 132. PLAN-01 — Skip

**Question (B5):** Who is responsible for finding the internship?

**Approved answer (C5), as supplied:** Students are responsible for securing their own internship opportunities, with support from the department internship coordinator and the MSFEA Career Development Center.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Student responsibility and CDC postings/application support already exist.

**Evidence:** [summer-training-guidelines-2026.md · Securing an Internship through the CDC](<../../kb/normalized/summer-training-guidelines-2026.md:54>); [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>); [cdc-knowledge-base.md · How to apply through the CDC](<../../kb/normalized/cdc-knowledge-base.md:24>).

#### 133. PLAN-02 — Skip

**Question (B6):** How can the MSFEA Career Development Center help me find an internship?

**Approved answer (C6), as supplied:** The CDC shares internship opportunities, supports applications, and provides guidance on self-secured internships and company documentation. Monitor CDC postings and contact the CDC when assistance is needed.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Student responsibility and CDC postings/application support already exist.

**Evidence:** [summer-training-guidelines-2026.md · Securing an Internship through the CDC](<../../kb/normalized/summer-training-guidelines-2026.md:54>); [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>); [cdc-knowledge-base.md · How to apply through the CDC](<../../kb/normalized/cdc-knowledge-base.md:24>).

#### 134. PLAN-03 — Skip

**Question (B7):** What type of work is acceptable for the internship course

**Approved answer (C7), as supplied:** The work must provide meaningful professional experience related to your discipline and involve engineering, computing, design, analysis, or technical problem solving. Work that is mainly unrelated business, finance, or administrative activity may not meet the course objectives.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** General disciplinary relevance plus department restrictions.

**Classification:** Skip. Meaningful work related to the student’s field is already required. “May not meet” is consistent with that general rule; preserve specific MECH/CHEM finance/banking prohibitions.

**Evidence:** [summer-training-guidelines-2026.md · Internships That Are Not Accepted](<../../kb/normalized/summer-training-guidelines-2026.md:39>); [summer-training-guidelines-2026.md · Department-Specific Rules](<../../kb/normalized/summer-training-guidelines-2026.md:227>).

#### 135. PLAN-04 — Skip

**Question (B8):** How many work hours are normally required?

**Approved answer (C8), as supplied:** The standard expectation is approximately 320 hours, based on eight full weeks at about 40 hours per week. A different schedule must still satisfy the approved duration and may require formal review.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All standard; exceptions department-specific.

**Classification:** Skip. Approximately 320 hours over eight weeks is already the standard. Do not convert it into approval for an unreviewed alternative schedule.

**Evidence:** [summer-training-guidelines-2026.md · Internship Requirements](<../../kb/normalized/summer-training-guidelines-2026.md:31>).

#### 136. PLAN-05 — Skip

**Question (B9):** Can my internship be longer than eight weeks?

**Approved answer (C9), as supplied:** Yes. An approved internship may be longer than eight weeks. Make sure your forms and final employer letter show the correct actual dates.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Longer placements, uncertain dates, late starts and completion beyond usual deadlines already have general guidance.

**Evidence:** [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 137. PLAN-06 — Skip

**Question (B10):** My internship end date is not fixed. What date should I enter?

**Approved answer (C10), as supplied:** Use the best confirmed date provided by the employer. If it changes, inform the course coordinator and correct the relevant Moodle form when instructed. The final employer letter must state the actual start and end dates.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Longer placements, uncertain dates, late starts and completion beyond usual deadlines already have general guidance.

**Evidence:** [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 138. PLAN-07 — Skip

**Question (B11):** What if my internship starts late in the summer?

**Approved answer (C11), as supplied:** A late start may be acceptable only if you can still complete the approved duration. Submit the required forms according to your actual timeline and contact the course coordinator if completion will fall after the official course or graduation deadlines.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Longer placements, uncertain dates, late starts and completion beyond usual deadlines already have general guidance.

**Evidence:** [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 139. PLAN-08 — Skip

**Question (B12):** My internship ends after the course submission deadline. What should I do?

**Approved answer (C12), as supplied:** Inform the course coordinator before the deadline. Students finishing later may receive a timeline tied to their actual completion date, but the applicable deadline must be confirmed for the current term and may affect graduation processing.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Longer placements, uncertain dates, late starts and completion beyond usual deadlines already have general guidance.

**Evidence:** [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 140. PLAN-09 — Broaden

**Question (B13):** Is a gap allowed between two approved internship components?

**Approved answer (C13), as supplied:** A gap may be acceptable only when the full combined arrangement, dates, and both components have been approved in writing. Do not assume a gap is accepted without confirmation.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE gap rule; CHEM same-summer restriction.

**Classification:** Broaden. Broaden the conditional gap guidance: full schedule and both components require written approval. Retain CHEM’s same-summer condition and each department’s underlying split eligibility.

**Evidence:** [email-clarifications.md · Gap between approved components](<../../kb/normalized/email-clarifications.md:273>); [summer-training-guidelines-2026.md · Chemical Engineering (CHEM)](<../../kb/normalized/summer-training-guidelines-2026.md:246>).

#### 141. PLAN-10 — Skip

**Question (B14):** My internship supervisor changed after I started. What should I do?

**Approved answer (C14), as supplied:** Inform the course coordinator immediately and provide the new supervisor’s name, title, and email. Your Proposal or Notice of Arrival may need to be corrected or resubmitted.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Supervisor changes, new-company approval and cancellation response already exist.

**Evidence:** [email-clarifications.md · Problems or changes during an internship](<../../kb/normalized/email-clarifications.md:67>).

#### 142. PLAN-11 — Skip

**Question (B15):** I changed companies after my internship was approved. Can I continue?

**Approved answer (C15), as supplied:** A new company or substantially different experience requires new approval. Contact the course coordinator and CDC immediately, submit the required documents, and do not assume the previous approval carries over.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Supervisor changes, new-company approval and cancellation response already exist.

**Evidence:** [email-clarifications.md · Problems or changes during an internship](<../../kb/normalized/email-clarifications.md:67>).

#### 143. PLAN-12 — Skip

**Question (B16):** What happens if the company cancels my internship?

**Approved answer (C16), as supplied:** Notify the course coordinator and CDC immediately. You will need an alternative approved arrangement and updated documentation. Keep the cancellation email or letter as supporting evidence.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Supervisor changes, new-company approval and cancellation response already exist.

**Evidence:** [email-clarifications.md · Problems or changes during an internship](<../../kb/normalized/email-clarifications.md:67>).

### Sheet: 19_Co-op

#### 144. COOP-01 — Skip

**Question (B5):** What is the minimum duration of the co-op experience?

**Approved answer (C5), as supplied:** The co-op experience must last at least six full months.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** All CO-OP departments.

**Classification:** Skip. Six-month minimum already exists. Keep CO-OP program scope; this is not the ordinary internship duration.

**Evidence:** [msfea-cdc-coop-handbook.md · What CO-OP is](<../../kb/normalized/msfea-cdc-coop-handbook.md:17>).

#### 145. COOP-02 — Hold

**Question (B6):** When should a co-op student submit the Proposal for Approved Experience?

**Approved answer (C6), as supplied:** Submit the Proposal on Moodle as soon as the co-op placement is confirmed.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** CO-OP self-found proposal; all CO-OP arrival form.

**Classification:** Hold. The CO-OP handbook has a specific proposal for self-found placements and a first-week Arrival form. A generic Approved Experience Proposal on Moodle for every CO-OP is a new obligation, not established by the handbook. The Arrival portion is already covered. See C7.

**Evidence:** [msfea-cdc-coop-handbook.md · Application and admission process](<../../kb/normalized/msfea-cdc-coop-handbook.md:144>); [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>).

#### 146. COOP-03 — Skip

**Question (B7):** When should a co-op student submit the Notice of Arrival?

**Approved answer (C7), as supplied:** Submit the Notice of Arrival after the co-op starts. Do not submit it before the actual start date.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** All CO-OP departments.

**Classification:** Skip. Arrival after start is already covered; retain the more precise existing first-week deadline.

**Evidence:** [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>).

#### 147. COOP-04 — Skip

**Question (B8):** When is the co-op Progress Report due?

**Approved answer (C8), as supplied:** Submit the co-op Progress Report at the end of the third month of the co-op.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** All CO-OP departments.

**Classification:** Skip. End-of-third-month progress report already exists; retain its one-page format.

**Evidence:** [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>).

#### 148. COOP-05 — Hold

**Question (B9):** What must a co-op student submit after finishing?

**Approved answer (C9), as supplied:** After completing the co-op, submit the required student self-evaluation or reflection form, the official signed employer letter, the Final Report, and the Final Voice-Over Presentation, following the current Moodle instructions.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** CO-OP handbook; additional department requirements possible.

**Classification:** Hold. Final report and student reflection already exist. Universal narrated presentation and signed company-letter obligations are not established; handbook specifies employer performance/feedback forms. Clarify whether these are additions, substitutes, or an EECE-only course process. See C7.

**Evidence:** [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>); [msfea-cdc-coop-handbook.md · Requirements to pass the co-op course (summary)](<../../kb/normalized/msfea-cdc-coop-handbook.md:259>); [msfea-cdc-coop-handbook.md · Employer responsibilities during the co-op](<../../kb/normalized/msfea-cdc-coop-handbook.md:292>).

#### 149. COOP-06 — Hold

**Question (B10):** What employer letter is required for a co-op?

**Approved answer (C10), as supplied:** Upload an official company document on letterhead, signed by the employer, confirming completion of the co-op and stating the actual duration and relevant work details.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** CO-OP handbook; additional department requirements possible.

**Classification:** Hold. Final report and student reflection already exist. Universal narrated presentation and signed company-letter obligations are not established; handbook specifies employer performance/feedback forms. Clarify whether these are additions, substitutes, or an EECE-only course process. See C7.

**Evidence:** [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>); [msfea-cdc-coop-handbook.md · Requirements to pass the co-op course (summary)](<../../kb/normalized/msfea-cdc-coop-handbook.md:259>); [msfea-cdc-coop-handbook.md · Employer responsibilities during the co-op](<../../kb/normalized/msfea-cdc-coop-handbook.md:292>).

### Sheet: 20_Email_Derived_FAQs

#### 150. EFAQ-001 — Skip

**Question (C5):** Do I need to submit a letter from my employer?

**Approved answer (D5), as supplied:** Yes. The official employer or supervisor completion/evaluation letter is a required EECE 500 deliverable.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 151. EFAQ-002 — Add

**Question (C6):** Does AUB have a template or evaluation form that my employer can complete?

**Approved answer (D6), as supplied:** A fixed template is not normally required. The employer may use its official format if all required information is included; always check the current Moodle page for any updated template.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Checklist general; no-template permission absent.

**Classification:** Add. Add once: a fixed completion-letter template is not normally required; official employer format is acceptable if all required information is included, subject to any current Moodle template. Do not confuse this with the separate CO-OP employer evaluation form.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>).

#### 152. EFAQ-003 — Skip

**Question (C7):** What information must the employer letter include?

**Approved answer (D7), as supplied:** It should include the internship start and end dates, completed projects or tasks, a brief evaluation of the student’s work, and the employer or supervisor’s signature.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 153. EFAQ-004 — Hold

**Question (C8):** Can I ask for the employer letter before my internship finishes?

**Approved answer (D8), as supplied:** This applied for summer graduate Yes. If issued early, it should state the actual start date, expected end date, and work or tasks completed, subject to the current Moodle requirements.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE summer graduates only; acceptance conditional.

**Classification:** Hold. The answer begins “This applied for summer graduate Yes.” Existing source requires course-team confirmation before accepting an early letter. Green broadens department scope but does not erase the summer-graduate or approval conditions; confirm intended population and acceptance rule. See C10.

**Evidence:** [email-clarifications.md · Early or temporarily delayed employer letter (ECE)](<../../kb/normalized/email-clarifications.md:127>).

#### 154. EFAQ-005 — Skip

**Question (C9):** What should I do if HR says the employer letter will be delayed?

**Approved answer (D9), as supplied:** The letter remains required. Follow up with HR and contact the course team before the deadline rather than assuming the requirement is waived.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** General coordinator/exception guidance; specific temporary email ECE.

**Classification:** Skip. Letter remains required and student contacts the course team before the deadline; covered by existing general requirements. Temporary-email acceptance is a separate scope expansion.

**Evidence:** [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>); [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

#### 155. EFAQ-006 — Broaden

**Question (C10):** Can my supervisor send an official email while I wait for the signed letter?

**Approved answer (D10), as supplied:** Only with course-team approval. An official email may be accepted temporarily in an exceptional delay, but the final signed letter must still be submitted when instructed.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE only.

**Classification:** Broaden. Promote temporary official supervisor email during an exceptional delay to all departments, preserving course-team approval and the eventual signed-letter requirement.

**Evidence:** [email-clarifications.md · Early or temporarily delayed employer letter (ECE)](<../../kb/normalized/email-clarifications.md:127>).

#### 156. EFAQ-007 — Skip

**Question (C11):** Who should provide the letter if my internship or research was supervised by an AUB professor?

**Approved answer (D11), as supplied:** The supervising faculty member or appropriate AUB unit should provide the official completion/evaluation documentation.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 157. EFAQ-008 — Skip

**Question (C12):** Is the document I received the required employer letter, or is it only part of my presentation?

**Approved answer (D12), as supplied:** It qualifies only if it is an official employer/supervisor document containing the required dates, tasks, evaluation, and signature.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Official employer/approved-supervisor completion letter, dates, tasks, evaluation and signature are already universal. The current checklist also requires a stamp: retain it; the workbook’s shorter answers do not expressly waive it. Faculty documentation applies only to an approved research experience.

**Evidence:** [summer-training-guidelines-2026.md · Notice of Completion / Employer Letter Checklist](<../../kb/normalized/summer-training-guidelines-2026.md:200>); [email-clarifications.md · Employer and research documentation exceptions](<../../kb/normalized/email-clarifications.md:111>).

#### 158. EFAQ-009 — Skip

**Question (C13):** Can I pass EECE 500 without the employer letter?

**Approved answer (D13), as supplied:** No. Missing any required deliverable leaves the internship file incomplete and may result in a Fail.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Required documentation must be complete and satisfactory; already universal. Do not present an unconditional Fail when the source allows authorized remediation.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [summer-training-guidelines-2026.md · Evaluation and Grading](<../../kb/normalized/summer-training-guidelines-2026.md:212>).

#### 159. EFAQ-010 — Skip

**Question (C14):** My internship ends after the common course deadline. When should I submit the final documents?

**Approved answer (D14), as supplied:** Contact the course coordinator before the deadline. Students finishing later may receive a submission timeline tied to their actual completion date.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Longer placements, uncertain dates, late starts and completion beyond usual deadlines already have general guidance.

**Evidence:** [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 160. EFAQ-012 — Broaden

**Question (C15):** My internship was extended after I completed eight weeks. Should I submit now or wait until it officially ends?

**Approved answer (D15), as supplied:** Ask the course coordinator to confirm, particularly when the extended period includes new tasks, results, or learning that should appear in the final submissions.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE only; related general dates guidance exists.

**Classification:** Broaden. Broaden the explicit instruction to ask whether submission follows the required eight weeks or the extended end date. Do not invent an automatic deadline.

**Evidence:** [email-clarifications.md · Submission timing after an internship extension (ECE)](<../../kb/normalized/email-clarifications.md:103>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 161. EFAQ-013 — Broaden

**Question (C16):** I am a summer graduate. Do I have an earlier deadline?

**Approved answer (D16), as supplied:** Summer graduates may have earlier deadlines because grades must be processed sooner. Follow the graduating-student Moodle announcement or coordinator email.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE only.

**Classification:** Broaden. Move the shared summer-graduate deadline clarification to all-department scope. Keep “may receive earlier deadlines” and current Moodle/coordinator control; no fixed date is introduced.

**Evidence:** [email-clarifications.md · Summer-graduate deadlines (ECE)](<../../kb/normalized/email-clarifications.md:223>).

#### 162. EFAQ-014 — Skip

**Question (C17):** Can I request an extension for a required submission?

**Approved answer (D17), as supplied:** Extensions are not automatic. Request one before the deadline, explain the reason, provide evidence when relevant, and state the proposed submission date.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Request an extension before the deadline with justification and supporting evidence; already general.

**Evidence:** [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

#### 163. EFAQ-015 — Add

**Question (C18):** Is the Progress Report deadline counted from my internship start date?

**Approved answer (D18), as supplied:** Internship-week deadlines are normally counted from your approved internship start date unless Moodle announces a common course deadline.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** Related timeline is general; explicit interpretation absent.

**Classification:** Add. Add one general clarification: internship-week deadlines normally run from the student’s own approved start date unless Moodle specifies a common deadline. Existing Week-4 wording implies this but does not explicitly resolve the semester-start question.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 164. EFAQ-016 — Skip

**Question (C19):** Should I submit the Proposal before my internship is confirmed?

**Approved answer (D19), as supplied:** No. Submit it after confirmation, using accurate organization, supervisor, dates, and work details.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Proposal after confirmation and before the internship is already general.

**Evidence:** [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>); [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>).

#### 165. EFAQ-017 — Skip

**Question (C20):** When should I submit the Notice of Arrival?

**Approved answer (D20), as supplied:** Submit it after you actually start the internship and within the deadline stated on Moodle.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Notice of Arrival after starting, during the first week, is already general.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Internship dates and duration changes](<../../kb/normalized/email-clarifications.md:87>).

#### 166. EFAQ-018 — Skip

**Question (C21):** I already started but forgot the Proposal or Notice of Arrival. Are they still required?

**Approved answer (D21), as supplied:** Yes. Both are required forms. Submit them immediately and follow any coordinator instructions for a late or corrected submission.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Starting does not remove the Proposal/Arrival requirements. Coordinate late submissions rather than promising automatic acceptance.

**Evidence:** [summer-training-guidelines-2026.md · Internship Timeline and Deliverables](<../../kb/normalized/summer-training-guidelines-2026.md:144>); [email-clarifications.md · Deadline extensions and petition delays](<../../kb/normalized/email-clarifications.md:211>).

#### 167. EFAQ-019 — Skip

**Question (C22):** The dates or supervisor in my Moodle form are wrong. How can I correct them?

**Approved answer (D22), as supplied:** Contact the course coordinator with the correct information. The form may need to be reopened or removed so you can resubmit.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Wrong form details, restricted final submissions and upload troubleshooting already exist generally. VOP remains required only where the department requires it.

**Evidence:** [email-clarifications.md · Moodle submissions and corrections](<../../kb/normalized/email-clarifications.md:39>).

#### 168. EFAQ-026 — Skip

**Question (C23):** I found the internship myself. Do I need a petition or CDC approval?

**Approved answer (D23), as supplied:** Follow the CDC self-secured internship procedure and obtain all required approvals. The CDC will guide on whether a petition is required

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. CDC guidance, self-secured form and required approvals already exist. Preserve the more detailed petition checklist in the June guideline.

**Evidence:** [cdc-knowledge-base.md · Applying to an internship found independently](<../../kb/normalized/cdc-knowledge-base.md:32>); [summer-training-guidelines-2026.md · Securing an Internship Independently](<../../kb/normalized/summer-training-guidelines-2026.md:70>).

#### 169. EFAQ-027 — Skip

**Question (C24):** My petition was approved, but I am still not on the Moodle page. What should I do?

**Approved answer (D24), as supplied:** Send the course coordinator your name, ID, and approval so your registration and Moodle access can be checked.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Moodle-access checks and distinct AUBSIS registration process already exist. These instructions do not authorize the bot to collect/store student identifiers.

**Evidence:** [email-clarifications.md · Moodle access and registration](<../../kb/normalized/email-clarifications.md:27>).

#### 170. EFAQ-028 — Skip

**Question (C25):** I am not yet showing on AUBSIS. Can I still access Moodle and submit?

**Approved answer (D25), as supplied:** Contact the course coordinator for the Moodle check, but resolve official AUBSIS registration through the appropriate academic or Registrar process.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Moodle-access checks and distinct AUBSIS registration process already exist. These instructions do not authorize the bot to collect/store student identifiers.

**Evidence:** [email-clarifications.md · Moodle access and registration](<../../kb/normalized/email-clarifications.md:27>).

#### 171. EFAQ-029 — Skip

**Question (C26):** My Progress Report is satisfactory, but the Final Report or VOP box is still blocked. What should I do?

**Approved answer (D26), as supplied:** Check all prerequisites and then send the course coordinator a screenshot so the Moodle restriction can be reviewed.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Wrong form details, restricted final submissions and upload troubleshooting already exist generally. VOP remains required only where the department requires it.

**Evidence:** [email-clarifications.md · Moodle submissions and corrections](<../../kb/normalized/email-clarifications.md:39>).

#### 172. EFAQ-030 — Skip

**Question (C27):** I cannot upload a required file. What should I do before the deadline?

**Approved answer (D27), as supplied:** Check the file type, size, deadline, and prerequisites; if the problem remains, send a screenshot to the course coordinator before the deadline.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** All internship departments.

**Classification:** Skip. Wrong form details, restricted final submissions and upload troubleshooting already exist generally. VOP remains required only where the department requires it.

**Evidence:** [email-clarifications.md · Moodle submissions and corrections](<../../kb/normalized/email-clarifications.md:39>).

#### 173. EFAQ-031 — Broaden

**Question (C28):** Why does Moodle show a red X instead of Done after I submitted?

**Approved answer (D28), as supplied:** Check the activity-completion requirements. If every requirement is satisfied and the status remains unchanged, send the coordinator a screenshot.

**Fill / intended scope:** Green · All internship departments.

**Current KB scope:** ECE only.

**Classification:** Broaden. Promote red-X/activity-completion troubleshooting and screenshot escalation to all departments.

**Evidence:** [email-clarifications.md · Moodle completion status (ECE)](<../../kb/normalized/email-clarifications.md:59>).

#### 174. EFAQ-040 — Skip

**Question (C29):** What is the minimum duration of the co-op experience?

**Approved answer (D29), as supplied:** The co-op must last at least six full months.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** All CO-OP departments.

**Classification:** Skip. Six-month minimum already exists. Keep CO-OP program scope; this is not the ordinary internship duration.

**Evidence:** [msfea-cdc-coop-handbook.md · What CO-OP is](<../../kb/normalized/msfea-cdc-coop-handbook.md:17>).

#### 175. EFAQ-041 — Hold

**Question (C30):** When should a co-op student submit the Proposal and Notice of Arrival?

**Approved answer (D30), as supplied:** Submit the Proposal when the co-op is confirmed and the Notice of Arrival after the co-op actually starts.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** CO-OP self-found proposal; all CO-OP arrival form.

**Classification:** Hold. The CO-OP handbook has a specific proposal for self-found placements and a first-week Arrival form. A generic Approved Experience Proposal on Moodle for every CO-OP is a new obligation, not established by the handbook. The Arrival portion is already covered. See C7.

**Evidence:** [msfea-cdc-coop-handbook.md · Application and admission process](<../../kb/normalized/msfea-cdc-coop-handbook.md:144>); [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>).

#### 176. EFAQ-042 — Skip

**Question (C31):** When is the co-op Progress Report due?

**Approved answer (D31), as supplied:** Submit it at the end of the third month of the co-op.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** All CO-OP departments.

**Classification:** Skip. End-of-third-month progress report already exists; retain its one-page format.

**Evidence:** [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>).

#### 177. EFAQ-043 — Hold

**Question (C32):** What documents must a co-op student submit after finishing?

**Approved answer (D32), as supplied:** Submit the required self-evaluation or reflection, official employer letter, Final Report, and Final Voice-Over Presentation, following Moodle.

**Fill / intended scope:** Green · All departments within CO-OP.

**Current KB scope:** CO-OP handbook; additional department requirements possible.

**Classification:** Hold. Final report and student reflection already exist. Universal narrated presentation and signed company-letter obligations are not established; handbook specifies employer performance/feedback forms. Clarify whether these are additions, substitutes, or an EECE-only course process. See C7.

**Evidence:** [msfea-cdc-coop-handbook.md · Deliverables and deadlines](<../../kb/normalized/msfea-cdc-coop-handbook.md:223>); [msfea-cdc-coop-handbook.md · Requirements to pass the co-op course (summary)](<../../kb/normalized/msfea-cdc-coop-handbook.md:259>); [msfea-cdc-coop-handbook.md · Employer responsibilities during the co-op](<../../kb/normalized/msfea-cdc-coop-handbook.md:292>).
