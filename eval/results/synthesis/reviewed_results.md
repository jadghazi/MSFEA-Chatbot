# Synthesis experiments — reviewed measurements

Review method: Coding assistant manual review against saved source chunks and frozen expected qualities; not an independent human or calibrated judge.

The synthesis mean excludes the one intentional refusal. Grounding errors
are reviewed separately; valid source labels alone do not establish support.
Latency is the median sum of provider latencies per answered turn; the two-call
candidate also adds a deliberate seven-second inter-call quota delay.

| Candidate | Synthesis /5 (11 answerable) | Unsupported answers | False refusals | All-premise recall | Calls | Input tokens | Provider ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 3.09 | 2 | 1/11 | 10/11 | 11 | 25,572 | 1175 |
| task_prompt | 3.00 | 0 | 2/11 | 10/11 | 11 | 16,057 | 1158 |
| k3 | 3.18 | 0 | 2/11 | 6/11 | 11 | 20,369 | 1126 |
| k12 | 3.00 | 1 | 1/11 | 11/11 | 11 | 34,449 | 1137 |
| two_step | 3.00 | 1 | 1/11 | 10/11 | 22 | 53,256 | 2783 |
| temperature | 3.09 | 2 | 1/11 | 10/11 | 11 | 25,572 | 17128 |
| max_gate | 3.27 | 2 | 0/11 | 10/11 | 12 | 27,732 | 1186 |
| model_current | 2.73 | 0 | 2/11 | 10/11 | 11 | 25,572 | 6980 |
| native_system | 2.91 | 3 | 1/11 | 10/11 | 11 | 25,594 | 1153 |
| confirmation_frame | 3.00 | 1 | 2/11 | 10/11 | 11 | 25,576 | 1102 |
| confirmation_frame_v2 | 3.55 | 1 | 1/11 | 10/11 | 11 | 25,587 | 1079 |
| structured | 2.45 | 1 | 2/11 | 10/11 | 11 | 26,100 | 1296 |
| resolve_turn | 3.64 | 1 | 1/11 | 10/11 | 22 | 27,469 | 2092 |
| task_contract | 3.82 | 0 | 2/11 | 10/11 | 11 | 25,953 | 1194 |
| combined | 4.00 | 1 | 0/11 | 11/11 | 12 | 37,496 | 1212 |
| combined_adaptive | 4.45 | 0 | 0/11 | 11/11 | 12 | 28,979 | 1862 |
| combined_adaptive_repeat | 4.45 | 0 | 0/11 | 11/11 | 12 | 28,979 | 1410 |

## Per-case scores and actual outputs

### baseline

