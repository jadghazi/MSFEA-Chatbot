# Faculty full-set answer review

A case appears below if the annotated source document missed retrieval, the bot refused, or the judge marked the answer wrong/uncertain. The answer and judgment are shown so a document annotation or grader mistake can be audited.

## faculty-007-chem (CHEM)

**Question:** How long must my internship be?

**Resolved reference:** The ordinary internship minimum is eight full approved weeks; department-specific exceptions need approval.

**Annotated document hit:** False

**Bot answer:**

To satisfy the approved experience requirement, the internship must be at least 8 weeks.

**Citations:** cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete; reason: The chatbot failed to mention that department-specific exceptions to the eight-week minimum require approval, which is a critical component of the resolved policy for the Chemical Engineering department.

**Source review (Codex):** acceptable — The question asks for the ordinary minimum; eight weeks is the approved rule. The judge demanded an unasked exception caveat. The annotated document missed, but the cited CDC FAQ supports the answer.

**Retrieved passages:**

- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs (score 0.81)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs (score 0.76)
- email-clarifications.md > Combining or splitting two company internships (CHEM) (score 0.73)
- email-clarifications.md > Approved Internship Email Clarifications > Internship dates and duration changes > Submission timing after an internship extension (score 0.80)
- email-clarifications.md > Internship dates and duration changes (score 0.84)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs (score 0.77)
- email-clarifications.md > Internship dates and duration changes (score 0.82)

## faculty-010-mech (MECH)

**Question:** Can I do 6 weeks at one company and 2 weeks at another company?

**Resolved reference:** Two company weeks after six are not a documented standard route. Six company weeks alone are insufficient. Two approved faculty research weeks can complete the route if the research includes hands-on engineering work.

**Annotated document hit:** True

**Bot answer:**

Two separate four-week company periods are not accepted for Mechanical Engineering, and two separate company internships need prior department approval. The standard option is an approved eight-week company internship. Alternatively, you can do a six-week company internship combined with two weeks of approved faculty research that includes hands-on engineering work, which requires prior approval and documentation. CO-OP has its own rules — say CO-OP if that's your programme.

**Citations:** email-clarifications.md > Combining two company internships (MECH); email-clarifications.md > Company internship plus research (MECH)

**Refused:** False

**Judge:** fail; failed fields: policy_correct; reason: The chatbot incorrectly states that the standard option is an eight-week company internship, whereas the policy specifies that six company weeks alone are insufficient and requires a specific research component to meet the requirement.

**Source review (Codex):** partial — The answer gives the valid eight-week company and approved 6+2 research routes, but does not directly resolve the proposed 6+2 two-company plan. The judge's claim that eight company weeks is wrong is itself incorrect.

**Retrieved passages:**

- email-clarifications.md > Combining two company internships (MECH) (score 0.73)
- email-clarifications.md > Taking another summer course (score 0.68)
- email-clarifications.md > Company internship plus research (MECH) (score 0.71)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.70)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.69)
- email-clarifications.md > Splitting company internships (MECH) (score 0.73)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.65)

## faculty-011-ece (ECE)

**Question:** Can I combine two internships?

**Resolved reference:** Two company placements require prior written approval. After six company weeks, a second placement must last at least four weeks; a 4+4 split is case-specific and needs a petition.

**Annotated document hit:** True

**Bot answer:**

A combined company internship is not automatically accepted and requires prior written approval or petition, with each component documented and technically relevant. A six-plus-four company arrangement requires at least ten total company weeks, where the second internship lasts at least four weeks following an initial six-week placement. Alternatively, a six-week company placement can be combined with a two-week approved research component with an MSFEA faculty member, which also requires prior approval.

**Citations:** email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Combining two company internships; email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > 6+2 arrangement definition

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot incorrectly states that a 6+4 arrangement requires ten total weeks, whereas the policy specifies that a 6+4 arrangement is not automatically accepted and requires a petition, and it fails to mention that a 4+4 split is also case-specific and requires a petition.

**Source review (Codex):** acceptable — Prior written approval and the six-plus-four company duration are stated correctly. The judge incorrectly calls six plus four not ten weeks and demands an unasked 4+4 detail.

**Retrieved passages:**

- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Combining two company internships (score 0.80)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.75)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > 4+4 company-internship split (score 0.75)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Progress reporting for a 6+2 arrangement (score 0.69)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Internship Requirements: Duration, Hours, and Locations > Internships That Are Not Accepted (score 0.67)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > 6+2 arrangement definition (score 0.71)
- email-clarifications.md > Forms for a second internship (score 0.71)

## faculty-012-mech (MECH)

**Question:** Can I split the internship into two 4-week internships?

**Resolved reference:** Two separate four-week company internships are prohibited.

**Annotated document hit:** True

**Bot answer:**

No. Internships cannot be split into two separate four-week periods for MECH.

**Citations:** email-clarifications.md > Splitting company internships (MECH)

**Refused:** False

**Judge:** fail; failed fields: refusal_appropriate; reason: The chatbot correctly identified that the requested split-internship arrangement is prohibited for MECH students and provided a direct, accurate answer supported by the retrieved documentation.

**Source review (Codex):** acceptable — The answer directly and correctly rejects a MECH 4+4 split; the judge's reason agrees but its refusal flag is false.

**Retrieved passages:**

- email-clarifications.md > Splitting company internships (MECH) (score 0.85)
- email-clarifications.md > Company internship plus research (MECH) (score 0.74)
- email-clarifications.md > Combining two company internships (MECH) (score 0.75)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.78)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Mechanical Engineering (MECH) (score 0.71)
- email-clarifications.md > Taking another summer course (score 0.76)
- summer-training-guidelines-2026.md > Internship Timeline and Deliverables (score 0.69)

## faculty-012-chem (CHEM)

**Question:** Can I split the internship into two 4-week internships?

**Resolved reference:** Do not promise a 4+4 split; obtain written approval and complete components within the same summer.

**Annotated document hit:** True

**Bot answer:**

Two company placements need prior written approval, must occur within the same summer term, and must satisfy the total approved training duration of at least 8 weeks. A four-plus-four plan is not automatically accepted merely because CHEM permits internship parts within one summer.

**Citations:** email-clarifications.md > Combining or splitting two company internships (CHEM); summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Chemical Engineering (CHEM); cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs

**Refused:** False

**Judge:** fail; failed fields: refusal_appropriate; reason: The chatbot accurately conveys the requirement for prior approval, the same-summer constraint, and the necessity of meeting the 8-week minimum duration.

**Source review (Codex):** acceptable — Prior written approval, same-summer timing, and total duration are all present; the judge's reason agrees but its refusal flag is false.

**Retrieved passages:**

