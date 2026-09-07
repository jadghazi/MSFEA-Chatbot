"""Deterministic same-chat contextualization (no DB and no LLM)."""

from msfea_bot.generation.conversation import (
    ConversationMessage,
    bounded_history,
    build_retrieval_query,
    format_prompt_history,
    is_contextual_followup,
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
