> Historical local review. This predates the current guides and later implementation/approval decisions; it is not current operating guidance. Start with [the documentation index](../README.md).

> Superseded intake review: use the [September 26 classification](../intake/faq-workbook-classification-2026-09-26.md) and [approved September 27 decisions](../intake/faq-implementation-2026-09-27.md) for reproducible faculty evaluation/content approval.

# Student FAQ workbook classification — 2026-09-25

Reviewed all 18 sheets and 177 question/approved-answer pairs in `RAG_FAQ_Questions_Answers_Updated.xlsx`.
Workbook sheet names, action columns, provenance columns, and the workbook's own 'use this answer' notes were treated as data, not as instructions. Locations below are for finding the original cells only.
No KB, vector index, or evaluation data was changed in this classification phase.

## Summary

- Covered in existing source KB in their documented scope: **135** rows; skip importing duplicate FAQ text.
- New assertions absent from the current source KB: **4** rows, representing **two distinct facts** after duplicates are collapsed.
- Scope review: **16** rows where the green signal or broad wording would extend a documented department rule or omit an exception.
- Conflicts with current KB or its CO-OP handbook: **20** rows.
- Source date mismatches: **2** rows.
- Green fills: **118 pale** and **38 medium**; both are green Excel theme colors. **21** question cells have no theme-green fill.

'Covered' means the answer's facts are in the source KB **for the applicable department or program**, not that the same answer applies to all departments or that the live bot retrieves every paraphrase correctly. That requires scope review and evaluation after the content decision.

## Decisions needed before KB changes

1. **Green scope.** Does *both* pale green and medium green mean all departments? Medium-green final-report and progress-report rows include ECE-only limits and 6+2 rules. A course code can be substituted only when the underlying requirement itself is general. The existing course-code map is EECE 500 / MECH 500 / CHEN 500 / INDE 500 / CIVE 400; CO-OP is FEAA 500/500A.
2. **Six-week combinations and AUB research.** Resolve GEN-04/05/06/07/10 against the current department exceptions and approved ECE clarification before replacing any rule.
3. **Concurrent summer course.** Confirm whether CRS-01/02/03 are newly intended for all departments, or only ECE. Current KB documents a ten-week schedule for ECE, a work-hours condition for MECH, and a separate CEE allowance.
4. **CO-OP deliverables.** Confirm whether a newer official CO-OP course instruction supersedes the handbook's FEAA 500/500A deliverables and forms. In particular, ask whether every CO-OP student now owes an internship Proposal, employer letter, and Final Voice-Over Presentation.
5. **Survey applicability.** Confirm which department(s) require the student internship survey/evaluation in addition to the general Summary Sheet.
6. **Two new facts.** Confirm that no fixed employer completion-letter template is required, and that internship-week deadlines generally run from each student's own approved start date unless Moodle sets a shared deadline.
7. **Source date.** Two answers cite 'May 2026' while the official guideline in this repo is dated June 2026; confirm which revision should govern.

## KB sources checked

- [Summer Training Guidelines — June 2026](../../kb/normalized/summer-training-guidelines-2026.md): general timeline and deliverables, employer-letter checklist, and department-specific exceptions.
- [Approved Internship Email Clarifications](../../kb/normalized/email-clarifications.md): course codes, ECE summer-course and 6+2 rules, combined reports, AI policy, Moodle workflow, and employer-letter exceptions.
- [Internship Report Templates and Rubrics](../../kb/normalized/internship-report-templates-and-rubrics.md): common report structure and general length guidance.
- [MSFEA CO-OP Handbook](../../kb/normalized/msfea-cdc-coop-handbook.md): FEAA 500/500A forms, reports, employer evaluation, and program duration.
- [CDC Knowledge Base](../../kb/normalized/cdc-knowledge-base.md): CDC processes and recurring general questions.

## Row-by-row classification

