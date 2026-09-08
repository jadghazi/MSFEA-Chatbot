# Broader golden-set review

`golden_final.jsonl` is the clean broader verification run. It uses the selected
configuration on the existing 74-case golden set (68 answerable, six refusals).
This is separate from the frozen 12-case synthesis experiment and its scores.
The earlier `golden_contaminated_discarded.jsonl` is invalid and excluded.

## Known weaknesses checked against the original pipeline

Four concerning outputs were rerun through the saved original prompt/gate/depth
as `golden_spot_baseline.jsonl`, using `golden_spot_cases.jsonl`.

| Case | Selected result | Baseline control |
|---|---|---|
| dept-split-internship | Gives only the Mechanical rule, despite no selected department | Identical text |
| dept-consulting | Generalizes the technical-consulting rule without clarifying department | Identical text |
| coop-deliverables | Lists only arrival and progress items, omitting final deliverables | Identical text |
| internship-vs-coop | Uses generic one/two-month internship description and omits graduation/course conditions | Same omissions; different phrasing |

These remain limitations. The focused comparison with explicit duration, pay and
waiver dimensions performs better, but that does not establish that every comparison
paraphrase is solved. The broad comparison's required graduation premise remains
absent from retrieved context; another prompt instruction cannot recover missing
evidence. Its generic internship duration also needs reconciliation with the
Approved Experience eight-week minimum before a future release claims completeness.

The real HTTP summer-course paraphrase gives the ten-week rule correctly but
does not lead with an explicit No. Fixed-case synthesis scores must not be used to
hide this wording sensitivity.

The first clean broad run also attached the separate ten-week summer-course rule
to “six company weeks for the 6+2 option.” The baseline control answered that case
correctly, identifying this as a regression in the decision cue rather than an
existing weakness. Before release, the cue was narrowed to require that every
numeric rule's own source conditions match the student's circumstances. Targeted
live controls for this 6+2 case and the actual summer-course condition are saved
as `decision_guard_condition.jsonl` and `decision_guard_summer.jsonl`.

Citation/refusal/disclaimer counts describe structural checks, not complete factual
accuracy. The manual review also noted smaller omissions (for example, the generic
petition answer omits copying the CDC). Full outputs remain available for user review.
