# Final production configuration review

Manual coding-assistant review against the frozen expected qualities and retrieved
source chunks. This is not an independent human or calibrated-judge score.

| Case | Synthesis /5 | Grounding | Review |
|---|---:|---|---|
| s01-explain | 5 | supported | Direct definition, both components and approval/documentation |
| s02-what | 5 | supported | Same meaning and quality as Explain |
| s03-confirm | 5 | supported | Direct one-sentence confirmation |
| s04-correct | 5 | supported | Corrects company-vs-research misunderstanding |
| s05-component | 5 | supported | Directly identifies missing research component |
| s06-comparison | 5 | supported | Covers duration, pay, optional status and FEAA 500 waiver |
| s07-two-thresholds | 4 | supported | Correct decision and limits; omits one-point calculation/disclosure caveat |
| s08-why | 3 | supported | Correct fairness rationale; omits explicit wait-time acknowledgement |
| s09-registration | 5 | supported | Correct inference from separate administrative checks |
| s10-topic-switch | 4 | supported | Clean IAESTE switch and joining action; omits contact email |
| s11-unsupported-why | 5 | supported refusal | Refuses undocumented rationale |
| s12-summer-course | 5 | supported | Applies conditional ten-week rule and rejects 6+2 |

Mean synthesis over 11 answerable cases: **4.64/5**. Observed unsupported
answers: **0**. False refusals: **0/11**. All-premise retrieval/gate: **11/11**.
Provider calls: 12. Input tokens: 29,163.

`production_final_12.jsonl` contains the actual production prompts, retrieval and
answers. `production_condition_v3.jsonl` and `production_summer_v3.jsonl` verify
both sides of the conditional rule that caused a regression in the first broad run.