### 01_General

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | GEN-01 | What is EECE 500? | Pale green | Covered |
| B6 | GEN-01 | What is MECH 500? | Pale green | Covered |
| B7 | GEN-01 | What is CHEN 500? | Pale green | Covered |
| B8 | GEN-01 | What is INDE 500? | Pale green | Covered |
| B9 | GEN-01 | What is CIVE 400? | Pale green | Covered |
| B10 | GEN-02 | Is the internship course required for graduation? | Pale green | Covered |
| B11 | GEN-03 | How long must my internship be? | Pale green | Scope review — Eight weeks is the general minimum, but IEM and CEE have documented exceptional six-week approvals. |
| B12 | GEN-04 | Is a 6-week internship enough? | Pale green | Conflict — 6+2 at another company is stated as a general route; the KB documents department exceptions and a MECH prohibition. |
| B13 | GEN-05 | What should I do if my company offers only a 6-week internship? | Pale green | Conflict — Same broad 6+2 rule as the previous row; cannot apply it to every department. |
| B14 | GEN-06 | Can I do 6 weeks at one company and 2 weeks at another company? | Pale green | Conflict — Restricts the two-week research route to Dar Al-Handasah, while current ECE clarification does not. |
| B15 | GEN-07 | Can I combine two internships? | Pale green | Conflict — Calls a 6+4 second-company placement the standard ECE arrangement; current KB requires case-specific approval unless another summer course triggers the ten-week rule. |
| B16 | GEN-08 | Can I split the internship into two 4-week internships? | Pale green | Scope review — The generic answer omits that MECH prohibits 4+4 while CEE permits it under a specific condition. |
| B17 | GEN-10 | Can I do my approved experience at AUB with a professor? | Pale green | Conflict — Absolute 'not accepted' omits documented special-circumstance and department research exceptions for AUB placements. |
| B18 | GEN-11 | What are the requirements for the Dar Al-Handasah 6+2 arrangement? | Pale green | Scope review — The underlying 6+2 research route is documented for ECE and IEM, not every department; MECH prohibits this add-on. |
| B19 | GEN-12 | Can I do my internship outside Lebanon? | Pale green | Covered |

### 02_Approval_Petitions

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | APR-01 | Does my internship need to be approved before I start? | Pale green | Covered |
| B6 | APR-02 | I found the internship myself. What should I do? | Pale green | Covered |
| B7 | APR-03 | Do I need a petition for a self-secured internship? | Pale green | Covered |
| B8 | APR-04 | What should the company letter for an internship-approval petition contain? | Pale green | Covered |
| B9 | APR-05 | My company is not listed with the CDC. Can I still intern there? | Pale green | Covered |
| B10 | APR-06 | Are startup internships accepted? | Pale green | Covered |
| B11 | APR-07 | Who approves an internship exception? | Pale green | Covered |
| B12 | APR-08 | Can I start first and ask for approval later? | Pale green | Covered |
| B13 | APR-09 | What happens if my petition is incomplete? | Pale green | Covered |
| B14 | APR-10 | My friend received approval for the same arrangement last year. Does that mean mine is approved? | Pale green | Covered |
| B15 | APR-11 | What documents are needed if the company is already listed with the CDC? | Pale green | Covered |
| B16 | APR-12 | What must an internship petition include? | Pale green | Covered |
| B17 | APR-13 | How do I request an exception to an internship rule? | Pale green | Covered |

### 03_Remote

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | REM-01 | Are fully online or remote internships accepted? | Pale green | Scope review — General remote-work rejection must retain the documented IEM U.S.-based exception. |
| B6 | REM-02 | Remote internships were accepted in a previous summer. Does that mean mine is accepted? | Pale green | Covered |
| B7 | REM-03 | Should I accept a remote internship first and petition later? | Pale green | Covered |

### ece specific2

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | RES-01 | Do I have to watch the EECE 500 lectures and videos? | None/other | Covered |
| B6 | RES-02 | Do I have to take the Moodle quiz? | None/other | Covered |
| B7 | RES-03 | Can I attempt the quiz more than once? | None/other | Conflict — Says multiple quiz attempts are allowed; current KB says they may be available and current Moodle controls the setting. |
| B8 | RES-04 | What is the passing grade for the EECE 500 quiz? | None/other | Covered |
| B9 | RES-05 | Why do I need to complete the lectures, videos, and quiz? | None/other | Covered |
| B10 | RES-06 | Why can’t I access the Moodle quiz? | None/other | Covered |
| B11 | RES-07 | What if I do not reach the quiz passing score? | None/other | Covered |
| B12 | RES-08 | I missed the quiz deadline. Can it be reopened? | None/other | Covered |