- email-clarifications.md > Reporting after approval of multiple internship components (score 0.78)
- email-clarifications.md > Combining or splitting two company internships (CHEM) (score 0.82)
- email-clarifications.md > Taking another summer course (score 0.76)
- email-clarifications.md > Six-week internship completion (CHEM) (score 0.70)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.71)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Chemical Engineering (CHEM) (score 0.77)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs (score 0.67)

## faculty-014-ece (ECE)

**Question:** What are the requirements for the Dar Al-Handasah 6+2 arrangement?

**Resolved reference:** Dar is not exclusive. Six company weeks plus two faculty research weeks require approval and documentation for both components, plus a separate research report.

**Annotated document hit:** True

**Bot answer:**

To pursue a six-week company internship plus two-week research arrangement, the arrangement must be approved and documented. The six company weeks and two faculty-research weeks with an MSFEA faculty member require prior approval and documentation, and eligibility depends on your department and prior approval. Dar Al-Handasah serves as one example of a company offering such placements, and the department's approval rules apply to other companies too.

**Citations:** email-clarifications.md > Company placements, AUB research, and approved gaps; email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > 6+2 arrangement definition

**Refused:** False

**Judge:** fail; failed fields: conditions_complete, refusal_appropriate; reason: The chatbot failed to mention the requirement for a separate research report, which is a key component of the 6+2 arrangement policy.

**Source review (Codex):** confirmed_gap — The broad 6+2 requirements question received approval conditions but omitted the separate research report.

**Retrieved passages:**

- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.70)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > 6+2 arrangement definition (score 0.63)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Progress reporting for a 6+2 arrangement (score 0.60)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Combining two company internships (score 0.60)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.60)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.62)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Eligibility requirements (score 0.60)

## faculty-014-iem (IEM)

**Question:** What are the requirements for the Dar Al-Handasah 6+2 arrangement?

**Resolved reference:** Dar is not exclusive. Six company weeks plus two faculty research weeks require approval and documentation for both components, plus a separate research report.

**Annotated document hit:** True

**Bot answer:**

To complete the Dar Al-Handasah six-week company placement plus two-week research arrangement, you must submit a Progress Report at the end of Week 4 of the company internship covering only that internship. For the final deliverables, submit one Final Report for the company internship and a separate research report for the approved research component. Check Moodle for additional confirmed information based on your arrangement.

**Citations:** email-clarifications.md > Company placements, AUB research, and approved gaps

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, retrieval_sufficient; reason: The chatbot failed to mention the essential requirement of prior approval and documentation for the arrangement, which is a critical condition for eligibility.

**Source review (Codex):** confirmed_gap — The answer listed reporting steps but omitted prior approval for the 6+2 arrangement.

**Retrieved passages:**

- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.70)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.60)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.62)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Eligibility requirements (score 0.60)
- email-clarifications.md > Current policy and individual exceptions (score 0.59)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Eligibility requirements (score 0.58)
- email-clarifications.md > Combining two company internships (IEM) (score 0.55)

## faculty-014-cee (CEE)

**Question:** What are the requirements for the Dar Al-Handasah 6+2 arrangement?

**Resolved reference:** Dar is not exclusive. The proposed two-week faculty research addition to six company weeks requires Chair approval; if approved, document both components and submit a separate research report. A separate exceptional six-week approval exists for selected companies.

**Annotated document hit:** True

**Bot answer:**

Submit a separate research report in addition to the company internship Final Report. You must also submit your Progress Report at the end of Week 4 of the company internship, covering only the company internship. Check Moodle for additional confirmed information based on your arrangement.

**Citations:** email-clarifications.md > Reporting after approval of multiple internship components; email-clarifications.md > Company placements, AUB research, and approved gaps

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot failed to mention the essential requirement of obtaining Chair approval for the 6+2 arrangement.

**Source review (Codex):** confirmed_gap — The answer listed reports but omitted Chair approval for the proposed research addition.

**Retrieved passages:**

- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.70)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.60)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.62)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Eligibility requirements (score 0.60)
- email-clarifications.md > Current policy and individual exceptions (score 0.59)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Eligibility requirements (score 0.58)
- email-clarifications.md > Combining two company internships (CEE) (score 0.52)

## faculty-017-chem (CHEM)

**Question:** I found the internship myself. What should I do?

**Resolved reference:** If you secured the internship independently rather than through the CDC, complete the CDC self-secured internship procedure and obtain the required departmental approval before starting.

**Annotated document hit:** True

**Bot answer:**

To complete your internship approval, fill out the self-secured internship form at https://forms.office.com/pages/responsepage.aspx?id=Glu6x7ZB6UOhIG_2VK2hNxgNyBu3jyVItFyTXDeYtMVUM05XSkRJQThUQ1VaM1dLOEZUOVM4N1Q1RC4u. You must also contact the CDC to confirm that the company is approved.

**Citations:** cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot failed to mention the requirement to obtain departmental approval, which is a critical step in the expected resolved policy for self-secured internships.

**Source review (Codex):** confirmed_gap — The self-secured placement answer gave the CDC form and check but omitted required departmental approval before starting.

**Retrieved passages:**

- email-clarifications.md > Approved Internship Email Clarifications > Internship contact routing > Chemical Engineering internship contact (CHEM) (score 0.64)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently (score 0.71)
- email-clarifications.md > Problems or changes during an internship (score 0.71)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently (score 0.69)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.68)
- email-clarifications.md > Internship contact routing (score 0.68)
- cdc-knowledge-base.md > Internship (Approved Experience Course) (score 0.71)

## faculty-020-ece (ECE)

**Question:** My company is not listed with the CDC. Can I still intern there?

**Resolved reference:** Potentially, but prior approval is required by submitting a petition. The supporting company letter should describe the company and industry, the type of training provided, and the internship duration.

**Annotated document hit:** True

**Bot answer:**

Yes, you can intern at a company that is not listed with the CDC, but you must first contact the CDC to confirm approval or be guided to petition your department directly.

**Citations:** cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, grounded; reason: The chatbot failed to mention the mandatory requirement to submit a petition and provide a specific company letter, instead directing the student to contact the CDC for guidance.

**Source review (Codex):** confirmed_gap — The answer omitted the petition and the supporting official company-letter details for an unlisted company.

**Retrieved passages:**

- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Securing an Internship Independently > If the Company Is Already Listed with the CDC (score 0.82)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Securing an Internship Independently > If the Company Is NOT Listed with the CDC (score 0.79)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently (score 0.77)
- summer-training-guidelines-2026.md > Career Development Center (CDC) Internship Search and Postings (score 0.76)
- email-clarifications.md > Problems or changes during an internship (score 0.77)
- summer-training-guidelines-2026.md > Career Development Center (CDC) Internship Search and Postings (score 0.74)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Combining two company internships (score 0.62)

## faculty-025-ece (ECE)

**Question:** My friend received approval for the same arrangement last year. Does that mean mine is approved?

