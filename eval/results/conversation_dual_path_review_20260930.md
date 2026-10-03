> Historical evaluation evidence/protocol. Settings, results and instructions refer to the dated run below; use [current task guidance](../../docs/README.md) for today's implementation and verification.

# Conversational retrieval change: before/after review (2026-09-30)

The production Oracle index and department-scoped search were held fixed. Baseline code was commit `928fce0`; candidate conversation code was mounted read-only into an ephemeral app container. No index or production container was changed during this comparison. The 21 frozen cases include genuine pronoun follow-ups, topic switches, switch-backs, and the observed CO-OP credit failure. Raw per-case rankings are in the adjacent `conversation_dual_path_before_20260930.json` and `conversation_dual_path_after_20260930.json` files.

| Retrieval measure | Before | After |
| --- | ---: | ---: |
| Expected evidence in top 7 | 21/21 | 21/21 |
| Expected evidence at rank 1 | 11/21 | 13/21 |
| Exact standalone parity for independent questions | 9/9 | 9/9 |

Only two evidence ranks changed: `credits-after-application` and its no-punctuation variant moved from rank 5 to rank 1. The other 19 cases kept their prior evidence rank, including the mentorship sign-up, CO-OP duration, letter, and switch-back follow-ups. A first broad candidate made mentorship sign-up fall from rank 1 to rank 5 and was discarded before this final comparison.

Limited live answer checks were reviewed manually, not scored by an LLM judge:

| Case | Before | After |
| --- | --- | --- |
| “Does CO-OP count for credits?” after “How can I get a CO-OP internship?” | Production interaction 398 answered how to apply instead of addressing credits. | Answered that FEAA 500 is 3-credit Pass/Fail and the department decides degree/elective treatment; cited CO-OP policy. |
| “Does it count for credits?” after a CO-OP explanation | Mixed internship billing/eligibility with the CO-OP rule and asked the student to name CO-OP again. | Resolved “it” to CO-OP and answered only the CO-OP credit rule; cited CO-OP policy. |
| “Where do I sign up?” after switching from CO-OP to mentorship | Correctly directed the student to MentorPlus+/CDC sign-up. | Same correct answer and citations. |
| “How long is it?” after a CO-OP explanation | Correctly answered minimum six months. | Same correct answer and citation. |

The production synthesis evidence/context/threshold gate passed 75/75 with the candidate code. Focused unit tests passed 65/65. This is a targeted conversational regression result, **not** an estimate of overall student-answer accuracy. The change keeps one Gemini generation call per answered question; a substantive ambiguous question may incur one additional local retrieval search.