### ece specific3

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | PR-01 | Do I have to submit a Progress Report? | Medium green | Covered |
| B6 | PR-02 | When is the Progress Report due? | Medium green | Source mismatch — Approved answer calls the general guideline May 2026; the repo's official guideline is June 2026. |
| B7 | PR-03 | Is the Progress Report deadline counted from the summer semester start or from my internship start date? | Medium green | New — The general rule that internship-week deadlines run from each student's own start date is not stated explicitly in the current source KB. |
| B8 | PR-04 | What should I include in my Progress Report? | Medium green | Covered |
| B9 | PR-05 | How long should the Progress Report be? | Medium green | Covered |
| B10 | PR-06 | Can I submit the Final Report instead of the Progress Report? | Medium green | Covered |
| B11 | PR-07 | My Progress Report is much longer than required. Will it be accepted? | Medium green | Covered |
| B12 | PR-08 | If I have two approved internships, which one should the Progress Report cover? | Medium green | Covered |
| B13 | PR-09 | For the Dar Al-Handasah 6+2 arrangement, what should the Progress Report cover? | Medium green | Scope review — The 6+2 research route is documented for ECE and IEM, and prohibited as an add-on in MECH; the green cell cannot make it universal. |
| B14 | PR-10 | I am a summer graduate. Do I need to submit the Progress Report earlier? | Medium green | Scope review — Earlier summer-graduate deadlines are documented only in the ECE clarification, despite the green fill. |
| B15 | PR-11 | My Progress Report was evaluated as unsatisfactory. Can I resubmit it? | Medium green | Covered |
| B16 | PR-12 | Will an initial unsatisfactory Progress Report automatically make me fail the course? | Medium green | Covered |

### ECE specific1

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | FR-01 | Is the Final Training Report required? | Medium green | Covered |
| B6 | FR-02 | When should I submit my Final Training Report? | Medium green | Covered |
| B7 | FR-03 | How long should the Final Training Report be? | Medium green | Conflict — The ECE 5-page/1,500-word/20-page limits cannot become universal; the general report template gives a different length range. |
| B8 | FR-04 | What font and spacing should I use in the Final Report? | Medium green | Scope review — Size-12, double-spaced formatting is explicitly ECE-scoped in the current clarification. |
| B9 | FR-05 | What should be included on the Final Report cover page? | Medium green | Covered |
| B10 | FR-06 | Do I need a Table of Contents? | Medium green | Covered |
| B11 | FR-07 | What should I write in the introduction? | Medium green | Covered |
| B12 | FR-08 | What should I include in the main body of the Final Report? | Medium green | Scope review — Engineering/computing and EECE ABET language requires department-aware wording before all-department use. |
| B13 | FR-09 | Do I need to give an example of solving an engineering problem? | Medium green | Scope review — Mandatory engineering/science/mathematics example is explicit for ECE; the general template uses broader discipline-specific language. |
| B14 | FR-10 | What does 'impact of engineering solutions' mean in the report? | Medium green | Scope review — The exact global/economic/environmental/societal reflection is ECE-specific; general rubric wording is broader. |
| B15 | FR-11 | What should I write about acquiring and applying new knowledge? | Medium green | Covered |
| B16 | FR-12 | What should I include in the conclusion? | Medium green | Covered |
| B17 | FR-13 | Do I need references in the Final Report? | Medium green | Covered |
| B18 | FR-14 | Can I include drawings, calculations, or technical documents? | Medium green | Covered |
| B19 | FR-15 | Can two students who interned together submit the same report? | Medium green | Covered |
| B20 | FR-16 | What happens if I omit one of the required core sections? | Medium green | Covered |
| B21 | FR-17 | How should I prepare the Final Report if I completed two internships or an internship plus research? | None/other | Conflict — For two ECE internships, current KB specifies one report with separate components; the workbook says to confirm whether one or separate reports. |
| B22 | FR-18 | What should I do if company information is confidential? | Medium green | Scope review — The report-specific clarification is currently ECE-scoped; the general template discusses confidentiality for presentations. |