**Resolved reference:** No. Previous individual or exceptional approvals do not automatically apply to another student or another semester. Follow the current policy and obtain approval when required.

**Annotated document hit:** False

**Bot answer:**

No, a friend's individual exception or approval in an earlier term does not establish current policy or automatically approve another student. The current department and course requirements govern the arrangement, and you must obtain any required approval before relying on it.

**Citations:** email-clarifications.md > Current policy and individual exceptions

**Refused:** False

**Judge:** pass; failed fields: none; reason: The chatbot accurately conveys that previous individual exceptions do not establish precedent and that current approval is required.

**Source review (Codex):** acceptable — The answer correctly rejects automatic precedent and cites the reviewed current-policy FAQ. The annotated document list missed an equivalent newer approved source.

**Retrieved passages:**

- email-clarifications.md > Current policy and individual exceptions (score 0.76)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Combining two company internships (score 0.67)
- email-clarifications.md > Approval before beginning an internship (score 0.67)
- email-clarifications.md > Moodle access and registration (score 0.69)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.67)
- email-clarifications.md > Problems or changes during an internship (score 0.68)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.63)

## faculty-026-mech (MECH)

**Question:** What documents are needed if the company is already listed with the CDC?

**Resolved reference:** Submit the required approval request or petition and an official signed company letter on letterhead stating the internship duration and describing the expected training and work. Follow the current CDC and Moodle procedure before starting.

**Annotated document hit:** True

**Bot answer:**

You need to submit an online petition and upload an official company letter featuring the company letterhead, a signature, the internship duration, and a description of the training and expected work.

**Citations:** summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Securing an Internship Independently > If the Company Is Already Listed with the CDC

**Refused:** False

**Judge:** fail; failed fields: refusal_appropriate; reason: The chatbot accurately identified the required documents and the petition process while correctly referencing the need to follow the CDC and Moodle procedures.

**Source review (Codex):** acceptable — The answer lists every document the student requested. The judge's reason says it is correct but its refusal flag is false; an extra procedural reminder is not needed to identify the documents.

**Retrieved passages:**

- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Securing an Internship Independently > If the Company Is Already Listed with the CDC (score 0.79)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Securing an Internship Independently > If the Company Is NOT Listed with the CDC (score 0.75)
- email-clarifications.md > Problems or changes during an internship (score 0.70)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently (score 0.71)
- email-clarifications.md > Combining two company internships (MECH) (score 0.57)
- summer-training-guidelines-2026.md > Career Development Center (CDC) Internship Search and Postings (score 0.69)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs (score 0.70)

## faculty-028-iem (IEM)

**Question:** How do I request an exception to an internship rule?

**Resolved reference:** Submit a formal petition before relying on the exception. Include a clear justification and complete supporting documents, then obtain the required departmental and course approvals and follow the CDC procedure.

**Annotated document hit:** True

**Bot answer:**

To request an exception, you must submit it through the AUB online petition system at https://petitions.aub.edu.lb. Authorized department and course personnel make the decisions on exceptions, as the student assistant cannot grant them.

**Citations:** email-clarifications.md > Internship approval authority

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, grounded, refusal_appropriate, retrieval_sufficient; reason: The retrieved sources do not contain the required procedure for submitting a formal petition, such as the necessity of including a clear justification and supporting documents.

**Source review (Codex):** confirmed_gap — The petition location and approval authority are given, but the answer omits the justification and supporting documents needed to request an exception.

**Retrieved passages:**

- email-clarifications.md > Approved Internship Email Clarifications > Internship contact routing > Industrial Engineering and Management internship contact (IEM) (score 0.64)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Requesting a support letter (score 0.71)
- email-clarifications.md > Problems or changes during an internship (score 0.73)
- email-clarifications.md > Current policy and individual exceptions (score 0.71)
- email-clarifications.md > Internship approval authority (score 0.72)
- cdc-knowledge-base.md > Forms & Requests — Where to Find Them (score 0.72)
- summer-training-guidelines-2026.md > Professional Expectations During the Internship (score 0.74)

## faculty-030-ece (ECE)

**Question:** Remote internships were accepted in a previous summer. Does that mean mine is accepted?

**Resolved reference:** No. Temporary or exceptional approvals from previous semesters do not establish a permanent  rule. Your internship must follow the policy applicable to the current term.

**Annotated document hit:** True

**Bot answer:**

No, remote internships are not accepted unless your department allows a narrow exception and you obtain approval through a formal petition.

**Citations:** summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Internship Requirements: Duration, Hours, and Locations > Internships That Are Not Accepted

**Refused:** False

**Judge:** fail; failed fields: policy_correct, refusal_appropriate; reason: The chatbot failed to address the student's specific question about whether past acceptance of remote internships establishes a precedent, instead providing a generic policy statement.

**Source review (Codex):** acceptable — The answer starts No and applies the current remote-internship approval rule; it does not rely on prior summer precedent.

**Retrieved passages:**

- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Internship Requirements: Duration, Hours, and Locations > Internships That Are Not Accepted (score 0.79)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Combining two company internships (score 0.72)
- email-clarifications.md > Taking another summer course (score 0.74)
- email-clarifications.md > Approved Internship Email Clarifications > Deadline extensions and petition delays > Summer-graduate deadlines (score 0.74)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Internship Requirements: Duration, Hours, and Locations > Internships That Are Not Accepted (score 0.73)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Internship Requirements: Duration, Hours, and Locations > Internships That Are Not Accepted (score 0.73)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Securing an Internship Independently > If the Company Is Already Listed with the CDC (score 0.74)

## faculty-037-ece (ECE)

**Question:** Why can’t I access the Moodle quiz?

**Resolved reference:** The quiz may be restricted until the required lectures or videos are completed. Finish the assigned resources and check again. If access remains blocked, send the course coordinator a screenshot before the deadline.

**Annotated document hit:** True

**Bot answer:**

The quiz may remain restricted until all assigned lectures and recorded videos are completed or attempted. Complete the required resources and check again.

**Citations:** email-clarifications.md > Moodle quiz access and attempts

**Refused:** False

**Judge:** fail; failed fields: conditions_complete; reason: The chatbot failed to include the instruction to contact the course coordinator with a screenshot if access remains blocked, which is a required step in the expected resolved policy.

**Source review (Codex):** partial — The answer explains the likely Moodle prerequisite and immediate step, but omits the coordinator/screenshot fallback if access remains blocked.

**Retrieved passages:**

- email-clarifications.md > Moodle quiz access and attempts (score 0.83)
- email-clarifications.md > Moodle access and registration (score 0.76)
- email-clarifications.md > Moodle quiz access and attempts (score 0.81)
- email-clarifications.md > Moodle quiz passing score (score 0.73)
- email-clarifications.md > Approved Internship Email Clarifications > Moodle submissions and corrections > Moodle completion status (score 0.68)
- email-clarifications.md > Moodle submissions and corrections (score 0.70)
- email-clarifications.md > Course completion requirements (ECE) (score 0.57)

