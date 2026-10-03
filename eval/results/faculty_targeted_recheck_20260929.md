> Historical evaluation evidence/protocol. Settings, results and instructions refer to the dated run below; use [current task guidance](../../docs/README.md) for today's implementation and verification.

# Focused faculty-question recheck — 2026-09-29

The previous 205-case run exposed three false refusals and several answers that missed the student's actual question or a consequential requirement. This follow-up changed only source-backed KB passages, rebuilt the local pgvector index from source, and replayed 19 selected, anonymized faculty questions across five departments. No model judge was used. The review below is a human assessment of the answer text against the current approved KB and the owner's conflict decisions; it is not a new full-set accuracy score.

| Check | Result |
| --- | ---: |
| Selected questions answered without an API error | 19/19 |
| Previously false-refused questions now answered | 3/3 |
| Unwarranted refusals in this replay | 0/19 |
| Answers judged materially correct and useful | 19/19 |
| Annotated source document retrieved | 19/19 |

The 19 cases include the five department variants of the six-week question, three department variants of Dar Al-Handasah 6+2, the three earlier false refusals, CEE acceptable work, ECE presentation, CHEM report content, CO-OP final documents, and nearby controls. Full answers and citations are in [the compact replay record](faculty_targeted_recheck_20260929.jsonl). The replay used the locally rebuilt index and Gemini 3.5 Flash-Lite, with an 8.5-second minimum delay between requests. It consumed 19 generation calls in the normal case; no full 205-case run or model-judge calls were made.

The three former refusals now directly answer the student: a bare employer attendance letter is insufficient (`faculty-087-chem`), students find their own internships with CDC and coordinator support (`faculty-132-chem`), and CO-OP follows its own proposal/admission process rather than a universal internship-course Moodle proposal (`faculty-145-ece`). The CEE work-type answer now addresses technical relevance (`faculty-134-cee`); ECE directly confirms its Final Voice-over Presentation (`faculty-070-ece`); and the CHEM CO-OP final-deliverables answer includes the signed company completion letter (`faculty-177-chem`). The six-week and Dar 6+2 answers remain department-specific.

Some answers are concise. For example, the IEM Dar 6+2 answer says "for the approved" arrangement and gives the reporting requirements but does not restate the approval process. This is useful and not materially misleading under the requested student-information standard. The CO-OP proposal answer points to the advisor/timeline rather than inventing an exact submission date absent from the handbook. These are not grounds for another change or a larger test run.

This is a focused regression check, not a claim that all 205 cases are flawless. The local source-ingestion/chunking checks passed (23 tests), and the deployment still requires separate Oracle smoke verification.
