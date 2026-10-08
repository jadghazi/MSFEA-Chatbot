"""Process-stage constraints apply across topics, not selected test questions."""

import pytest

from msfea_bot.retrieval.scope import excluded_process_stages, requires_later_outcome_evidence


@pytest.mark.parametrize("question", [
    "Will I get hired after the workshop?",
    "Does the employer retain employees after the work term ends?",
    "Is employment guaranteed upon completion of training?",
    "Will they offer a permanent job once we finish?",
    "Will finishing the exchange term guarantee permanent employment?",
    "Does completing a paid training program mean they will hire me?",
    "Will finishing the exchange term mean the employer hires me permanently?",
    "Does completing training mean the company retains employees?",
])
def test_later_employment_excludes_entry_only_facts(question: str) -> None:
    assert excluded_process_stages(question) == ("entry",)


@pytest.mark.parametrize("question", [
    "Will I get hired after applying?",
    "Is a placement guaranteed after being accepted?",
    "Will I get a job after completing my application?",
    "Will I get a job after we're accepted to the workshop?",
    "After graduating, how do I apply for a job?",
    "How much does the workshop cost?",
    "Can I work before finishing training?",
    "What happens afterwards?",
])
def test_entry_questions_and_unclear_stages_keep_evidence(question: str) -> None:
    assert excluded_process_stages(question) == ()


def test_outcome_gate_does_not_block_documented_general_help() -> None:
    assert requires_later_outcome_evidence("Will I get hired after the workshop?")
    assert requires_later_outcome_evidence("Do they promise permanent employment after training?")
    assert not requires_later_outcome_evidence("What career help is available for employment after graduation?")
    assert not requires_later_outcome_evidence("Will I get a placement after applying?")


def test_future_assistance_is_distinct_from_a_promised_outcome() -> None:
    for question in ("Will the center help me find a job after the workshop?",
                     "Will the advisor support my job search after training?",
                     "Will the service help me get hired after graduation?"):
        assert excluded_process_stages(question) == ("entry",)
        assert not requires_later_outcome_evidence(question)


def test_assistance_word_does_not_bypass_explicit_outcome_claims() -> None:
    for question in ("Will the center help guarantee a job after training?",
                     "Will they hire me and help with housing after the workshop?",
                     "Will support definitely mean employment after training?"):
        assert requires_later_outcome_evidence(question)