## faculty-045-ece (ECE)

**Question:** Can I submit the Final Report instead of the Progress Report?

**Resolved reference:** No. The Progress Report and Final Training Report are separate required deliverables and serve different purposes.

**Annotated document hit:** False

**Bot answer:**

No, each required report serves a distinct purpose and the Progress Report must still be submitted. Submit the Progress Report at the end of Week 4 of the company internship and cover only the company internship in it.

**Citations:** email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Progress reporting for a 6+2 arrangement

**Refused:** False

**Judge:** fail; failed fields: grounded, retrieval_sufficient; reason: The retrieved excerpts do not contain the specific policy stating that the Progress Report and Final Report are separate required deliverables, making the chatbot's claim ungrounded in the provided source material.

**Source review (Codex):** partial — The answer is substantively correct that the Progress and Final Reports are separate, but cites a 6+2-specific passage rather than the general deliverables rule; annotated document retrieval missed.

**Retrieved passages:**

- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Progress reporting for a 6+2 arrangement (score 0.71)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.72)
- email-clarifications.md > AI use, similarity, and report revision (score 0.74)
- email-clarifications.md > Revision of unsatisfactory internship reports (score 0.74)
- email-clarifications.md > Progress Report length and component (score 0.71)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.72)
- email-clarifications.md > Moodle submissions and corrections (score 0.77)

## faculty-046-mech (MECH)

**Question:** My Progress Report is much longer than required. Will it be accepted?

**Resolved reference:** A report that does not follow the required length or template may be returned for revision. Keep the report concise, cover the required sections, and follow the current Moodle template and word/page guidance.

**Annotated document hit:** True

**Bot answer:**

Write approximately 1,000 words or 3 to 5 pages for your Progress Report, keeping it concise and focused on relevant progress following the current Moodle template.

**Citations:** email-clarifications.md > Progress Report length and component

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot failed to answer the student's specific question about whether an overly long report would be accepted, instead providing general length guidelines.

**Source review (Codex):** confirmed_gap — The answer gives target length but never answers whether an overlong Progress Report can be accepted or returned for revision.

**Retrieved passages:**

- email-clarifications.md > Progress Report length and component (score 0.75)
- email-clarifications.md > AI use, similarity, and report revision (score 0.72)
- email-clarifications.md > Revision of unsatisfactory internship reports (score 0.73)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Progress Report Checklist (score 0.72)
- email-clarifications.md > Moodle submissions and corrections (score 0.71)
- email-clarifications.md > Company placements, AUB research, and approved gaps (score 0.73)
- email-clarifications.md > Company internship plus research (MECH) (score 0.61)

## faculty-050-ece (ECE)

**Question:** My Progress Report was evaluated as unsatisfactory. Can I resubmit it?

**Resolved reference:** A revision may be allowed or required, but resubmission is not automatic. Follow the feedback and the deadline provided by the course team, and resubmit only when the Moodle submission is reopened or you are instructed to do so.

**Annotated document hit:** True

**Bot answer:**

Yes, you may be allowed or asked to revise an unsatisfactory Progress Report. A first unsatisfactory Progress Report does not mean an automatic course fail if an allowed revision passes, though all other course requirements must still be completed.

**Citations:** email-clarifications.md > Revision of unsatisfactory internship reports; email-clarifications.md > AI use, similarity, and report revision

**Refused:** False

**Judge:** fail; failed fields: conditions_complete; reason: The chatbot failed to mention the necessary procedural conditions for resubmission, specifically that the student must wait for the Moodle submission to be reopened or receive specific instructions from the course team.

**Source review (Codex):** partial — Revision may be allowed is correct, but the answer omits following course-team feedback and resubmission instructions.

**Retrieved passages:**

- email-clarifications.md > Revision of unsatisfactory internship reports (score 0.78)
- email-clarifications.md > Progress Report length and component (score 0.69)
- email-clarifications.md > AI use, similarity, and report revision (score 0.73)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Progress reporting for a 6+2 arrangement (score 0.66)
- email-clarifications.md > Moodle submissions and corrections (score 0.71)
- summer-training-guidelines-2026.md > Approved Experience Evaluation and Pass/Fail Grading (score 0.66)
- email-clarifications.md > Moodle submissions and corrections (score 0.73)

## faculty-052-chem (CHEM)

**Question:** Is the Final Training Report required?

**Resolved reference:** Yes. The Final Training Report is a required CHEN 500 deliverable and must cover the approved experience activities.

**Annotated document hit:** True

**Bot answer:**

Yes, the Final Training Report is required. You must submit it within 1 week after completing the internship, following the report template and formatting guidelines provided on Moodle.

**Citations:** summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Training Report

**Refused:** False

**Judge:** fail; failed fields: refusal_appropriate; reason: The chatbot correctly identifies that the report is required and provides relevant submission details supported by the cited source.

**Source review (Codex):** acceptable — The Final Report requirement is answered directly with a supporting citation; the judge's reason agrees but its refusal flag is false.

**Retrieved passages:**

- email-clarifications.md > Required Final Report sections (score 0.73)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Training Report (score 0.79)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Final Approved Experience Report Rubric (score 0.73)
- email-clarifications.md > Shared Final Report formatting and content (score 0.71)
- internship-report-templates-and-rubrics.md > 2. Final Training Report Template (8–15 pages) (score 0.80)
- email-clarifications.md > Shared Final Report formatting and content (score 0.72)
- email-clarifications.md > Six-week internship completion (CHEM) (score 0.66)

## faculty-053-iem (IEM)

**Question:** When should I submit my Final Training Report?

**Resolved reference:** Normally submit the Final Training Report within one week of completing the approved internship, unless the current departmental Moodle page announces a different official deadline.

**Annotated document hit:** True

**Bot answer:**

Submit your Final Training Report within 1 week after completing the internship.

**Citations:** summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Training Report

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete; reason: The chatbot failed to include the essential caveat that the departmental Moodle page may announce a different official deadline, which is part of the expected resolved policy.

**Source review (Codex):** partial — The one-week normal deadline is correct, but the answer does not mention that an official current Moodle deadline can supersede it.

**Retrieved passages:**

- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Training Report (score 0.83)
- internship-report-templates-and-rubrics.md > 2. Final Training Report Template (8–15 pages) (score 0.79)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.72)
- summer-training-guidelines-2026.md > Internship Timeline and Deliverables (score 0.72)
- email-clarifications.md > Current dates and daily internship records (score 0.70)
- internship-report-templates-and-rubrics.md > 2. Final Training Report Template (8–15 pages) (score 0.80)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Industrial Engineering and Management (IEM) (score 0.65)

## faculty-055-ece (ECE)

**Question:** What font and spacing should I use in the Final Report?