[Raw prompts, retrieved chunks and responses](baseline.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. False pre-LLM refusal despite retrieved definition; no invented facts.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Defines correctly but adds progress-report timing and separate research report unasked.

> For ECE students: The 6+2 arrangement combines six weeks of company internship with two weeks of research with an MSFEA faculty member, and both components must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship, covering only the company part, and you must also submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: supported. Does not confirm interpretation; answers how to document research instead.

> For ECE students: For a six-week internship plus two-week research arrangement, submit a separate research report for the research component. Use the research two-week form provided on Moodle, which must include the faculty supervisor, research dates, and technical nature of the work. Written confirmation from the faculty supervisor may also be required.

Sources: email-clarifications.md > Reports for multiple approved components (ECE); email-clarifications.md > Forms for additional internship components

**s04-correct — so two more weeks at the company instead?**

Score: 1/5. Grounding: unsupported. Yes endorses two more weeks at the same company, while cited alternative is four weeks at another company. Rule itself is quoted accurately but its application is misleading.

> For ECE students: Yes, students completing a six-week internship can meet the remaining requirement by completing a minimum four-week internship at another company instead of doing two weeks of faculty research.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Correct No and remaining research component; volunteers a research-report requirement.

> For ECE students: No, you have not completed the entire arrangement until you finish both the six company weeks and the two-week research component, and you must submit a separate research report for that research component.

Sources: email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: unsupported. Duration/pay contrast mostly direct, but waiver passage is absent; unconditional no need for both omits passing FEAA 500. Optional status also omitted.

> For CO-OP: A co-op work term is a minimum of 6 months, full-time, and paid. In comparison, internships are typically short, lasting one or two months (with a minimum duration of 8 weeks for the approved experience), and can be unpaid. Additional co-ops are allowed if approved by the department and co-op advisor, but you do not need to do both a co-op and an internship.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correctly applies independent limits; omits disclosure/citation caveat and one-point difference.

> The AI-generated text percentage of 23% is within the maximum limit of 25%, but the Turnitin similarity percentage of 21% exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Gives fairness rationale but ignores the wait-time tension; repeats avoid-rejecting advice.

> You may only apply to one CDC internship offer at a time to give everyone a fair chance at CDC offers. You should also avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Direct No, explains separate administrative checks and routes registration correctly.

> No, Moodle access and AUBSIS registration are separate administrative checks, so you cannot skip checking AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Answers IAESTE only with club and contact despite earlier internship history.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct refusal; no invented rationale for exactly two research weeks.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 4/5. Grounding: supported. Correctly says six plus two is insufficient and applies ten-week rule; opening does not replace is less clear than changes the requirement.

> For ECE students: Taking another summer course does not replace the requirement for ten weeks of approved internship (either ten weeks at one company or six weeks at one company plus four weeks at another), so six company weeks plus two research weeks is not enough.

Sources: email-clarifications.md > Taking another summer course (ECE)

### task_prompt

[Raw prompts, retrieved chunks and responses](task_prompt.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Same false gate refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Still appends report instructions to definition.

> For ECE students, the 6+2 arrangement is a combined internship option where you complete a six-week company internship along with a two-week research component with an MSFEA faculty member. Both components must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship (covering only the company internship) and submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: supported. Still answers documentation instead of confirming research.

> For ECE students, the two-week research component of a 6+2 arrangement requires submitting a separate research report, and you must use the research two-week form provided on Moodle, which includes the faculty supervisor, research dates, and technical nature of the work. Written confirmation from the faculty supervisor may also be required.

Sources: email-clarifications.md > Combined internship arrangements (ECE); email-clarifications.md > Forms for additional internship components; summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 4/5. Grounding: supported. Correct No for substituting company weeks, but adds another-company alternative.

> For ECE students: No, you cannot simply add two more weeks at the same company as an alternative. For a six-week internship, the alternative arrangements are either completing two weeks of research with an MSFEA faculty member or completing a minimum four-week internship at another company.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 3/5. Grounding: supported. States premises before conclusion and adds report requirement.

> For ECE students doing a six-week internship plus two-week research arrangement, the six company weeks and two faculty-research weeks must both be approved and documented. You have not completed the entire approved 6+2 arrangement until you also complete the two-week research component and submit its separate research report.

Sources: email-clarifications.md > Combined internship arrangements (ECE); email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: incomplete. Correct comparison of duration/pay and acknowledges missing waiver evidence; cannot finish requested comparison.

> An internship has a minimum duration of 8 weeks and can be unpaid, whereas an MSFEA co-op work term lasts a minimum of 6 months, is full-time, and is paid. Regarding whether you need to do both, the provided evidence does not contain this information.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; cdc-knowledge-base.md > Internship FAQs

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Direct No and correct separate limits; omits disclosure and one-point difference.

> No, the Turnitin similarity percentage exceeds the permitted limit. While the AI-generated text is within the 25% maximum limit at 23%, the Turnitin similarity percentage of 21% exceeds the maximum allowable threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 1/5. Grounding: supported. False refusal although fairness rationale is retrieved.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact fcareer@aub.edu.lb.

Sources: none (refusal)

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Direct conclusion from separate administrative checks.

> No, being on Moodle does not prove you are registered on AUBSIS. Moodle access and AUBSIS registration are separate administrative checks, and AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Successful IAESTE topic switch with contact.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities by contacting iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct refusal on undocumented rationale.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 3/5. Grounding: supported. Restates ten-week rule without explicitly answering whether six plus two is enough.

> For ECE students, taking another summer course while completing EECE500 requires ten weeks of approved internship (either ten weeks at one company or six weeks at one company plus four weeks at another company), along with the required EECE500 and departmental approval.

Sources: email-clarifications.md > Taking another summer course (ECE)

### k3

[Raw prompts, retrieved chunks and responses](k3.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Same false gate refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 2/5. Grounding: incomplete. Restates source approval/report instructions; faculty identity is missing from reduced context.

> For ECE students: The six company weeks and two faculty-research weeks must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship and cover only the company internship in that report.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: supported. Still answers forms/reports instead of confirming.

> For ECE students: For the two weeks of research, use the research two-week form provided on Moodle and submit a separate research report for this research component.

Sources: email-clarifications.md > Forms for additional internship components; email-clarifications.md > Reports for multiple approved components (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 5/5. Grounding: supported. Directly corrects meaning of plus two without outlawing other approved arrangements.

> For ECE students: No, the two weeks cannot be done at the company instead. The 6+2 arrangement specifically requires six company weeks plus two weeks of faculty research.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 5/5. Grounding: supported. Direct No and precise remaining component.

> No, you have not completed your approved arrangement yet, because the two faculty-research weeks must still be completed alongside the six company weeks.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: incomplete. Duration/pay contrast only; no exemption/optional evidence.

> Internships are typically short, lasting a minimum of 8 weeks, and can be unpaid. In contrast, CO-OP work terms are a minimum of 6 months, full-time, and paid.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Applies both limits correctly but gives less explanation.

> No, the AI-generated text is within the maximum limit of 25%, but the Turnitin similarity percentage exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness rationale but ignores wait-time tension.

> You may only apply to one internship offer at a time to give everyone a fair chance at CDC offers, and you should avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs; cdc-knowledge-base.md > How to apply through the CDC

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration inference.

> No, being added to Moodle does not prove you are registered on AUBSIS. Moodle access and AUBSIS registration are separate administrative checks, and AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 1/5. Grounding: supported. IAESTE evidence lost and topic switch falsely refused.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact fcareer@aub.edu.lb.

Sources: none (refusal)

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct unsupported-rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 5/5. Grounding: supported. Direct No with the decisive ten-week rule.

> For ECE students: No, six company weeks and two research weeks is not enough when taking another summer course. You must complete ten weeks of approved internship, which can be done either as ten weeks at one company or six weeks at one company plus four weeks at another company.

Sources: email-clarifications.md > Taking another summer course (ECE)

### k12

[Raw prompts, retrieved chunks and responses](k12.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Same false gate refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Definition plus unnecessary reporting details.

> For ECE students: A six-week company internship can be combined with two weeks of research with an MSFEA faculty member. This arrangement must be approved and documented, and requires submitting a Progress Report at the end of Week 4 of the company internship covering only the company portion, as well as a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: supported. Confirmation still answered with forms and reports.

> For ECE students doing a 6+2 arrangement, submit a separate research report for the research component. Use the research two-week form provided on Moodle, which includes the faculty supervisor, research dates, and technical nature of the work, and note that written confirmation from the faculty supervisor may also be required.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE); email-clarifications.md > Forms for additional internship components

**s04-correct — so two more weeks at the company instead?**

Score: 2/5. Grounding: supported. Repeats two alternatives and leaves correction implicit.

> For ECE students completing a 6-week internship, you must either complete 2 weeks of research with an MSFEA faculty member or a minimum 4-week internship at another company.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 5/5. Grounding: supported. Direct No and remaining research requirement.

> For ECE students: No, a six-week internship plus two-week research arrangement requires both the approved company weeks and the research component to be completed.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 4/5. Grounding: supported. Retrieves and correctly applies passing FEAA 500 waiver; omits explicit full-time detail.

> Internships are typically short, lasting a minimum of 8 weeks, and can be unpaid. In contrast, CO-OP terms are longer with a minimum duration of 6 months, and they are paid. CO-OP is an optional program. Passing FEAA 500 for CO-OP means you are no longer required to take the 0-credit Approved Experience or Professional Training course.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > CO-OP FAQs; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 3/5. Grounding: supported. Concludes similarity fails but merely restates AI limit without applying 23 explicitly.

> No, your Turnitin similarity percentage exceeds the permitted limit. The maximum allowed AI-generated text is 25%, but the maximum Turnitin similarity threshold is 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness stated but ignores the wait issue.

> To give everyone a fair chance at CDC offers, you may only apply to one offer at a time. Avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct direct registration conclusion.

> No, Moodle access and AUBSIS registration are separate administrative checks, so approval and Moodle access do not prove you are registered on AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE club/contact.

> You can join the IAESTE Club to participate in its activities and internship opportunities, and you can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 1/5. Grounding: unsupported. Says six plus two is enough and the summer course does not change requirement, contradicting retrieved ten-week rule.

> For ECE students: Yes, six weeks at one company plus two weeks of research with an MSFEA faculty member meets the ECE duration requirement. Taking another summer course does not change this requirement, provided you have the required EECE500 and departmental approval.

Sources: email-clarifications.md > Taking another summer course (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

### two_step

[Raw prompts, retrieved chunks and responses](two_step.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Same false gate refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Fact selector includes irrelevant reports and composer repeats them.

> For ECE students, a 6+2 arrangement combines a six-week company internship with two weeks of research with an MSFEA faculty member. Both components must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship covering only that part, and you must submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: supported. Confirmation again becomes documentation instructions.

> For ECE students, the two-week research component requires using the research two-week form provided on Moodle, including the faculty supervisor, research dates, and technical nature of the work. Written confirmation from the faculty supervisor may also be required.

Sources: email-clarifications.md > Forms for additional internship components

**s04-correct — so two more weeks at the company instead?**

Score: 1/5. Grounding: unsupported. Yes answers same-company two-week suggestion using a four-week different-company rule.

> For ECE students: Yes, instead of 2 weeks of faculty research, you must complete a minimum 4-week internship at another company to fulfill the requirement for a 6-week internship.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Direct No but volunteers report.

> For ECE students: No, you have not completed your approved 6+2 arrangement yet, because both the six company weeks and two faculty-research weeks must be approved and documented. You must also submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: incomplete. Duration/pay only; required waiver evidence absent.

> Internships are typically short, lasting an internship minimum duration of 8 weeks (or one to two months), and can be unpaid. In contrast, the MSFEA co-op work term is a minimum of 6 months, full-time, and paid.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct application of both numerical limits.

> Not quite. While your 23% AI-generated text is within the maximum limit of 25%, your 21% Turnitin similarity exceeds the maximum allowed threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness rationale but ignores waiting issue.

> You may only apply to one internship offer at a time to give everyone a fair chance at CDC offers, and you should avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration conclusion.

> No, Moodle access and AUBSIS registration are separate administrative checks. You cannot skip checking AUBSIS, and its registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 3/5. Grounding: incomplete. IAESTE club given but available contact dropped.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 5/5. Grounding: supported. Applies ten-week summer-course rule and says six plus two insufficient.

> For ECE students taking another summer course, the requirement is ten weeks of approved internship (either ten weeks at one company or six weeks at one company plus four weeks at another), so a six-week company plus two-week research arrangement is not enough.

Sources: email-clarifications.md > Taking another summer course (ECE)

### temperature

[Raw prompts, retrieved chunks and responses](temperature.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Identical to baseline. False pre-LLM refusal despite retrieved definition; no invented facts.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Identical to baseline. Defines correctly but adds progress-report timing and separate research report unasked.

> For ECE students: The 6+2 arrangement combines six weeks of company internship with two weeks of research with an MSFEA faculty member, and both components must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship, covering only the company part, and you must also submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: supported. Identical to baseline. Does not confirm interpretation; answers how to document research instead.

> For ECE students: For a six-week internship plus two-week research arrangement, submit a separate research report for the research component. Use the research two-week form provided on Moodle, which must include the faculty supervisor, research dates, and technical nature of the work. Written confirmation from the faculty supervisor may also be required.

Sources: email-clarifications.md > Reports for multiple approved components (ECE); email-clarifications.md > Forms for additional internship components

**s04-correct — so two more weeks at the company instead?**

Score: 1/5. Grounding: unsupported. Identical to baseline. Yes endorses two more weeks at the same company, while cited alternative is four weeks at another company. Rule itself is quoted accurately but its application is misleading.

> For ECE students: Yes, students completing a six-week internship can meet the remaining requirement by completing a minimum four-week internship at another company instead of doing two weeks of faculty research.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Identical to baseline. Correct No and remaining research component; volunteers a research-report requirement.

> For ECE students: No, you have not completed the entire arrangement until you finish both the six company weeks and the two-week research component, and you must submit a separate research report for that research component.

Sources: email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: unsupported. Identical to baseline. Duration/pay contrast mostly direct, but waiver passage is absent; unconditional no need for both omits passing FEAA 500. Optional status also omitted.

> For CO-OP: A co-op work term is a minimum of 6 months, full-time, and paid. In comparison, internships are typically short, lasting one or two months (with a minimum duration of 8 weeks for the approved experience), and can be unpaid. Additional co-ops are allowed if approved by the department and co-op advisor, but you do not need to do both a co-op and an internship.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Identical to baseline. Correctly applies independent limits; omits disclosure/citation caveat and one-point difference.

> The AI-generated text percentage of 23% is within the maximum limit of 25%, but the Turnitin similarity percentage of 21% exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Identical to baseline. Gives fairness rationale but ignores the wait-time tension; repeats avoid-rejecting advice.

> You may only apply to one CDC internship offer at a time to give everyone a fair chance at CDC offers. You should also avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Identical to baseline. Direct No, explains separate administrative checks and routes registration correctly.

> No, Moodle access and AUBSIS registration are separate administrative checks, so you cannot skip checking AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Identical to baseline. Answers IAESTE only with club and contact despite earlier internship history.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Identical to baseline. Correct refusal; no invented rationale for exactly two research weeks.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 4/5. Grounding: supported. Identical to baseline. Correctly says six plus two is insufficient and applies ten-week rule; opening does not replace is less clear than changes the requirement.

> For ECE students: Taking another summer course does not replace the requirement for ten weeks of approved internship (either ten weeks at one company or six weeks at one company plus four weeks at another), so six company weeks plus two research weeks is not enough.

Sources: email-clarifications.md > Taking another summer course (ECE)

### max_gate

[Raw prompts, retrieved chunks and responses](max_gate.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 3/5. Grounding: supported. Gate now admits the answer; correct definition but report dump remains.

> For ECE students: The 6+2 arrangement combines six weeks at a company with two weeks of research with an MSFEA faculty member. Both the six company weeks and two faculty-research weeks must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship and cover only the company internship in that report. Additionally, you must submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Defines correctly but adds progress-report timing and separate research report unasked.

> For ECE students: The 6+2 arrangement combines six weeks of company internship with two weeks of research with an MSFEA faculty member, and both components must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship, covering only the company part, and you must also submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: supported. Does not confirm interpretation; answers how to document research instead.

> For ECE students: For a six-week internship plus two-week research arrangement, submit a separate research report for the research component. Use the research two-week form provided on Moodle, which must include the faculty supervisor, research dates, and technical nature of the work. Written confirmation from the faculty supervisor may also be required.

Sources: email-clarifications.md > Reports for multiple approved components (ECE); email-clarifications.md > Forms for additional internship components

**s04-correct — so two more weeks at the company instead?**

Score: 1/5. Grounding: unsupported. Yes endorses two more weeks at the same company, while cited alternative is four weeks at another company. Rule itself is quoted accurately but its application is misleading.

> For ECE students: Yes, students completing a six-week internship can meet the remaining requirement by completing a minimum four-week internship at another company instead of doing two weeks of faculty research.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Correct No and remaining research component; volunteers a research-report requirement.

> For ECE students: No, you have not completed the entire arrangement until you finish both the six company weeks and the two-week research component, and you must submit a separate research report for that research component.

Sources: email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: unsupported. Duration/pay contrast mostly direct, but waiver passage is absent; unconditional no need for both omits passing FEAA 500. Optional status also omitted.

> For CO-OP: A co-op work term is a minimum of 6 months, full-time, and paid. In comparison, internships are typically short, lasting one or two months (with a minimum duration of 8 weeks for the approved experience), and can be unpaid. Additional co-ops are allowed if approved by the department and co-op advisor, but you do not need to do both a co-op and an internship.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correctly applies independent limits; omits disclosure/citation caveat and one-point difference.

> The AI-generated text percentage of 23% is within the maximum limit of 25%, but the Turnitin similarity percentage of 21% exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Gives fairness rationale but ignores the wait-time tension; repeats avoid-rejecting advice.

> You may only apply to one CDC internship offer at a time to give everyone a fair chance at CDC offers. You should also avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Direct No, explains separate administrative checks and routes registration correctly.

> No, Moodle access and AUBSIS registration are separate administrative checks, so you cannot skip checking AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Answers IAESTE only with club and contact despite earlier internship history.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct refusal; no invented rationale for exactly two research weeks.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 4/5. Grounding: supported. Correctly says six plus two is insufficient and applies ten-week rule; opening does not replace is less clear than changes the requirement.

> For ECE students: Taking another summer course does not replace the requirement for ten weeks of approved internship (either ten weeks at one company or six weeks at one company plus four weeks at another), so six company weeks plus two research weeks is not enough.

Sources: email-clarifications.md > Taking another summer course (ECE)

### model_current

[Raw prompts, retrieved chunks and responses](model_current.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Unchanged first-result gate blocks Explain.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Definition plus unasked reporting details.

> For ECE students, the 6+2 arrangement is a combined setup consisting of a 6-week company internship paired with 2 weeks of research with an MSFEA faculty member. Both components must be approved and documented. You submit your Progress Report at the end of Week 4 of the company internship (covering only the company portion), and you must submit a separate research report for the 2-week research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: incomplete. Still interprets confirmation as requirements and truncates mid-sentence.

> For ECE students, for the two-week research component:
>
> * Fill out the research two-week form provided on Moodle, including your faculty supervisor, research dates, and

Sources: email-clarifications.md > Forms for additional internship components

**s04-correct — so two more weeks at the company instead?**

Score: 1/5. Grounding: incomplete. Changes same-company reference to another company and truncates before completing its correction.

> For ECE students, if you complete a 6-week internship, you cannot simply add 2 more weeks at another company. You must either complete 2 weeks of research with

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 5/5. Grounding: supported. Direct No and precise unfinished component.

> No. For ECE students, an approved 6+2 arrangement requires completing and documenting both the six company weeks and the two faculty-research weeks to satisfy the required duration. Since you have not yet started the research component, you have not completed your approved arrangement.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 1/5. Grounding: supported. Refuses comparison because waiver evidence is absent; no invented waiver.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact fcareer@aub.edu.lb.

Sources: none (refusal)

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct separate numeric conclusions, no disclosure reminder.

> No. Based on the numbers you provided, your 23% AI-generated text is within the 25% limit, but your 21% Turnitin similarity exceeds the 20% maximum permitted threshold.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness only; wait issue ignored.

> You may only apply to one CDC offer at a time to give everyone a fair chance at CDC offers. You should also avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration inference.

> No. Moodle access and AUBSIS registration are separate administrative checks, so being added to Moodle does not mean you are registered on AUBSIS. You must still verify and resolve your AUBSIS registration through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE topic switch with contact.

> MSFEA students can get involved by joining the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 1/5. Grounding: incomplete. Starts the correct ten-week conclusion but truncates the required alternatives.

> No. For ECE students, taking another summer course while completing EECE500 requires completing ten weeks of approved internship—either ten weeks at one company, or six weeks at one company plus

Sources: email-clarifications.md > Taking another summer course (ECE)

### native_system

[Raw prompts, retrieved chunks and responses](native_system.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Unchanged gate refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Definition plus unasked reports.

> For ECE students: The 6+2 arrangement combines a six-week company internship with two weeks of research with an MSFEA faculty member. The arrangement must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship covering only the company portion, and submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 2/5. Grounding: supported. Mentions two-week research meaning, then dumps forms/reports without direct confirmation.

> For ECE students: The two-week research component is done alongside a six-week company internship as part of the 6+2 arrangement. You must use the research two-week form on Moodle, including the faculty supervisor, research dates, and technical nature of the work, and you may be required to provide written confirmation from the faculty supervisor. You also must submit a separate research report for this research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); email-clarifications.md > Forms for additional internship components; email-clarifications.md > Reports for multiple approved components (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 1/5. Grounding: unsupported. Misleading Yes to same-company two-week suggestion, quoting a different-company four-week alternative.

> For ECE students: Yes, students completing a six-week internship can fulfill the requirement by doing either two weeks of research with an MSFEA faculty member or a minimum four-week internship at another company.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Correct No but adds report.

> For ECE students: No, you have not completed the arrangement yet, because the two-week faculty-research component still needs to be completed and documented, and you must submit a separate research report for it.

Sources: email-clarifications.md > Combined internship arrangements (ECE); email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: unsupported. Invents unsupported unconditional exemption from doing both; retrieved duration does not establish the waiver.

> For CO-OP: A co-op work term is a minimum of 6 months, full-time, and paid. In contrast, internships are typically short, lasting one or two months (with a minimum of 8 weeks for the approved experience), and can be unpaid. You do not need to do both; the MSFEA co-op requirement is satisfied by one 6-month work term, and additional co-ops are allowed only if approved by the department and co-op advisor.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct numerical comparison.

> For your AI percentage, 23% is within the maximum permitted limit of 25%. However, your Turnitin similarity percentage of 21% exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness only, wait issue unaddressed.

> You may only apply to one offer at a time to give everyone a fair chance at CDC offers.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct direct registration answer.

> No, Moodle access and AUBSIS registration are separate administrative checks, so being on Moodle does not prove you are registered on AUBSIS. You must resolve AUBSIS registration through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE club/contact.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities by contacting iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 1/5. Grounding: unsupported. Offers six plus two as an alternative while taking a summer course, despite retrieved ten-week condition.

> For ECE students: Taking another summer course does not replace the internship duration requirements. To satisfy EECE500, you must complete ten weeks of approved internship: either ten weeks at one company or six weeks at one company plus four weeks at another company, with both companies requiring the applicable forms and employer documentation. Alternatively, you can do a combined arrangement such as a six-week internship plus a two-week research component, which must be approved and documented.

Sources: email-clarifications.md > Taking another summer course (ECE); email-clarifications.md > Combined internship arrangements (ECE)

### confirmation_frame

[Raw prompts, retrieved chunks and responses](confirmation_frame.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Gate refusal unchanged.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Definition plus reports.

> For ECE students: The 6+2 arrangement is a combined internship where you complete six weeks at a company and two weeks of research with an MSFEA faculty member. Both components must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship covering only that part, and you must submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 4/5. Grounding: supported. Confirms correctly but volunteers research report.

> Yes, the six company weeks are combined with two weeks of research with an MSFEA faculty member, and both components must be approved and documented. For ECE students, submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); email-clarifications.md > Reports for multiple approved components (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 4/5. Grounding: supported. Corrects precisely but adds unasked alternative.

> No, for ECE students, the six company weeks plus two weeks of faculty research means two weeks of research with an MSFEA faculty member, not two more weeks at the company. Alternatively, you can complete a minimum 4-week internship at another company.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 1/5. Grounding: supported. False refusal; this prototype also changed trailing newlines on non-target questions.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 2/5. Grounding: incomplete. Omits required minimum and waiver; does not resolve doing both.

> For CO-OP: A co-op work term has a minimum duration of 6 months, is full-time, and is paid. In contrast, internships are typically shorter at one or two months and can be unpaid. Regarding whether you need to do both, a 6-month co-op is required, and additional co-ops (consecutive or not) are allowed if approved by the department and co-op advisor.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct independent limits.

> No, the Turnitin similarity percentage exceeds the permitted limit. Based on the facts you stated, your AI-generated text is within the 25% maximum, but your 21% similarity exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness only.

> You may only apply to one offer at a time to give everyone a fair chance at CDC offers.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration inference.

> No, Moodle access and AUBSIS registration are separate administrative checks, so you cannot skip checking AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE switch.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 1/5. Grounding: unsupported. Incorrectly accepts six plus two with summer course; non-target prompt newline also changed.

> For ECE students: Taking another summer course while completing EECE500 does not change the duration requirement, so a six-week company internship plus two-week faculty research arrangement is sufficient provided it is approved and documented.

Sources: email-clarifications.md > Taking another summer course (ECE); email-clarifications.md > Combined internship arrangements (ECE)

### confirmation_frame_v2

[Raw prompts, retrieved chunks and responses](confirmation_frame_v2.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Gate refusal unchanged.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Byte-identical baseline question and reporting detail.

> For ECE students: The 6+2 arrangement combines six weeks of company internship with two weeks of research with an MSFEA faculty member, and both components must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship, covering only the company part, and you must also submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 4/5. Grounding: supported. Correct confirmation, but adds report.

> For ECE: Correct. The 6+2 arrangement combines six company weeks with two weeks of research with an MSFEA faculty member, and you must submit a separate research report for that research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); email-clarifications.md > Reports for multiple approved components (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 3/5. Grounding: supported. Corrects meaning then repeats alternatives redundantly.

> For ECE students: No, a 6+2 arrangement means six company weeks plus two weeks of faculty research, not two additional weeks at the company. Alternatively, completing a 6-week internship requires either 2 weeks of research with an MSFEA faculty member or a minimum 4-week internship at another company.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Baseline correct No plus extra report.

> For ECE students: No, you have not completed the entire arrangement until you finish both the six company weeks and the two-week research component, and you must submit a separate research report for that research component.

Sources: email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: unsupported. Baseline unsupported waiver persists.

> For CO-OP: A co-op work term is a minimum of 6 months, full-time, and paid. In comparison, internships are typically short, lasting one or two months (with a minimum duration of 8 weeks for the approved experience), and can be unpaid. Additional co-ops are allowed if approved by the department and co-op advisor, but you do not need to do both a co-op and an internship.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct numeric comparison.

> The AI-generated text percentage of 23% is within the maximum limit of 25%, but the Turnitin similarity percentage of 21% exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness only.

> You may only apply to one CDC internship offer at a time to give everyone a fair chance at CDC offers. You should also avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration inference.

> No, Moodle access and AUBSIS registration are separate administrative checks, so you cannot skip checking AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE switch.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 4/5. Grounding: supported. Baseline correct ten-week rule.

> For ECE students: Taking another summer course does not replace the requirement for ten weeks of approved internship (either ten weeks at one company or six weeks at one company plus four weeks at another), so six company weeks plus two research weeks is not enough.

Sources: email-clarifications.md > Taking another summer course (ECE)

### structured

[Raw prompts, retrieved chunks and responses](structured.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Unchanged gate refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Definition plus unasked report.

> For ECE students, the six-week internship plus two-week research arrangement requires that both the six company weeks and two faculty-research weeks are approved and documented, with a separate research report submitted for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 1/5. Grounding: supported. Observable resolved_question wrongly broadens confirmation into requirements.

> For ECE students, the two-week research component requires using the research two-week form on Moodle, which must include the faculty supervisor, research dates, and technical nature of the work, and may require written confirmation from the faculty supervisor. Additionally, students must submit a separate research report for this component.

Sources: email-clarifications.md > Forms for additional internship components; email-clarifications.md > Reports for multiple approved components (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 2/5. Grounding: supported. Repeats alternative rules without direct correction.

> For ECE students completing a 6-week internship, you must either complete 2 weeks of research with an MSFEA faculty member or a minimum 4-week internship at another company.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 1/5. Grounding: supported. False refusal of supported incomplete-arrangement question.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 2/5. Grounding: incomplete. Omits eight-week minimum and waiver, adds irrelevant CO-OP clarification.

> For duration and pay, internships are typically short at one or two months and can be unpaid, while CO-OP work terms are a minimum of 6 months, full-time, and paid. CO-OP has its own rules — say CO-OP if that's your programme.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct arithmetic comparison.

> Not quite, as the 21% Turnitin similarity exceeds the 20% maximum threshold, although the 23% AI-generated text is within the 25% limit.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness only.

> You may only apply to one internship offer at a time to give everyone a fair chance at CDC offers.

Sources: cdc-knowledge-base.md > Internship FAQs; cdc-knowledge-base.md > How to apply through the CDC

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration conclusion.

> No. Moodle access and AUBSIS registration are separate administrative checks, so AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 3/5. Grounding: incomplete. Club given but available contact omitted.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 2/5. Grounding: unsupported. Says taking summer course does not change rule while applying ten-week rule; misstates the condition.

> No, taking another summer course does not change the duration requirement, but your arrangement of six company weeks plus two research weeks is insufficient because EECE500 requires ten weeks of approved internship (such as ten weeks at one company or six weeks at one company plus four weeks at another company).

Sources: email-clarifications.md > Taking another summer course (ECE); cdc-knowledge-base.md > What it is

### resolve_turn

[Raw prompts, retrieved chunks and responses](resolve_turn.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Unchanged gate refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 3/5. Grounding: supported. Definition still includes reporting dump.

> For ECE students: The 6+2 arrangement allows you to combine a six-week company internship with two weeks of research with an MSFEA faculty member to meet the duration requirement. Both components must be approved and documented. You must submit the Progress Report at the end of Week 4 of the company internship covering only the company portion, and submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 5/5. Grounding: supported. Source-free interpretation produces exact confirmation; concise correct reply.

> Yes, the 6+2 arrangement for ECE students includes six company weeks combined with two weeks of research with an MSFEA faculty member.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 5/5. Grounding: supported. Correctly rejects same-company substitution.

> No, for ECE students the 6+2 arrangement means six company weeks plus two weeks of faculty research, not additional time at the company.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 5/5. Grounding: supported. Applies remaining research requirement directly.

> No, your understanding is not correct. The approved arrangement consists of both the six company weeks and the two research weeks, so you have not completed it until you finish the research component as well.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 2/5. Grounding: incomplete. Cannot resolve doing both; vague statement that co-op is required omits optional status and waiver.

> For CO-OP: A co-op work term is a minimum of 6 months, full-time, and paid. In contrast, internships are typically short, lasting one or two months (with a minimum duration of 8 weeks for the approved experience), and can be unpaid. Regarding whether you need to do both, a 6-month co-op is required; additional co-ops, whether consecutive or not, are allowed if approved by the department and co-op advisor.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct separate thresholds, wording unnecessarily admonishing.

> No, your understanding is incorrect. While 23% AI-generated text is within the maximum limit of 25%, a 21% Turnitin similarity percentage exceeds the maximum allowed threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 4/5. Grounding: supported. Rewrites why as confirmation but answer still gives fairness and acknowledges wait.

> Yes, you may only apply to one internship offer at a time to ensure everyone gets a fair chance, even though employers typically take two to three weeks to respond.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration inference.

> No, Moodle access and AUBSIS registration are separate administrative checks, so Moodle access does not prove you are registered on AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE switch.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 1/5. Grounding: incomplete. Interpreter removes why, so documented rule is affirmed instead of refusing absent rationale.

> Yes, for the ECE 6+2 arrangement, the department requires two weeks of research with an MSFEA faculty member to complement the six-week internship.

Sources: summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 1/5. Grounding: unsupported. Accepts six plus two with another summer course.

> For ECE students: Yes, a six-week company internship plus two-week research arrangement is sufficient if approved and documented, and you may also take another summer course with the required EECE500 and departmental approval.

Sources: email-clarifications.md > Taking another summer course (ECE); email-clarifications.md > Combined internship arrangements (ECE)

### task_contract

[Raw prompts, retrieved chunks and responses](task_contract.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 1/5. Grounding: supported. Unchanged gate refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s02-what — What is the 6+2 arrangement**

Score: 4/5. Grounding: supported. Two-sentence definition but includes one unasked reporting requirement.

> For ECE students, the 6+2 arrangement is a combined internship where you complete six weeks at a company and two weeks of research with an MSFEA faculty member. The arrangement must be approved and documented, and you must submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 5/5. Grounding: supported. Direct concise confirmation; no forms or reports.

> Correct, the arrangement combines six company weeks with two weeks of research with an MSFEA faculty member.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 5/5. Grounding: supported. Direct correction; no irrelevant alternatives.

> Not quite. For ECE, the six company weeks and two research weeks arrangement means six company weeks plus two weeks of faculty research rather than two more weeks at the company.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Correct No plus one unasked report.

> For ECE students: No, you have not completed the entire arrangement until you finish both the six company weeks and the two-week research component, and you must submit a separate research report for that research component.

Sources: email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 3/5. Grounding: incomplete. Duration/pay comparison, but no waiver evidence or complete answer.

> Internships are typically short, lasting a minimum of 8 weeks, and can be unpaid. In contrast, CO-OP work terms are longer, with a minimum duration of 6 months, and are paid.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct numeric comparison.

> The AI-generated text percentage of 23% is within the maximum limit of 25%, but the Turnitin similarity percentage of 21% exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 1/5. Grounding: supported. Explicit reason cue wrongly refuses documented fairness rationale.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact fcareer@aub.edu.lb.

Sources: none (refusal)

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration inference.

> No, Moodle access and AUBSIS registration are separate administrative checks, so you cannot skip checking AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE switch.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 5/5. Grounding: supported. Precisely applies ten-week condition, rejecting six plus two.

> For ECE students: No, a six-week company internship plus two-week research arrangement is not enough when taking another summer course. To fulfill EECE500 while taking another summer course, you must complete ten weeks of approved internship, which can be done either as ten weeks at one company or six weeks at one company plus four weeks at another company.

Sources: email-clarifications.md > Taking another summer course (ECE)

### combined

[Raw prompts, retrieved chunks and responses](combined.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 3/5. Grounding: supported. Answers Explain but still includes reports.

> For ECE students, the 6+2 arrangement combines a six-week company internship with two weeks of research with an MSFEA faculty member. Both the six company weeks and two faculty-research weeks must be approved and documented. A separate research report must be submitted for the research component, and the Progress Report submitted at the end of Week 4 must cover only the company internship.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s02-what — What is the 6+2 arrangement**

Score: 4/5. Grounding: supported. Concise definition; followed-by wording could imply an order the source does not expressly mandate, so avoid treating it as an ordering rule.

> For ECE students, a 6+2 arrangement is a combined internship where you complete six weeks at a company followed by two weeks of research with an MSFEA faculty member. The complete arrangement must be approved and documented.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 5/5. Grounding: supported. Direct confirmation without reporting dump.

> Correct. As discussed, the two weeks of research are conducted with an MSFEA faculty member as part of the combined arrangement.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 5/5. Grounding: supported. Direct correction without alternatives.

> No, for ECE the 6+2 arrangement means six company weeks plus two weeks of faculty research, not additional time at the company.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 5/5. Grounding: supported. Clear No and missing research component.

> For ECE students: No, a six-week internship plus two-week research arrangement requires both the approved company weeks and the research component to be completed.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 5/5. Grounding: supported. All requested comparison premises recovered and synthesized.

> For internships:
> - Duration: minimum of 8 weeks.
> - Pay: can be unpaid.
>
> For CO-OP:
> - Duration: minimum of 6 months.
> - Pay: paid full-time.
> - Mandatory status: optional program.
> - Requirement interaction: students who pass FEAA 500 for CO-OP are no longer required to take the 0-credit Approved Experience / Professional Training course in their department.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 3/5. Grounding: supported. Correct similarity conclusion but mainly restates limits.

> No, your Turnitin similarity percentage exceeds the permitted limit. The maximum allowed AI-generated text is 25%, but the maximum Turnitin similarity threshold is 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Fairness only.

> To give everyone a fair chance at CDC offers, you may only apply to one offer at a time. Avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Correct registration inference.

> No, Moodle access and AUBSIS registration are separate administrative checks, so approval and Moodle access do not prove you are registered on AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE switch.

> You can join the IAESTE Club to participate in its activities and internship opportunities, and you can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correct rationale refusal.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 1/5. Grounding: unsupported. Combination regresses: accepts six plus two with another summer course despite ten-week source.

> For ECE students: Yes, six weeks at one company plus two weeks of research with an MSFEA faculty member meets the ECE internship duration requirement, and taking another summer course does not change this as long as you have the required EECE500 and departmental approval.

Sources: email-clarifications.md > Taking another summer course (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

### combined_adaptive

[Raw prompts, retrieved chunks and responses](combined_adaptive.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 4/5. Grounding: supported. Answers Explain in two sentences; one unasked research-report detail remains.

> For ECE students: The 6+2 arrangement combines a six-week company internship with a two-week research component with an MSFEA faculty member. Both the company weeks and faculty-research weeks must be approved and documented, and a separate research report must be submitted for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s02-what — What is the 6+2 arrangement**

Score: 4/5. Grounding: supported. Consistent definition across paraphrase; one report detail remains.

> For ECE students, the 6+2 arrangement is a combined internship where you complete six weeks at a company and two weeks of research with an MSFEA faculty member. The arrangement must be approved and documented, and you must submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 5/5. Grounding: supported. Direct concise confirmation with no unasked administrative content.

> Correct, the arrangement combines six company weeks with two weeks of research with an MSFEA faculty member.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 5/5. Grounding: supported. Direct correction tied to research meaning; no unrelated alternative.

> Not quite. For ECE, the six company weeks and two research weeks arrangement means six company weeks plus two weeks of faculty research rather than two more weeks at the company.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Correct remaining research conclusion; extra report requirement.

> For ECE students: No, you have not completed the entire arrangement until you finish both the six company weeks and the two-week research component, and you must submit a separate research report for that research component.

Sources: email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 5/5. Grounding: supported. Explicit duration/pay comparison, optional CO-OP and conditional FEAA 500 waiver, all supported.

> For internships:
> - Duration: minimum of 8 weeks.
> - Pay: can be unpaid.
>
> For CO-OP:
> - Duration: minimum of 6 months.
> - Pay: paid full-time.
> - Mandatory status: optional program.
> - Requirement interaction: students who pass FEAA 500 for CO-OP are no longer required to take the 0-credit Approved Experience / Professional Training course in their department.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct independent numerical application; no disclosure caveat or one-point calculation.

> The AI-generated text percentage of 23% is within the maximum limit of 25%, but the Turnitin similarity percentage of 21% exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Documented fairness rationale; still does not address the wait-time tension explicitly.

> You may only apply to one CDC internship offer at a time to give everyone a fair chance at CDC offers. You should also avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Direct supported registration inference.

> No, Moodle access and AUBSIS registration are separate administrative checks, so you cannot skip checking AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE topic switch and contact.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correctly refuses undocumented rationale.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 5/5. Grounding: supported. Direct No and correct ten-week rule for the stated summer-course condition.

> For ECE students: No, a six-week company internship plus two-week research arrangement is not enough when taking another summer course. To fulfill EECE500 while taking another summer course, you must complete ten weeks of approved internship, which can be done either as ten weeks at one company or six weeks at one company plus four weeks at another company.

Sources: email-clarifications.md > Taking another summer course (ECE)

### combined_adaptive_repeat

[Raw prompts, retrieved chunks and responses](combined_adaptive_repeat.jsonl)

**s01-explain — Explain the 6+2 arrangement**

Score: 4/5. Grounding: supported. Answers Explain in two sentences; one unasked research-report detail remains.

> For ECE students: The 6+2 arrangement combines a six-week company internship with a two-week research component with an MSFEA faculty member. Both the company weeks and faculty-research weeks must be approved and documented, and a separate research report must be submitted for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s02-what — What is the 6+2 arrangement**

Score: 4/5. Grounding: supported. Consistent definition across paraphrase; one report detail remains.

> For ECE students, the 6+2 arrangement is a combined internship where you complete six weeks at a company and two weeks of research with an MSFEA faculty member. The arrangement must be approved and documented, and you must submit a separate research report for the research component.

Sources: email-clarifications.md > Combined internship arrangements (ECE); summer-training-guidelines-2026.md > Electrical and Computer Engineering (ECE)

**s03-confirm — so 2 weeks of research**

Score: 5/5. Grounding: supported. Direct concise confirmation with no unasked administrative content.

> Correct, the arrangement combines six company weeks with two weeks of research with an MSFEA faculty member.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s04-correct — so two more weeks at the company instead?**

Score: 5/5. Grounding: supported. Direct correction tied to research meaning; no unrelated alternative.

> Not quite. For ECE, the six company weeks and two research weeks arrangement means six company weeks plus two weeks of faculty research rather than two more weeks at the company.

Sources: email-clarifications.md > Combined internship arrangements (ECE)

**s05-component — I finished the six company weeks but have not started the research. Have I completed my approved 6+2 arrangement?**

Score: 4/5. Grounding: supported. Correct remaining research conclusion; extra report requirement.

> For ECE students: No, you have not completed the entire arrangement until you finish both the six company weeks and the two-week research component, and you must submit a separate research report for that research component.

Sources: email-clarifications.md > Reports for multiple approved components (ECE)

**s06-comparison — How does the required internship compare with CO-OP in duration, pay, and whether I need to do both?**

Score: 5/5. Grounding: supported. Explicit duration/pay comparison, optional CO-OP and conditional FEAA 500 waiver, all supported.

> For internships:
> - Duration: minimum of 8 weeks.
> - Pay: can be unpaid.
>
> For CO-OP:
> - Duration: minimum of 6 months.
> - Pay: paid full-time.
> - Mandatory status: optional program.
> - Requirement interaction: students who pass FEAA 500 for CO-OP are no longer required to take the 0-credit Approved Experience / Professional Training course in their department.

Sources: msfea-cdc-coop-handbook.md > What CO-OP is; cdc-knowledge-base.md > Quick Reference: Key Numbers; msfea-cdc-coop-handbook.md > Policies

**s07-two-thresholds — My report has 23% AI-generated text and 21% Turnitin similarity. Are both within the permitted limits?**

Score: 4/5. Grounding: supported. Correct independent numerical application; no disclosure caveat or one-point calculation.

> The AI-generated text percentage of 23% is within the maximum limit of 25%, but the Turnitin similarity percentage of 21% exceeds the maximum threshold of 20%.

Sources: email-clarifications.md > AI use, similarity, and report revision

**s08-why — Why can I only apply to one CDC internship offer at a time, even though companies take weeks to reply?**

Score: 3/5. Grounding: supported. Documented fairness rationale; still does not address the wait-time tension explicitly.

> You may only apply to one CDC internship offer at a time to give everyone a fair chance at CDC offers. You should also avoid applying to offers you might later reject.

Sources: cdc-knowledge-base.md > Internship FAQs

**s09-registration — My petition was approved and I was added to Moodle. Does that prove I am registered on AUBSIS and can skip checking it?**

Score: 5/5. Grounding: supported. Direct supported registration inference.

> No, Moodle access and AUBSIS registration are separate administrative checks, so you cannot skip checking AUBSIS. AUBSIS registration must be resolved through the appropriate academic or Registrar process.

Sources: email-clarifications.md > Moodle access and registration

**s10-topic-switch — How do I join IAESTE?**

Score: 5/5. Grounding: supported. Correct IAESTE topic switch and contact.

> MSFEA students can join the IAESTE Club to participate in its activities and internship opportunities. You can contact them at iaeste.lebanon@aub.edu.lb.

Sources: cdc-knowledge-base.md > IAESTE — International Internship Exchange

**s11-unsupported-why — Why exactly did the department choose two research weeks instead of one for the ECE 6+2 arrangement?**

Score: 5/5. Grounding: supported. Correctly refuses undocumented rationale.

> I couldn't find a specific answer to that. I can help with the CDC's programs — internships (Approved Experience), CO-OP, IAESTE, full-time job support, and mentorship — so try asking a more specific question (for example, name the program and what you need, like deadlines, eligibility, or deliverables). If your question was already specific and I still couldn't help, please contact Rafika Dinnawi (rd39@aub.edu.lb), the Electrical and Computer Engineering coordinator.

Sources: none (refusal)

**s12-summer-course — I have approval to take another summer course during EECE500. Is six company weeks plus two research weeks enough, or does taking the course change the requirement?**

Score: 5/5. Grounding: supported. Direct No and correct ten-week rule for the stated summer-course condition.

> For ECE students: No, a six-week company internship plus two-week research arrangement is not enough when taking another summer course. To fulfill EECE500 while taking another summer course, you must complete ten weeks of approved internship, which can be done either as ten weeks at one company or six weeks at one company plus four weeks at another company.

Sources: email-clarifications.md > Taking another summer course (ECE)
