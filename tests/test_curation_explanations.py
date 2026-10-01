from copy import deepcopy

from msfea_bot.curation.explanations import explain_regression


def test_legacy_failure_is_explained_without_changing_its_result() -> None:
    recorded = {"newly_lost_previously_passing": ["followup-letter-location"],
                "new_premise_regressions": [], "golden_baseline_failures": ["unrelated"]}
    original = deepcopy(recorded)
    explained = explain_regression(recorded)
    lost = explained["lost_cases"][0]
    assert lost["question"] == "Where do I get it?"
    assert "letter" in lost["history"][0]["content"]
    assert "letter request form" in lost["expected_answer"]
    assert lost["source_section"] == "Requesting a Letter or Convention de Stage"
    assert lost["diagnostic_origin"] == "test_catalog"
    assert "before_sources" not in lost
    assert explained["newly_lost_previously_passing"] == original["newly_lost_previously_passing"]
    assert recorded == original


def test_recorded_expectation_and_passages_take_precedence_over_catalog() -> None:
    explained = explain_regression({
        "newly_lost_previously_passing": ["followup-letter-location"],
        "lost_cases": [{"id": "followup-letter-location", "expected_answer": "Recorded policy.",
                        "before_sources": [{"text": "Recorded evidence."}]}],
    })
    lost = explained["lost_cases"][0]
    assert lost["expected_answer"] == "Recorded policy."
    assert lost["before_sources"] == [{"text": "Recorded evidence."}]
    assert lost["question"] == "Where do I get it?"


def test_unknown_historical_case_does_not_invent_a_question_or_source() -> None:
    explained = explain_regression({"newly_lost_previously_passing": ["removed-test"]})
    assert explained["lost_cases"] == [{"id": "removed-test", "diagnostic_origin": "test_catalog"}]


def test_passing_result_does_not_gain_a_failure() -> None:
    assert explain_regression({"newly_lost_previously_passing": []})["lost_cases"] == []