**Resolved reference:** Use size 12 font and double spacing with appropriate margins. All pages should be numbered.

**Annotated document hit:** True

**Bot answer:**

Use double spacing and size 12 font.

**Citations:** email-clarifications.md > Shared Final Report formatting and content

**Refused:** False

**Judge:** fail; failed fields: conditions_complete; reason: The chatbot failed to include the requirement for page numbering, which is a specified formatting instruction in the source material.

**Source review (Codex):** acceptable — The student asked for font and spacing, both of which were answered correctly. The judge required unrelated page numbering.

**Retrieved passages:**

- email-clarifications.md > Shared Final Report formatting and content (score 0.81)
- email-clarifications.md > Final Report requirements (ECE) (score 0.68)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Final Approved Experience Report Rubric (score 0.71)
- email-clarifications.md > Final presentation content and visual communication (score 0.73)
- email-clarifications.md > Shared Final Report formatting and content (score 0.69)
- email-clarifications.md > Progress Report length and component (score 0.70)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Career Readiness Resources > CV and Cover Letter Guidelines (score 0.77)

## faculty-056-mech (MECH)

**Question:** What should be included on the Final Report cover page?

**Resolved reference:** Include the course name and number, your name, major, internship term, company name and location, report submission date, and internship start and end dates.

**Annotated document hit:** True

**Bot answer:**

Include your course number and title, student name, ID number, department, organization name, approved experience location, approved experience dates, and submission date.

**Citations:** internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Cover Page

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot provided requirements from the wrong template (Progress Report) instead of the expected policy for the Final Report, omitting the required major and internship term.

**Source review (Codex):** acceptable — The answer mirrors the official Final Report cover-page template; the frozen expectation and judge demand major/term fields not present in that cited template.

**Retrieved passages:**

- email-clarifications.md > Shared Final Report formatting and content (score 0.78)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 1. Progress Report Template (3–5 pages) > Cover Page (score 0.75)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Cover Page (score 0.78)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.73)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Final Approved Experience Report Rubric (score 0.71)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Table of Contents (score 0.76)
- email-clarifications.md > Company internship plus research (MECH) (score 0.58)

## faculty-057-chem (CHEM)

**Question:** Do I need a Table of Contents?

**Resolved reference:** Yes. Include a Table of Contents with report sections and page numbers and, where applicable, lists of tables, figures, and pictures.

**Annotated document hit:** True

**Bot answer:**

Include page numbers and, where applicable, lists of tables, figures, and pictures.

**Citations:** internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Table of Contents

**Refused:** False

**Judge:** fail; failed fields: policy_correct, refusal_appropriate; reason: The chatbot failed to answer the student's direct question about whether a Table of Contents is required, omitting the 'Yes' confirmation.

**Source review (Codex):** confirmed_gap — The answer gives page-number details but never explicitly says a Table of Contents is required.

**Retrieved passages:**

- email-clarifications.md > Shared Final Report formatting and content (score 0.70)
- email-clarifications.md > Shared Final Report formatting and content (score 0.66)
- email-clarifications.md > Shared Final Report formatting and content (score 0.68)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Table of Contents (score 0.67)
- email-clarifications.md > Required Final Report sections (score 0.67)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Final Approved Experience Report Rubric (score 0.63)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Chemical Engineering (CHEM) (score 0.56)

## faculty-062-chem (CHEM)

**Question:** What should I write about acquiring and applying new knowledge?

**Resolved reference:** Explain what new knowledge or skills you needed, how you learned them, which learning strategies or resources you used, and how you applied the new knowledge to your internship work.

**Annotated document hit:** True

**Bot answer:**

Discuss how new knowledge was acquired and applied, alongside technical and administrative activities, engineering or computing projects, specific applications of engineering, science, and mathematics, and informed judgment about relevant global, economic, environmental, and societal impacts. Keep the required Moodle report structure for these discussions.

**Citations:** email-clarifications.md > Shared Final Report formatting and content

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot failed to provide the specific guidance requested regarding what to write about acquiring and applying new knowledge, instead providing a generic list of report topics.

**Source review (Codex):** confirmed_gap — The answer repeats generic report topics instead of explaining how to describe acquiring, learning, and applying new knowledge.

**Retrieved passages:**

- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > Final Approved Experience Report Rubric (score 0.64)
- email-clarifications.md > Shared Final Report formatting and content (score 0.63)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > 4. Application of Engineering, Design, and Disciplinary Knowledge (score 0.66)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 3. Final Presentation > Final Presentation Rubric (score 0.63)
- email-clarifications.md > AI use, similarity, and report revision (score 0.64)
- email-clarifications.md > Problems or changes during an internship (score 0.62)
- email-clarifications.md > Combining or splitting two company internships (CHEM) (score 0.55)

## faculty-070-ece (ECE)

**Question:** Do I need to submit a Final Voice-Over Presentation?

**Resolved reference:** Yes. For EECE 500, follow the current Moodle instructions for the Final Voice-Over Presentation as part of the final course deliverables.

**Annotated document hit:** True

**Bot answer:**

Whether you need to submit a Final Voice-over Presentation depends on your department's specific requirements, as a voice-over PowerPoint may be required by some departments.

**Citations:** summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Presentation Guidelines

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot failed to provide the specific ECE requirement, instead giving a vague, non-committal answer despite the retrieved documents confirming that ECE students must submit a Voice-over Presentation.

**Source review (Codex):** confirmed_gap — ECE specifically requires the Final Voice-over Presentation; the answer gives an unnecessary department-dependent hedge.

**Retrieved passages:**

- email-clarifications.md > Final Voice-over Presentation duration (ECE) (score 0.83)
- email-clarifications.md > Final Voice-over Presentation duration (ECE) (score 0.75)
- email-clarifications.md > Final presentation content and visual communication (score 0.80)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Presentation Guidelines (score 0.77)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 3. Final Presentation > Final Presentation Rubric (score 0.70)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Presentation Guidelines (score 0.82)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Electrical and Computer Engineering (ECE) (score 0.61)

## faculty-075-ece (ECE)

**Question:** Should I use pictures, graphs, or charts?

**Resolved reference:** Yes. Appropriate pictures, diagrams, graphs, charts, and other relevant visuals are encouraged to improve understanding and engagement.

**Annotated document hit:** True

**Bot answer:**

Use relevant pictures, diagrams, graphs, or charts in your presentation when they help explain the work. Respect employer confidentiality and cite any external visuals or information you use.

**Citations:** email-clarifications.md > Final presentation content and visual communication

**Refused:** False

**Judge:** fail; failed fields: refusal_appropriate; reason: The chatbot correctly answers the question by encouraging the use of visuals while including necessary professional caveats found in the source material.

**Source review (Codex):** acceptable — Relevant visuals are clearly recommended with sensible confidentiality and citation conditions; the judge's reason agrees but its refusal flag is false.

