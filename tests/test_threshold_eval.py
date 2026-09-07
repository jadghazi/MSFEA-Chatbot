"""Integrity tests for the retrieval-only similarity calibration set."""

from eval.threshold_eval import load_threshold_set


def test_threshold_set_has_unique_valid_and_offtopic_cases() -> None:
    cases = load_threshold_set()
    assert len(cases) == 50
    assert len({case.id for case in cases}) == len(cases)
    assert any(case.should_pass_threshold for case in cases)
    assert any(not case.should_pass_threshold for case in cases)
