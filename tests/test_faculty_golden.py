"""The faculty evaluation set preserves workbook identity and resolved policy."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


CASES = Path(__file__).resolve().parents[1] / "eval/faculty_questions_golden.jsonl"


def _cases() -> list[dict[str, object]]:
    return [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines()]


def test_all_reviewed_workbook_rows_are_present() -> None:
    cases = _cases()
    assert len(cases) == 205
    assert len({case["id"] for case in cases}) == 205
    assert sum(case["primary_workbook_case"] is True for case in cases) == 177
    locations = {(case["source_sheet"], case["question_cell"]) for case in cases}
    assert len(locations) == 177
    assert sum(any(case["shared_scope"] for case in cases
                   if (case["source_sheet"], case["question_cell"]) == location)
               for location in locations) == 156
    assert all(case["question"] and case["expected_answer_or_behavior"]
               and case["source_doc_candidates"] for case in cases)


def test_policy_sensitive_shared_questions_cover_each_department() -> None:
    cases = _cases()
    departments = {"ece", "mech", "chem", "iem", "cee"}
    for workbook_id in ("GEN-04", "GEN-05", "GEN-06", "GEN-07", "GEN-08", "GEN-10", "GEN-11"):
        selected = [case for case in cases if case["workbook_id"] == workbook_id]
        assert {case["department"] for case in selected} == departments
        assert len({case["question"] for case in selected}) == 1
    assert Counter(case["department"] for case in cases) == {
        "ece": 60, "mech": 38, "chem": 38, "iem": 34, "cee": 35,
    }


def test_resolved_decisions_replace_obsolete_workbook_expectations() -> None:
    cases = {case["id"]: case for case in _cases()}
    assert "hands-on engineering" in str(cases["faculty-008-mech"]["expected_answer_or_behavior"])
    assert "selected companies" in str(cases["faculty-008-cee"]["expected_answer_or_behavior"])
    assert "8–15-page" in str(cases["faculty-054-cee"]["expected_answer_or_behavior"])
    assert "not guaranteed" in str(cases["faculty-034-ece"]["expected_answer_or_behavior"])
    assert "do not invent a universal Final VOP" in str(
        cases["faculty-148-iem"]["expected_answer_or_behavior"]
    )
