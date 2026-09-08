"""Deterministic same-chat contextualization (no DB and no LLM)."""

from msfea_bot.generation.conversation import (
    ConversationMessage,
    bounded_history,
    build_retrieval_query,
    format_prompt_history,
    is_contextual_followup,
    frame_confirmation,
    answer_task,
    needs_condition_focus,
)


def _history() -> list[ConversationMessage]:
    return [
        ConversationMessage("user", "Is a support letter available from the CDC?"),
        ConversationMessage("assistant", "Yes. Request it from the CDC."),
    ]


def test_pronoun_question_uses_history_for_retrieval() -> None:
    query = build_retrieval_query("Where do I get it?", _history())
    assert "support letter" in query
    assert "Where do I get it?" in query


def test_independent_topic_switch_omits_history() -> None:
    question = "What GPA do I need for CO-OP?"
    assert build_retrieval_query(question, _history()) == question
    assert format_prompt_history(question, _history()) == ""


def test_explicit_continuation_uses_history() -> None:
    assert is_contextual_followup("What about CO-OP?", _history())


def test_short_elliptical_question_uses_history() -> None:
    assert is_contextual_followup("Where do I submit?", _history())


def test_no_history_never_claims_a_followup() -> None:
    assert not is_contextual_followup("Where do I get it?", [])


def test_history_is_hard_bounded() -> None:
    history = [ConversationMessage("user", str(i) * 1500) for i in range(7)]
    bounded = bounded_history(history)
    assert len(bounded) == 4
    assert all(len(message.content) == 1200 for message in bounded)
    assert bounded[0].content.startswith("3")


def test_assistant_text_is_prompt_context_but_not_retrieval_text() -> None:
    history = _history()
    query = build_retrieval_query("What does that mean?", history)
    prompt_history = format_prompt_history("What does that mean?", history)
    assert "Request it from the CDC" not in query
    assert "ASSISTANT: Yes. Request it from the CDC." in prompt_history


def test_confirmation_framing_preserves_the_students_claim() -> None:
    question = "so two more weeks at the company instead?"
    framed = frame_confirmation(question, _history())
    assert framed == "Is my understanding of our conversation correct: two more weeks at the company instead?"
    assert "support letter" not in framed
    assert build_retrieval_query(question, _history()).endswith(question)


def test_complete_questions_are_never_rewritten_as_confirmations() -> None:
    for question in ("so why is that required?", "so how do I submit?", "so can I apply?",
                     "Why did the department choose this?", "What is the deadline?"):
        assert frame_confirmation(question, _history()) == question
    assert frame_confirmation("so two weeks", []) == "so two weeks"


def test_definition_cue_does_not_shorten_requested_checklists() -> None:
    assert answer_task("What is a placement?", []).startswith("Definition:")
    for question in ("Explain the required deliverables", "What is the list of forms?",
                     "Explain how to apply"):
        assert not answer_task(question, []).startswith("Definition:")


def test_decision_cue_keeps_source_conditions_attached() -> None:
    cue = answer_task("Am I eligible if I am also taking a course?", [])
    assert "every circumstance" in cue
    assert "did not state" in cue
    assert "names an option or arrangement" in cue


def test_named_arrangement_completion_excludes_alternative_paths() -> None:
    cue = answer_task("Are six weeks enough for the 6+2 option?", [])
    assert cue.startswith("Named arrangement completion:")
    assert "Do not substitute" in cue
    conditional = answer_task("I am also taking a course. Is 6+2 enough?", [])
    assert conditional.startswith("Decision:")


def test_only_decisions_with_explicit_extra_conditions_get_condition_focus() -> None:
    assert needs_condition_focus("I am also taking a course. Is 6+2 enough?")
    assert needs_condition_focus("Am I eligible while taking another course?")
    assert not needs_condition_focus("Are six weeks enough for the 6+2 option?")
    assert not needs_condition_focus("What happens while I take another course?")