### ece specific4

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | VOP-01 | Do I need to submit a Final Voice-Over Presentation? | None/other | Covered |
| B6 | VOP-02 | How many slides can I use in the VOP? | None/other | Covered |
| B7 | VOP-03 | How long can the audio be? | None/other | Covered |
| B8 | VOP-04 | What should the VOP contain? | None/other | Covered |
| B9 | VOP-05 | Should I include technical details in the presentation? | None/other | Covered |
| B10 | VOP-06 | Should I use pictures, graphs, or charts? | None/other | Covered |
| B11 | VOP-07 | Can my presentation just be text copied from my report? | None/other | Covered |
| B12 | VOP-08 | What is the Final Voice-Over Presentation? | None/other | Covered |
| B13 | VOP-09 | Should I submit a PowerPoint with audio or a screen-recorded video? | None/other | Covered |
| B14 | VOP-10 | What is the maximum total duration of the Final VOP? | None/other | Covered |
| B15 | VOP-11 | When is the Final VOP due? | None/other | Covered |
| B16 | VOP-12 | Can I submit the PowerPoint without audio? | None/other | Covered |

### 09_Employer_Letter

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | EMP-01 | Do I need a letter from my employer? | Pale green | Covered |
| B6 | EMP-02 | What should the employer letter include? | Pale green | Covered |
| B7 | EMP-03 | Does AUB have a specific employer-letter template? | Pale green | New — No current KB passage positively says a fixed employer completion-letter template is unnecessary. |
| B8 | EMP-04 | Does the employer letter need to be signed? | Pale green | Covered |
| B9 | EMP-05 | Does the employer letter need company letterhead? | Pale green | Covered |
| B10 | EMP-06 | Can the employer simply state that I worked there? | Pale green | Covered |
| B11 | EMP-07 | When should I ask my employer for the letter? | Pale green | Covered |
| B12 | EMP-10 | What is the employer completion letter? | Pale green | Covered |
| B13 | EMP-11 | What should I do if the company refuses to issue the employer letter? | Pale green | Covered |

### 10_Surveys

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | SUR-01 | Do I need to complete an Internship Survey? | Pale green | Conflict — The source guideline requires a Summary Sheet generally but a Student Evaluation Form only for some departments; the workbook makes a student survey universal. |
| B6 | SUR-02 | Is the Internship Survey the same as the employer letter? | Pale green | Covered |
| B7 | SUR-05 | What student survey or self-evaluation must I submit after the internship? | Pale green | Conflict — Likewise treats a student survey/self-evaluation as a required final deliverable for every department. |

### ece specific 5

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | AI-01 | Can I use AI to help write my EECE 500 report? | Medium green | Covered |
| B6 | AI-02 | What is the maximum allowed AI percentage? | Medium green | Covered |
| B7 | AI-03 | Do I have to disclose AI use? | Medium green | Covered |
| B8 | AI-04 | What happens if my report has too much AI-generated content? | Medium green | Covered |
| B9 | AI-05 | Is the AI percentage the same as the Turnitin similarity percentage? | Medium green | Covered |
| B10 | AI-06 | Can I use Grammarly or another editing tool? | Medium green | Covered |
| B11 | AI-07 | Can I copy company material or descriptions into my report? | Medium green | Covered |
| B12 | AI-08 | Can I copy parts of another student's report? | Medium green | Covered |
| B13 | AI-09 | What is the maximum Turnitin similarity percentage allowed? | Medium green | Covered |

### 12_Grading

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | GRD-01 | Is the internship course graded with a letter grade? | Pale green | Covered |
| B6 | GRD-05 | Can I be asked to revise a report? | Pale green | Covered |
| B7 | GRD-06 | What happens if my Progress Report or Final Report is unsatisfactory? | Pale green | Covered |
| B8 | GRD-07 | Are deadlines important even though the course is Pass/Fail? | Pale green | Covered |

### 13_Internship_Problems

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | PROB-01 | What should I do if my internship tasks are not related to engineering? | Pale green | Covered |
| B6 | PROB-02 | What if the company changes my assigned tasks after I start? | Pale green | Covered |
| B7 | PROB-03 | What if I have a problem with my supervisor or company? | Pale green | Covered |
| B8 | PROB-04 | Should I keep records of what I do during the internship? | Pale green | Covered |
| B9 | PROB-05 | What professional behavior is expected during the internship? | Pale green | Covered |
| B10 | PROB-06 | Can I request an extension for a deadline? | Pale green | Covered |
| B11 | PROB-07 | My supervisor is unavailable to complete a form or letter. What should I do? | Pale green | Covered |

