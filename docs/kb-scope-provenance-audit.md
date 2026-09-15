# Knowledge-base scope and provenance audit

Date: 2026-09-15
Implementation stage: KB publication guard Step 1

## Result

The current general-plus-exceptions document structure is retained. The audit found
one concrete metadata defect: `email-clarifications.md` declared a department but no
program or review provenance in frontmatter. Both source and normalized copies now
declare the internship program, the existing September 2026 project-review record,
and a stable source identity. No policy passage, heading, or chunk boundary was
rewritten.

The table below is an engineering traceability record, not policy-owner approval.
“General” is treated as a positive applicability claim. Where the reviewed sources do
not state a department-specific rule, the table records that absence instead of
inventing one.

## High-risk rule matrix

| Rule | General rule | MECH | ECE | CHEM | IEM | CEE | Source / effective information | Review status |
|---|---|---|---|---|---|---|---|---|
| Duration | Minimum 8 full weeks / typically 320 hours | No separate duration exception stated | 6 weeks plus 2 faculty-research weeks, or at least 4 weeks at another company | No separate duration exception stated | A 6-week placement may be petitioned for selected companies; 6+2 or at least 4 more company weeks is documented | A reduced 6-week placement may be approved exceptionally for selected companies | `summer-training-guidelines-2026.md` > Internship Requirements and department sections; June 2026. ECE approval/documentation detail also in approved `email-clarifications.md`; project review, September 2026 | Owner review needed for what qualifies as “selected companies” and who records exceptional approval |
| 6+2 / 4+4 | No universal split authorization | Two 4-week periods are prohibited; 6+2 is explicitly rejected by the approved clarification | 6+2 requires approval/documentation. A 4+4 proposal is case-specific and needs prior petition/written approval | Splitting is allowed only in the same summer; exact component lengths are not stated | 6+2 is documented after a 6-week placement; no 4+4 rule stated | 4+4 is allowed if one period is civil or construction engineering | Same sources/dates as duration | CHEM reporting details and IEM 4+4 treatment are unresolved; do not infer them |
| Concurrent summer course | No universal rule stated | Allowed if required work hours are completed | Approved concurrent course changes the email-clarification rule to 10 company-internship weeks: 10 at one company or 6+4 at two | No rule stated | No rule stated | Allowed while completing internship-hour requirements | Department sections, June 2026; ECE approved clarification, September 2026 | Owner should confirm whether MECH/CEE require advance approval and whether their wording implies any duration change |
| Eligibility | Minimum 90 completed credits | General rule only | General rule only | General rule only | General rule only | General rule only | `summer-training-guidelines-2026.md` > Eligibility. Supplied by CDC through project owner on 2026-08-05 and explicitly noted as absent from the June DOCX | Must be incorporated into the next official source revision; no department exception is documented |
| Remote work | Not accepted, subject to documented department exceptions | No exception stated | No exception stated | No exception stated | U.S.-based remote work is allowed only with legal U.S. work eligibility and department approval | No exception stated | `summer-training-guidelines-2026.md` > Internships That Are Not Accepted / IEM; owner-confirmed precedence 2026-08-05 | Reviewed exception relationship; future changes require explicit owner confirmation |
| Reports | Progress report by end of week 4; final report within 1 week after completion | No separate report rule stated | Separate research report for 6+2; one clearly separated final report for two internships; ECE final report due within 1 week | Reporting differs for one versus multiple companies, but details are absent | No separate report rule stated | No separate report rule stated | Summer guidelines, June 2026; ECE approved clarification, September 2026 | CHEM details are a blocking ambiguity for any curated answer that tries to state them |
| Presentations | Department-dependent; generally in person or recorded, with first-two-weeks-of-Fall scheduling | No exception stated | Voice-over presentation constraints in the approved clarification; final presentation due within 1 week after internship | Recorded 3-minute presentation required | Generally not required unless specified; selected students may present in seminars/orientation | No exception stated | Summer guidelines, June 2026; ECE approved clarification, September 2026 | Owner should reconcile general Fall scheduling with ECE's one-week deadline in the next official revision |
| Deadlines | Registrar controls registration/payment dates; timeline states week-1 arrival, week-4 progress, final report within 1 week, and presentation timing by department | General dates only | Report and presentation within 1 week after the individual end date; email clarification says extensions are not automatic | General dates only | General dates only | General dates only | Summer guidelines, June 2026; approved clarification, September 2026 | Exact current calendar dates must come from Registrar/Moodle and must be refused when absent |

## Provenance and applicability decisions

- The June 2026 summer-guidelines DOCX remains the declared source for extracted
  passages. Its normalized footer separately identifies owner-supplied additions and
  their 2026-08-05 review date; file timestamps were not used as policy dates.
- `email-clarifications.md` is an authorized clarification source under the existing
  intake decision recorded in `kb/README.md`: approved during project review in
  September 2026. The shared admin process does not establish an individual approver
  or two-person review, so the metadata does not claim either.
- Missing department-specific text means “not documented here,” not “prohibited” or
  “identical.” General rules remain applicable only where the source positively
  supports general applicability.
- The remote-work general rule and IEM exception, and the general presentation rule
  and department exceptions, are retained together. They are not duplicates.

## Regression coverage

`eval/scope_regression_set.jsonl` freezes eight independently source-grounded cases:
one per department, general-rule application, paraphrases, condition boundaries,
follow-up resolution, exception precedence, an exact deadline distinction, and an
unknown-department comparison. `eval.synthesis_gate` runs these beside—not instead
of—the existing synthesis and follow-up sets, with the existing top-k and similarity
threshold unchanged.

Unit coverage additionally fails on missing/invalid normalized department or program,
checks all five department fixtures, preserves nested scope inheritance, verifies
retrieved metadata, and checks applicability labels in unknown-department model
context. The legacy direct-curation scope defect remains a strict expected failure
until Step 2 replaces it with revision storage and validated scope.
