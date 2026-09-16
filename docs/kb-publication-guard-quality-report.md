# KB publication guard — independent quality review

Date: 2026-09-16

Implementation stage: Step 6 of `kb-publication-guard-plan.md`

Candidate base commit: `2e3c4f505eb2d5cf7416650217a91e01c2728032`

This review used the disposable local PostgreSQL service and the configured
production provider/model settings. It did not connect to, migrate, rebuild, restart,
or deploy Oracle.

## Automated gates

| Gate | Result |
|---|---|
| Ruff (`src tests eval`) | Pass |
| Strict mypy (`src eval`) | Pass, 48 source files |
| Widget submission tests | Pass, 3/3 |
| Python tests | Pass, 260/260; two upstream TestClient/AnyIO deprecation warnings |
| Clean normal ingestion | Pass, 210 chunks |
| Golden context recall at production depth | 67/68 (98.5%); floor 90% |
| Similarity threshold | 109/109 valid queries pass; lowest 0.6329 |
| Off-topic pre-LLM blocking | 11/20 (55%) |
| Synthesis/follow-up/scope all-premise gate | 27/27 |
| Frozen publication-guard retrieval sample | 9/9 answerable cases |
| Conflict-review candidate evidence | 7/7 |
| Known conflict-heuristic false-positive fixtures | 2, reported rather than hidden |

The first Step 6 run found a newly lost golden evidence case even though aggregate
recall remained above the floor. The failure was traced to RRF candidate crowding for
a numeric rule-application question. Increasing prompt depth would have exposed more
context to every answer, so it was not used. Instead, numeric decision/application
questions now widen only the internal retrieval candidate pool from 20 to 40 while
still returning the configured top seven chunks. A complete before/after sweep showed
one recovered golden case and zero losses across golden, synthesis, follow-up, and
scope sets. The final 67/68 exactly restores the frozen baseline; the remaining
`internship-vs-coop` miss is the same documented baseline miss.

## Per-department preservation

| Applicability | Result |
|---|---|
| CEE | 1/1 |
| CHEM | 1/1 |
| ECE | 2/2 |
| IEM | 1/1 |
| MECH | 1/1 |
| Unknown department | 3/3 |

The candidate-validation integration test separately verifies that an ECE-only draft
is retrieved for ECE and for no-department conditional guidance, but for none of the
other four known departments. Every candidate window carries the reviewed scope.

## Live answer review

The frozen ten-case preservation set ran once with Gemini
`gemini-flash-lite-latest`, temperature `0`, seed `42`, maximum output `1024`, top-k
`7`, threshold `0.60`, and the pinned BGE embedding revision. It made exactly ten
provider calls: 27,559 input tokens, 752 output tokens, and 965–22,084 ms provider
latency (median 1,482 ms). The long maximum was one provider response; no retry added
another generation call.

| Case | Review |
|---|---|
| ECE 6+2 | Pass — components plus approval/documentation retained |
| MECH split | Pass — direct scoped rejection |
| CEE split | Pass — civil/construction condition retained |
| IEM presentation | Pass — department exception retained |
| CHEM/general credits | Pass — 90-credit general rule, no invented exception |
| Unknown-department split | Pass — conditional CEE/MECH/ECE/CHEM guidance and department question; fixes the frozen baseline refusal |
| Corrective 6+2 follow-up | Known completeness limitation — correct six company plus two research weeks, but this stochastic run again omitted approval/documentation |
| Internship/CO-OP comparison | Pass — duration, pay, optional status and FEAA 500 waiver |
| IAESTE topic switch | Pass — correct new topic and contact |
| Undocumented rationale | Pass — grounded refusal and ECE escalation, no invented rationale |

Every answered case had source citations; the refusal had none. The API/widget adds
the standard visible AI disclaimer independently of this experiment harness. No new
factual, applicability, refusal, follow-up, citation, tone, or verbosity regression
was observed. The 6+2 follow-up omission is the same explicit limitation in the
frozen baseline and remains visible rather than being averaged away. It is not used
to certify automatic publication or policy truth.

## Reproducibility artifacts

- `eval/results/synthesis/step6-publication-guard.manifest.json`
  - SHA-256 `0716810c7a93202aec6f474651c715610fafeec047ec00abb3d7ef7d2a4cf3a2`
- `eval/results/synthesis/step6-publication-guard.jsonl`
  - SHA-256 `63175deb5bcfcbd03c635cf4fae22b014b0a821195000e60d2b0d072c82f5226`

The raw JSONL retains each retrieval result, rendered prompt, provider call metadata,
parsed answer, citations and refusal state. This engineering review does not replace
CDC source-owner approval for any future draft.