### 14_Concurrent_Course

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | CRS-01 | Can I take another summer course while completing my internship? | Pale green | Conflict — The ten-week and before-8:30/after-4:30 rule is ECE-specific in the current KB, although this question is green. |
| B6 | CRS-02 | How long must my internship be if I take another course at the same time? | Pale green | Conflict — Ten weeks with another summer course is documented for ECE, not for every department. |
| B7 | CRS-03 | Can I assume an 8-week internship is enough if I am also taking another course? | Pale green | Conflict — An eight-week internship is insufficient with a concurrent course under the ECE rule, but MECH/CEE rules differ. |

### 15_Deadlines

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | DEAD-01 | When are my deliverables due? | Pale green | Covered |
| B6 | DEAD-02 | When is the Proposal due? | Pale green | Covered |
| B7 | DEAD-03 | When is the Notice of Arrival due? | Pale green | Covered |
| B8 | DEAD-04 | When is the Progress Report due? | Pale green | Source mismatch — Approved answer says May 2026 guideline; the source guideline in this repo is June 2026. |
| B9 | DEAD-05 | When is the Final Training Report due? | Pale green | Covered |
| B10 | DEAD-06 | When is the employer letter due? | Pale green | Covered |
| B11 | DEAD-07 | I finished my internship later than other students. Do I use their deadline? | Pale green | Covered |
| B12 | DEAD-08 | Can I submit something late without asking? | Pale green | Covered |

### 16_Guardrails

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | SAFE-04 | My friend was allowed to do this last year. Can I? | Pale green | Covered |
| B6 | SAFE-05 | Can the chatbot approve my internship or petition? | Pale green | Covered |
| B7 | SAFE-06 | Can I skip the employer letter? | Pale green | Covered |
| B8 | SAFE-07 | Can I skip the Proposal or Notice of Arrival because I already started? | Pale green | Covered |
| B9 | SAFE-08 | Can I pass with one missing deliverable? | Pale green | Covered |
| B10 | SAFE-09 | Can I use a high amount of AI if the content is correct? | Pale green | Covered |
| B11 | SAFE-10 | Can I submit only 6 weeks because the company does not offer more? | Pale green | Conflict — The absolute 'No' omits exceptional six-week approvals documented for selected IEM and CEE placements. |

### 18_Search_Scheduling

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | PLAN-01 | Who is responsible for finding the internship? | Pale green | Covered |
| B6 | PLAN-02 | How can the MSFEA Career Development Center help me find an internship? | Pale green | Covered |
| B7 | PLAN-03 | What type of work is acceptable for the internship course | Pale green | Covered |
| B8 | PLAN-04 | How many work hours are normally required? | Pale green | Covered |
| B9 | PLAN-05 | Can my internship be longer than eight weeks? | Pale green | Covered |
| B10 | PLAN-06 | My internship end date is not fixed. What date should I enter? | Pale green | Covered |
| B11 | PLAN-07 | What if my internship starts late in the summer? | Pale green | Covered |
| B12 | PLAN-08 | My internship ends after the course submission deadline. What should I do? | Pale green | Covered |
| B13 | PLAN-09 | Is a gap allowed between two approved internship components? | Pale green | Scope review — Current written approval rule for a gap is in the ECE clarification; no all-department rule is documented. |
| B14 | PLAN-10 | My internship supervisor changed after I started. What should I do? | Pale green | Covered |
| B15 | PLAN-11 | I changed companies after my internship was approved. Can I continue? | Pale green | Covered |
| B16 | PLAN-12 | What happens if the company cancels my internship? | Pale green | Covered |

### 19_Co-op

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| B5 | COOP-01 | What is the minimum duration of the co-op experience? | Pale green | Covered |
| B6 | COOP-02 | When should a co-op student submit the Proposal for Approved Experience? | Pale green | Conflict — The CO-OP handbook's Proposal of Cooperative Education form applies to self-found placements; it does not require every CO-OP student to submit an internship Proposal on Moodle. |
| B7 | COOP-03 | When should a co-op student submit the Notice of Arrival? | Pale green | Covered |
| B8 | COOP-04 | When is the co-op Progress Report due? | Pale green | Covered |
| B9 | COOP-05 | What must a co-op student submit after finishing? | Pale green | Conflict — The CO-OP handbook requires a final report, self-evaluation and employer performance evaluation; it does not establish a universal Final Voice-Over Presentation or signed employer letter. |
| B10 | COOP-06 | What employer letter is required for a co-op? | Pale green | Conflict — The CO-OP handbook specifies a Final Student Performance Evaluation Form, not a universal signed letter on company letterhead. |

