# Follow-up answer-quality evaluation

**Date:** 2026-09-12

**Selected production model:** `gemini-flash-lite-latest` (unchanged)

The frozen set contains seven cases: the reported initial question, two elliptical
follow-ups with an incorrect earlier assistant answer, a paraphrase, a confirmation,
the separate summer-course exception, and an unsupported request for rationale.

| Run | Deterministic answer checks | Required evidence hits |
| --- | ---: | ---: |
| Baseline | 1/7 | 6/11 |
| Selected implementation | 7/7 | 11/11 |

The checks require a direct `No` for an insufficient six-week-only plan, the two
faculty-research weeks in ordinary 6+2 answers, no unasked ten-week rule or
procedures, no `For ECE students` prefix, citations and disclaimer, correct handling
of the summer-course exception, and refusal when the sources do not explain the
policy rationale.

Manual review of `flash_lite_selected.jsonl` confirms that all seven answers match
the expected behavior. In the reported follow-up, the answer explains the 6+2
option itself and does not repeat the earlier ten-week mistake or switch to progress
report instructions.

`gemini-3.6-flash` at low reasoning was tested as an experiment and rejected as the
pilot default after observing a 5 RPM free-tier limit and higher latency. It is not
part of the selected change. Each student turn still uses one Flash Lite generation
request.
