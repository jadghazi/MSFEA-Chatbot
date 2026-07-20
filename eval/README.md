# Evaluation harness (Phase 2)

**PLACEHOLDER** — filled in Phase 2 (CLAUDE.md §4, §5.2). It is built *before*
the bot so every later change is measurable.

Will contain:
- `golden_set.jsonl` — one record per question with fields:
  `question`, `expected_answer_or_behavior`, `source_doc`, `should_refuse`.
- A runner reporting the **two separate metrics**:
  - **Retrieval:** is the correct chunk in the top-k? (recall@k / hit rate)
  - **Answer:** is the answer correct and grounded, and does it refuse when it
    should?

Built with placeholder questions first, then real student questions swapped in.
Wired into CI so a regression can't merge silently.