### 20_Email_Derived_FAQs

| Cell | ID | Anonymized question | Question fill | Classification |
|---|---|---|---|---|
| C5 | EFAQ-001 | Do I need to submit a letter from my employer? | Pale green | Covered |
| C6 | EFAQ-002 | Does AUB have a template or evaluation form that my employer can complete? | Pale green | New — Duplicates the fixed-template claim in Employer Letter row 7; add once if confirmed. |
| C7 | EFAQ-003 | What information must the employer letter include? | Pale green | Covered |
| C8 | EFAQ-004 | Can I ask for the employer letter before my internship finishes? | Pale green | Conflict — Malformed answer starts 'This applied for summer graduate Yes'; current KB requires course-team confirmation and scopes early letters to ECE summer graduates. |
| C9 | EFAQ-005 | What should I do if HR says the employer letter will be delayed? | Pale green | Covered |
| C10 | EFAQ-006 | Can my supervisor send an official email while I wait for the signed letter? | Pale green | Scope review — Temporary acceptance of an official email during delay is currently an ECE-specific clarification. |
| C11 | EFAQ-007 | Who should provide the letter if my internship or research was supervised by an AUB professor? | Pale green | Covered |
| C12 | EFAQ-008 | Is the document I received the required employer letter, or is it only part of my presentation? | Pale green | Covered |
| C13 | EFAQ-009 | Can I pass EECE 500 without the employer letter? | Pale green | Covered |
| C14 | EFAQ-010 | My internship ends after the common course deadline. When should I submit the final documents? | Pale green | Covered |
| C15 | EFAQ-012 | My internship was extended after I completed eight weeks. Should I submit now or wait until it officially ends? | Pale green | Scope review — The instruction to confirm final-submission timing after extension is currently ECE-scoped. |
| C16 | EFAQ-013 | I am a summer graduate. Do I have an earlier deadline? | Pale green | Scope review — Earlier summer-graduate deadlines are documented only for ECE. |
| C17 | EFAQ-014 | Can I request an extension for a required submission? | Pale green | Covered |
| C18 | EFAQ-015 | Is the Progress Report deadline counted from my internship start date? | Pale green | New — Duplicates the start-date deadline interpretation in Progress Report row 7; add once if confirmed. |
| C19 | EFAQ-016 | Should I submit the Proposal before my internship is confirmed? | Pale green | Covered |
| C20 | EFAQ-017 | When should I submit the Notice of Arrival? | Pale green | Covered |
| C21 | EFAQ-018 | I already started but forgot the Proposal or Notice of Arrival. Are they still required? | Pale green | Covered |
| C22 | EFAQ-019 | The dates or supervisor in my Moodle form are wrong. How can I correct them? | Pale green | Covered |
| C23 | EFAQ-026 | I found the internship myself. Do I need a petition or CDC approval? | Pale green | Covered |
| C24 | EFAQ-027 | My petition was approved, but I am still not on the Moodle page. What should I do? | Pale green | Covered |
| C25 | EFAQ-028 | I am not yet showing on AUBSIS. Can I still access Moodle and submit? | Pale green | Covered |
| C26 | EFAQ-029 | My Progress Report is satisfactory, but the Final Report or VOP box is still blocked. What should I do? | Pale green | Covered |
| C27 | EFAQ-030 | I cannot upload a required file. What should I do before the deadline? | Pale green | Covered |
| C28 | EFAQ-031 | Why does Moodle show a red X instead of Done after I submitted? | Pale green | Scope review — The red-X completion-status clarification is currently ECE-scoped. |
| C29 | EFAQ-040 | What is the minimum duration of the co-op experience? | Pale green | Covered |
| C30 | EFAQ-041 | When should a co-op student submit the Proposal and Notice of Arrival? | Pale green | Conflict — Repeats a generic CO-OP Proposal requirement not established by the CO-OP handbook. |
| C31 | EFAQ-042 | When is the co-op Progress Report due? | Pale green | Covered |
| C32 | EFAQ-043 | What documents must a co-op student submit after finishing? | Pale green | Conflict — Repeats universal CO-OP final deliverables that differ from the CO-OP handbook. |