**Retrieved passages:**

- email-clarifications.md > Final presentation content and visual communication (score 0.84)
- email-clarifications.md > Shared Final Report formatting and content (score 0.68)
- email-clarifications.md > Research two-week form (ECE) (score 0.60)
- email-clarifications.md > Shared Final Report formatting and content (score 0.62)
- email-clarifications.md > AI use, similarity, and report revision (score 0.62)
- internship-report-templates-and-rubrics.md > Internship (Approved Experience) Report Templates and Rubrics > 2. Final Training Report Template (8–15 pages) > References (score 0.67)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Career Readiness Resources > CV and Cover Letter Guidelines (score 0.60)

## faculty-080-ece (ECE)

**Question:** When is the Final VOP due?

**Resolved reference:** Submit the Final Voice-Over Presentation within one week after completing the approved internship unless the current Moodle page announces an earlier official deadline, such as a graduation-related deadline.

**Annotated document hit:** True

**Bot answer:**

For ECE students, both the final training report and final presentation are due within one week after the completion of your internship, based on your specific internship end date.

**Citations:** summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Electrical and Computer Engineering (ECE)

**Refused:** False

**Judge:** fail; failed fields: conditions_complete; reason: The chatbot failed to include the critical caveat that the Moodle page may announce an earlier official deadline, which is a required component of the expected resolved policy.

**Source review (Codex):** partial — The usual one-week Final VOP timing is correct, but an earlier official Moodle deadline is possible and omitted.

**Retrieved passages:**

- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Electrical and Computer Engineering (ECE) (score 0.61)
- email-clarifications.md > Final presentation content and visual communication (score 0.73)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Presentation Guidelines (score 0.73)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Presentation Guidelines (score 0.66)
- email-clarifications.md > Final Voice-over Presentation duration (ECE) (score 0.65)
- email-clarifications.md > Approved Internship Email Clarifications > Internship dates and duration changes > Submission timing after an internship extension (score 0.61)
- email-clarifications.md > Final Report requirements (ECE) (score 0.58)

## faculty-081-ece (ECE)

**Question:** Can I submit the PowerPoint without audio?

**Resolved reference:** No. A Voice-Over Presentation requires recorded narration. A presentation without audio does not satisfy the requirement unless an alternative accommodation has been formally approved.

**Annotated document hit:** True

**Bot answer:**

No. The Voice-over Presentation requires narration recorded on the PowerPoint slides unless current Moodle instructions explicitly specify a different format.

**Citations:** email-clarifications.md > Final Voice-over Presentation duration (ECE)

**Refused:** False

**Judge:** fail; failed fields: refusal_appropriate; reason: The chatbot correctly identifies that narration is required and includes the relevant exception clause found in the retrieved source.

**Source review (Codex):** acceptable — Recorded narration is required and the answer states that clearly; the judge's reason agrees but its refusal flag is false.

**Retrieved passages:**

- email-clarifications.md > Final Voice-over Presentation duration (ECE) (score 0.82)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Presentation Guidelines (score 0.71)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Final Presentation Guidelines (score 0.63)
- email-clarifications.md > Employer and research documentation exceptions (score 0.58)
- email-clarifications.md > Moodle submissions and corrections (score 0.61)
- summer-training-guidelines-2026.md > Internship Timeline and Deliverables (score 0.56)
- email-clarifications.md > Final Voice-over Presentation duration (ECE) (score 0.64)

## faculty-087-chem (CHEM)

**Question:** Can the employer simply state that I worked there?

**Resolved reference:** No. The completion letter should include the required internship dates, projects/tasks completed, a brief evaluation of your work, and a signature.

**Annotated document hit:** True

**Bot answer:**

I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Adnan Itani (ai34@aub.edu.lb), the Chemical Engineering coordinator.

**Citations:** none

**Refused:** True

**Judge:** fail; failed fields: policy_correct, conditions_complete, grounded, relevant, refusal_appropriate; reason: The chatbot incorrectly refused to answer a question that was directly addressed by the provided source material regarding the required contents of an employer completion letter.

**Source review (Codex):** confirmed_gap — The bot refused despite an approved FAQ listing the required employer-letter content.

**Retrieved passages:**

- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for employers > Employer application process (score 0.65)
- email-clarifications.md > Student internship survey and employer-letter format (score 0.62)
- msfea-cdc-coop-handbook.md > Additional employer completion letter (score 0.64)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for employers > Employer application process (score 0.62)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for employers > Employer responsibilities during the co-op (score 0.60)
- email-clarifications.md > Approved Internship Email Clarifications > Employer and research documentation exceptions > Early or temporarily delayed employer letter (score 0.59)
- email-clarifications.md > Combining or splitting two company internships (CHEM) (score 0.52)

## faculty-106-mech (MECH)

**Question:** Are deadlines important even though the course is Pass/Fail?

**Resolved reference:** Yes. Timely completion of the required deliverables is part of the course requirements.

**Annotated document hit:** True

**Bot answer:**

Yes, deadlines are important. Summer-graduating students may receive earlier deadlines because their grades must be processed sooner, and you should follow the current graduating-student Moodle announcement or course-coordinator email.

**Citations:** email-clarifications.md > Approved Internship Email Clarifications > Deadline extensions and petition delays > Summer-graduate deadlines

**Refused:** False

**Judge:** fail; failed fields: policy_correct, grounded, retrieval_sufficient; reason: The retrieved excerpts do not contain the policy stating that deadlines are mandatory for Pass/Fail courses, and the chatbot failed to provide the expected answer.

**Source review (Codex):** confirmed_gap — Although it starts Yes, the answer shifts to summer-graduate deadlines and does not ground the ordinary Pass/Fail-course requirement in its citation.

**Retrieved passages:**

- email-clarifications.md > AI use, similarity, and report revision (score 0.73)
- email-clarifications.md > Taking another summer course (score 0.71)
- email-clarifications.md > Approved Internship Email Clarifications > Deadline extensions and petition delays > Summer-graduate deadlines (score 0.71)
- email-clarifications.md > Revision of unsatisfactory internship reports (score 0.69)
- email-clarifications.md > Moodle submissions and corrections (score 0.67)
- email-clarifications.md > Internship dates and duration changes (score 0.72)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Mechanical Engineering (MECH) (score 0.64)

## faculty-115-ece (ECE)

**Question:** How long must my internship be if I take another course at the same time?

**Resolved reference:** Ten internship weeks may be required when taking another summer course, but applicability depends on current course-team/Moodle requirements and approvals; do not state that all students unconditionally need ten weeks.

**Annotated document hit:** True

**Bot answer:**

