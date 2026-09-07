# Evaluation harness (Phase 2)

The golden set + metrics, built **before** the bot so every later change is
measurable (CLAUDE.md §4). Grading methodology is defined in
[ADR-0002](../docs/decisions/0002-evaluation-methodology.md).

## Contents

- `golden_set.jsonl` — one case per line: `question`,
  `expected_answer_or_behavior`, `source_doc`, `should_refuse`, plus helpers
  (`id`, `source_section`, `history`, `tags`, `is_synthetic`). `history` is optional
  and holds bounded earlier turns for follow-up/topic-switch cases. Seeded from the real CDC-KB
  FAQs plus refusal cases; `is_synthetic: true` marks questions we predicted
  (placeholders until real student questions arrive).
  It also includes intent-aware conversational cases for confirmations, topic
  switches, and applying documented thresholds to facts stated by a student.
- `loader.py` — parse + validate the golden set (`load_golden_set()`).
- `metrics.py` — the two metric families:
  - **Retrieval:** `recall_at_k`, `hit_rate_at_k`.
  - **Answer, Layer 1 (deterministic):** `refusal_is_correct`, `citation_present`,
    `disclaimer_present`.
- `run.py` — `python -m eval.run` summarizes the set and reports metric status.
- `threshold_set.jsonl` + `threshold_eval.py` — retrieval-only calibration for the
  pre-LLM similarity gate. It includes terse/misspelled valid questions and varied
  off-topic prompts, runs without an API key, and is gated in CI (ADR-0020).

## What is wired vs. pending

| Piece | Status |
|-------|--------|
| Golden set + loader | Ready |
| Answer Layer 1 (deterministic checks) | Ready, unit-tested (`python -m eval.answer_eval`) |
| Retrieval recall@k + context-recall | Ready (`python -m eval.retrieval_eval`); **gated in CI** on a context-recall floor |
| Similarity-threshold calibration | Ready (`python -m eval.threshold_eval`); **gated in CI**, no LLM calls |
| Answer Layer 2 (LLM-judge: faithfulness/groundedness) | **Not built.** No blocker — the provider has existed since Phase 3. This is the one real gap: nothing currently checks that an answer's claims are supported by the retrieved context |
| Answer Layer 3 (human calibration) | Pending real answers |

The answer eval is deliberately **not** in CI: it calls the live LLM, so it needs an
API key and burns free-tier quota. Run it locally before/after a change that could
affect generation.

## Run it

```bash
python -m eval.run     # summarize the golden set
python -m eval.threshold_eval  # verify the pre-LLM 0.60 gate; no Gemini usage
pytest                 # run metric + golden-set tests
```

Real student questions (batch 2) will be swapped in / added to `golden_set.jsonl`
as they arrive; the harness itself does not change.
