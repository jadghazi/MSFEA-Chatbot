"""Read-only explanations for recorded checks, including older test results."""

from __future__ import annotations

from typing import Any

from eval.loader import load_golden_set


def explain_regression(details: dict[str, Any]) -> dict[str, Any]:
    """Attach readable expectations without changing recorded outcomes or rerunning tests."""
    from msfea_bot.curation.validation import _jsonl_cases

    cases: dict[str, dict[str, Any]] = {
        item.id: {
            "id": item.id, "question": item.question,
            "history": [message.__dict__ for message in item.history],
            "expected_answer": item.expected_answer_or_behavior,
            "source_doc": item.source_doc, "source_section": item.source_section,
            "evidence": item.evidence,
        } for item in load_golden_set()
    }
    for name in ("synthesis_set.jsonl", "followup_set.jsonl", "scope_regression_set.jsonl"):
        for case in _jsonl_cases(name):
            cases.setdefault(case["id"], {
                "id": case["id"], "question": case["question"],
                "history": case.get("history", []),
                "expected_answer": case.get("expected_answer_or_behavior", ""),
                "evidence": case.get("evidence_all", []),
            })
    recorded = {item["id"]: item for item in details.get("lost_cases", [])}
    lost_ids = list(dict.fromkeys([
        *details.get("newly_lost_previously_passing", []),
        *details.get("new_premise_regressions", []), *recorded,
    ]))
    return {**details, "lost_cases": [
        {
            **cases.get(case_id, {"id": case_id}), **recorded.get(case_id, {}),
            "diagnostic_origin": "recorded" if case_id in recorded else "test_catalog",
        } for case_id in lost_ids
    ]}