When you take another summer course while completing your internship, a concurrent summer course requires department, course-team, and employer approval, and the required internship work hours must still be completed. You may have to complete at least ten weeks of approved training (ten weeks at one company or six weeks at one company plus four weeks at another) and schedule your other course before 8:30 AM or after 4:30 PM. Confirm whether these duration and class-time limits apply to your arrangement with the course team and current Moodle instructions before committing, as they are not an unconditional ten-week requirement for every student taking another course.

**Citations:** email-clarifications.md > Taking another summer course

**Refused:** False

**Judge:** not run; judge daily quota reached

**Source review (Codex):** manual_pass_unjudged — The final case received no model judgment after the first 429. Source review finds the ten-week condition, approvals, schedule constraints, and current-policy caveat correctly stated.

**Retrieved passages:**

- email-clarifications.md > Taking another summer course (score 0.84)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Combining two company internships (score 0.81)
- email-clarifications.md > Approved Internship Email Clarifications > Approved Experience course codes > EECE 500 internship duration (ECE) (score 0.71)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Six company weeks alone (score 0.74)
- email-clarifications.md > Approved Internship Email Clarifications > Internship dates and duration changes > Submission timing after an internship extension (score 0.75)
- email-clarifications.md > Approved Experience course billing (score 0.72)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs (score 0.72)

## faculty-117-chem (CHEM)

**Question:** When are my deliverables due?

**Resolved reference:** Deadlines are based on your internship timeline and the official dates posted on the current Moodle page or communicated to you. Check Moodle regularly.

**Annotated document hit:** True

**Bot answer:**

To successfully complete your internship course, you must submit the following deliverables according to this timeline:

- Proposal of Approved Experience Form: Complete this before beginning your internship, submitted through Moodle.
- Notice of Arrival Form: Submit this during the first week of training through Moodle.
- Professional Skills Requirement: Watch 3 recorded lectures on professional skills and engineering practice plus 3 internship experience videos, then complete the Moodle quiz with a minimum score of 75% during the internship.
- Progress Report: Submit a short report summarizing your internship experience and progress by the end of Week 4 (counted from your approved start date, unless Moodle announces a shared deadline), submitted through Moodle.
- Final Training Report: Submit this within 1 week after completing the internship following the template and guidelines posted on Moodle.
- Summary Sheet Form: Complete this online form at the end of the internship.
- Student Evaluation Form: Complete this required student internship survey separately from the Summary Sheet and employer letter at the end of the internship via the Online Form.
- Notice of Completion: Submit an official company letter confirming completion of your internship at the end of the internship via upload or department submission.
- Final Presentation: Deliver your internship presentation during the first 2 weeks of the Fall semester (depending on department requirements) via Department Submission.

**Citations:** summer-training-guidelines-2026.md > Internship Timeline and Deliverables

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot failed to provide the expected resolved policy, which emphasizes that deadlines are based on the internship timeline and official dates posted on Moodle, instead providing a rigid list of deadlines that ignores the possibility of Moodle-announced shared deadlines.

**Source review (Codex):** partial — The answer supplies many typical milestones and one shared-deadline caveat, but fails to lead with the current Moodle/approved-start-date rule and may overstate fixed dates.

**Retrieved passages:**

- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Deliverables and deadlines (score 0.71)
- summer-training-guidelines-2026.md > Internship Timeline and Deliverables (score 0.66)
- email-clarifications.md > Employer completion letter timing (score 0.66)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Deliverables and deadlines (score 0.65)
- email-clarifications.md > Progress Report deadline origin (score 0.61)
- email-clarifications.md > Proposal and Notice of Arrival timing (score 0.66)
- email-clarifications.md > Approved Internship Email Clarifications > Internship contact routing > Chemical Engineering internship contact (CHEM) (score 0.49)

## faculty-125-ece (ECE)

**Question:** My friend was allowed to do this last year. Can I?

**Resolved reference:** Ask what 'this' refers to. A friend's past individual approval does not establish a current policy or automatic exception; explain the applicable rule once the arrangement is identified.

**Annotated document hit:** False

**Bot answer:**

Ask which arrangement you mean before applying a rule, as a friend's individual exception or approval in an earlier term does not establish current policy or automatically approve another student. The current department and course requirements govern the identified arrangement; obtain any required approval before relying on an exception.

**Citations:** email-clarifications.md > Current policy and individual exceptions

**Refused:** False

**Judge:** pass; failed fields: none; reason: The chatbot correctly identifies the need to clarify the specific arrangement before applying policy and accurately reflects the provided source material regarding individual exceptions.

**Source review (Codex):** acceptable — The answer asks which arrangement is meant and rejects automatic precedent, with a supporting newer approved FAQ; the annotated document list missed it.

**Retrieved passages:**

- email-clarifications.md > Current policy and individual exceptions (score 0.74)
- msfea-cdc-coop-handbook.md > Policies (score 0.63)
- email-clarifications.md > Moodle quiz access and attempts (score 0.64)
- msfea-cdc-coop-handbook.md > CO-OP FAQs (score 0.62)
- msfea-cdc-coop-handbook.md > Policies (score 0.62)
- email-clarifications.md > Approved Internship Email Clarifications > Combined internship arrangements (ECE) > Combining two company internships (score 0.60)
- email-clarifications.md > Moodle access and registration (score 0.65)

## faculty-132-chem (CHEM)

**Question:** Who is responsible for finding the internship?

**Resolved reference:** Students are responsible for securing their own internship opportunities, with support from the department internship coordinator and the MSFEA Career Development Center.

**Annotated document hit:** True

**Bot answer:**

I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Adnan Itani (ai34@aub.edu.lb), the Chemical Engineering coordinator.

**Citations:** none

**Refused:** True

**Judge:** fail; failed fields: policy_correct, conditions_complete, grounded, refusal_appropriate, retrieval_sufficient; reason: The chatbot failed to retrieve the policy stating that students are responsible for securing their own internships and incorrectly refused to answer a straightforward policy question.

**Source review (Codex):** confirmed_gap — The bot refused an answerable question about who secures the internship.

**Retrieved passages:**

- email-clarifications.md > Approved Internship Email Clarifications > Internship contact routing > Chemical Engineering internship contact (CHEM) (score 0.71)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently (score 0.75)
- email-clarifications.md > Problems or changes during an internship (score 0.74)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.71)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently (score 0.72)
- summer-training-guidelines-2026.md > Career Development Center (CDC) Internship Search and Postings (score 0.69)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Applying to an internship found independently (score 0.71)

## faculty-134-cee (CEE)

**Question:** What type of work is acceptable for the internship course

**Resolved reference:** The work must provide meaningful professional experience related to your discipline and involve engineering, computing, design, analysis, or technical problem solving. Work that is mainly unrelated business, finance, or administrative activity may not meet the course objectives.

**Annotated document hit:** True

**Bot answer:**

To successfully complete the internship course, you must submit the following required forms, reports, and evaluations:

