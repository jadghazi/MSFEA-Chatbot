# Evaluation harness (Phase 2)

The golden set + metrics, built **before** the bot so every later change is
measurable (CLAUDE.md §4). Grading methodology is defined in
[ADR-0002](../docs/decisions/0002-evaluation-methodology.md).

## Contents

- `golden_set.jsonl` — one case per line: `question`,
  `expected_answer_or_behavior`, `source_doc`, `should_refuse`, plus helpers
  (`id`, `source_section`, `tags`, `is_synthetic`). Seeded from the real CDC-KB
  FAQs plus refusal cases; `is_synthetic: true` marks questions we predicted
  (placeholders until real student questions arrive).
- `loader.py` — parse + validate the golden set (`load_golden_set()`).
- `metrics.py` — the two metric families:
  - **Retrieval:** `recall_at_k`, `hit_rate_at_k`.
  - **Answer, Layer 1 (deterministic):** `refusal_is_correct`, `citation_present`,
    `disclaimer_present`.
- `run.py` — `python -m eval.run` summarizes the set and reports metric status.

## What is wired vs. pending

| Piece | Status |
|-------|--------|
| Golden set + loader | Ready |
| Answer Layer 1 (deterministic checks) | Ready, unit-tested |
| Retrieval recall@k | Function ready; needs a retriever (Phase 4) to run end-to-end |
| Answer Layer 2 (LLM-judge) | Pending the LLM provider (Phase 6) |
| Answer Layer 3 (human calibration) | Pending real answers |

## Run it

```bash
python -m eval.run     # summarize the golden set
pytest                 # run metric + golden-set tests
```

Real student questions (batch 2) will be swapped in / added to `golden_set.jsonl`
as they arrive; the harness itself does not change.