- Proposal of Approved Experience Form
- Notice of Arrival Form
- Professional Skills Requirement
- Progress Report
- Final Training Report
- Summary Sheet Form
- Student Evaluation Form (all departments)
- Notice of Completion
- Final Presentation

**Citations:** summer-training-guidelines-2026.md > Internship Timeline and Deliverables

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, grounded, relevant, refusal_appropriate, retrieval_sufficient; reason: The chatbot failed to answer the question about acceptable work types, instead providing a list of administrative deliverables that does not address the nature of the internship work.

**Source review (Codex):** confirmed_gap — The bot listed course deliverables instead of acceptable technical work types.

**Retrieved passages:**

- email-clarifications.md > Taking another summer course (score 0.73)
- summer-training-guidelines-2026.md > Internship Timeline and Deliverables (score 0.72)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Internship Requirements: Duration, Hours, and Locations > Internships That Are Not Accepted (score 0.71)
- cdc-knowledge-base.md > MSFEA CDC Student Knowledge Base > Internship (Approved Experience Course) > Internship FAQs (score 0.72)
- email-clarifications.md > Internship course grading (score 0.71)
- email-clarifications.md > Approved Internship Email Clarifications > Internship contact routing > Civil and Environmental Engineering internship contact (CEE) (score 0.64)
- cdc-knowledge-base.md > Internship (Approved Experience Course) (score 0.80)

## faculty-145-ece (ECE)

**Question:** When should a co-op student submit the Proposal for Approved Experience?

**Resolved reference:** Use the CO-OP handbook's proposal and admission process; no universal internship-course Moodle Proposal requirement was approved for CO-OP.

**Annotated document hit:** True

**Bot answer:**

I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

**Citations:** none

**Refused:** True

**Judge:** fail; failed fields: policy_correct, conditions_complete, grounded, relevant, refusal_appropriate; reason: The chatbot incorrectly claimed it could not find the answer and refused to provide the policy, despite the retrieved source explicitly stating that students must submit the 'Proposal of Cooperative Education and Experiential Learning Form' for self-found placements.

**Source review (Codex):** confirmed_gap — The bot refused rather than explaining the CO-OP handbook proposal/admission process and its distinction from the internship-course Moodle Proposal.

**Retrieved passages:**

- msfea-cdc-coop-handbook.md > CO-OP FAQs (score 0.81)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Application timeline (deadlines) (score 0.80)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Application and admission process (score 0.82)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Application and admission process (score 0.80)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for employers > Employer responsibilities during the co-op (score 0.77)
- msfea-cdc-coop-handbook.md > Policies (score 0.80)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Deliverables and deadlines (score 0.76)

## faculty-164-cee (CEE)

**Question:** Should I submit the Proposal before my internship is confirmed?

**Resolved reference:** No. Submit it after confirmation, using accurate organization, supervisor, dates, and work details.

**Annotated document hit:** True

**Bot answer:**

No, complete the Proposal of Approved Experience Form before beginning your internship, and submit it when the internship is confirmed.

**Citations:** email-clarifications.md > Forms for a second internship

**Refused:** False

**Judge:** fail; failed fields: grounded; reason: The chatbot provided the correct policy but cited a document regarding second internships rather than the relevant source that explicitly states the proposal should be submitted when the internship is confirmed.

**Source review (Codex):** partial — Submit after confirmation is correct, but the sole citation is scoped to a second internship while the question is general.

**Retrieved passages:**

- email-clarifications.md > Approved Internship Email Clarifications > Internship dates and duration changes > Submission timing after an internship extension (score 0.76)
- summer-training-guidelines-2026.md > Internship Timeline and Deliverables (score 0.73)
- email-clarifications.md > Forms for a second internship (score 0.74)
- email-clarifications.md > Internship dates and duration changes (score 0.78)
- email-clarifications.md > Proposal and Notice of Arrival timing (score 0.81)
- email-clarifications.md > Reporting after approval of multiple internship components (score 0.71)
- email-clarifications.md > Six-week internship approval (CEE) (score 0.68)

## faculty-165-ece (ECE)

**Question:** When should I submit the Notice of Arrival?

**Resolved reference:** Submit it after you actually start the internship and within the deadline stated on Moodle.

**Annotated document hit:** True

**Bot answer:**

Submit the Notice of Arrival during the first week of your training.

**Citations:** email-clarifications.md > Proposal and Notice of Arrival timing; summer-training-guidelines-2026.md > Internship Timeline and Deliverables

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete; reason: The chatbot failed to include the mandatory requirement to submit the form by the deadline stated on Moodle, providing only the timing relative to the start of training.

**Source review (Codex):** acceptable — During the first week necessarily means after starting and matches the approved timing FAQ; the judge demanded an unasked generic Moodle caveat.

**Retrieved passages:**

- email-clarifications.md > Proposal and Notice of Arrival timing (score 0.81)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Important Checklists > Notice of Completion / Employer Letter Checklist (score 0.71)
- email-clarifications.md > Forms for a second internship (score 0.65)
- email-clarifications.md > Internship dates and duration changes (score 0.68)
- summer-training-guidelines-2026.md > Internship Timeline and Deliverables (score 0.64)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Deliverables and deadlines (score 0.67)
- summer-training-guidelines-2026.md > Summer Training (Approved Experience) Guidelines > Department-Specific Rules > Electrical and Computer Engineering (ECE) (score 0.58)

## faculty-177-chem (CHEM)

**Question:** What documents must a co-op student submit after finishing?

**Resolved reference:** Follow the CO-OP handbook's final deliverables plus the additional signed company letter. Do not assert a universal CO-OP Final Voice-Over Presentation requirement.

**Annotated document hit:** True

**Bot answer:**

For CO-OP: You must submit the following documents at the end of the co-op:

- Co-op Final Report (a three-page memo describing the work completed, plus appendices with work samples)
- Student Self-Evaluation, Reflection, and Feedback Form
- Additional requirements set by your department, if any

**Citations:** msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Deliverables and deadlines

**Refused:** False

**Judge:** fail; failed fields: policy_correct, conditions_complete, refusal_appropriate; reason: The chatbot failed to include the required signed company letter (Final Student Performance Evaluation Form) mentioned in the expected resolved policy.

**Source review (Codex):** confirmed_gap — The CO-OP final-deliverables answer omitted the additional signed company letter.

**Retrieved passages:**

- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Deliverables and deadlines (score 0.80)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Requirements to pass the co-op course (summary) (score 0.82)
- msfea-cdc-coop-handbook.md > Policies (score 0.77)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for employers > Employer responsibilities during the co-op (score 0.77)
- msfea-cdc-coop-handbook.md > CO-OP FAQs (score 0.74)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Student evaluation (score 0.78)
- msfea-cdc-coop-handbook.md > MSFEA CO-OP (Cooperative Education) Handbook > Information for students > Deliverables and deadlines (score 0.83)
