"""Deterministic same-chat contextualization (no DB and no LLM)."""

from msfea_bot.generation.conversation import (
    ConversationMessage,
    bounded_history,
    build_retrieval_query,
    contextual_question,
    format_prompt_history,
    is_contextual_followup,
    frame_confirmation,
    answer_task,
    needs_condition_focus,
    retrieval_plan,
)


def _history() -> list[ConversationMessage]:
    return [
        ConversationMessage("user", "Is a support letter available from the CDC?"),
        ConversationMessage("assistant", "Yes. Request it from the CDC."),
    ]


def test_pronoun_question_uses_history_for_retrieval() -> None:
    query = build_retrieval_query("Where do I get it?", _history())
    assert "support letter" in query
    assert "Where do I get support letter?" == query
    assert "Earlier student" not in query


def test_independent_topic_switch_omits_history() -> None:
    question = "What GPA do I need for CO-OP?"
    assert build_retrieval_query(question, _history()) == question
    assert format_prompt_history(question, _history()) == ""


def test_named_what_about_topic_switch_omits_history() -> None:
    for question in ("What about CO-OP?", "what about Career+"):
        assert not is_contextual_followup(question, _history())
        assert build_retrieval_query(question, _history()) == question
        assert format_prompt_history(question, _history()) == ""


def test_referential_what_about_still_uses_history_for_retrieval() -> None:
    query = build_retrieval_query("What about that?", _history())
    assert "support letter" in query


def test_what_about_cue_answers_the_option_without_unasked_paperwork() -> None:
    cue = answer_task("what about the 6+2", _history())
    assert cue.startswith("Alternative or missing component:")
    assert "correct it explicitly" in cue
    assert "Do not discuss reports" in cue


def test_only_cue_decides_whether_the_exact_plan_is_sufficient() -> None:
    cue = answer_task("Can I do 6 weeks of internship only?", [])
    assert cue.startswith("Plan sufficiency:")
    assert "otherwise start with No" in cue
    assert "partial activity is allowed" in cue


def test_short_elliptical_question_uses_history() -> None:
    assert is_contextual_followup("Where do I submit?", _history())


def test_no_history_never_claims_a_followup() -> None:
    assert not is_contextual_followup("Where do I get it?", [])


def test_history_is_hard_bounded() -> None:
    history = [ConversationMessage("user", str(i) * 1500) for i in range(10)]
    bounded = bounded_history(history)
    assert len(bounded) == 8
    assert all(len(message.content) == 1200 for message in bounded)
    assert bounded[0].content.startswith("2")


def test_short_followups_keep_program_without_exact_reference_words() -> None:
    history = [ConversationMessage("user", "Tell me about CO-OP"),
               ConversationMessage("assistant", "CO-OP is an optional program.")]
    for question in ("Can I get paid?", "Do I need approval?", "What about the deadline?"):
        assert is_contextual_followup(question, history)
        assert "CO-OP" in build_retrieval_query(question, history)
    assert not is_contextual_followup("What about Career+?", history)


def test_bare_duration_question_can_use_recent_report_context() -> None:
    history = [ConversationMessage("user", "How long is the final training report?"),
               ConversationMessage("assistant", "Its length is set in the final report requirements.")]
    assert is_contextual_followup("How long should EECE500 be", history)
    assert "final training report" in build_retrieval_query("How long should EECE500 be", history)
    assert "final training report" in contextual_question("How long should EECE500 be", history)


def test_bare_course_code_duration_query_names_course_duration() -> None:
    assert build_retrieval_query("How long should the EECE500 be", []).startswith(
        "Course duration and training length:"
    )


def test_assistant_text_can_resolve_reference_but_is_not_policy_evidence() -> None:
    history = _history()
    query = build_retrieval_query("What does that mean?", history)
    prompt_history = format_prompt_history("What does that mean?", history)
    assert query == "What does support letter mean?"
    assert "ASSISTANT: Yes. Request it from the CDC." in prompt_history
    assert "Earlier assistant wording" not in query


def test_complete_confirmation_does_not_reuse_previous_assistant_guess() -> None:
    history = [ConversationMessage("user", "Can I do six weeks only?"),
               ConversationMessage("assistant", "You need four more company weeks.")]
    prompt_history = format_prompt_history(
        "so I need two weeks research after the six weeks at a company?", history
    )
    assert "USER: Can I do six weeks only?" in prompt_history
    assert "four more company weeks" not in prompt_history


def test_confirmation_framing_preserves_the_students_claim() -> None:
    question = "so two more weeks at the company instead?"
    framed = frame_confirmation(question, _history())
    assert framed == "Is my understanding of our conversation correct: two more weeks at the company instead?"
    assert "support letter" not in framed
    assert build_retrieval_query(question, _history()).startswith(
        "so two more weeks at the company instead"
    )


def test_explicit_subjects_and_relative_that_start_a_new_topic() -> None:
    history = [ConversationMessage("user", "What GPA do I need for CO-OP?")]
    for question in (
        "What is mentorship?",
        "What about internship?",
        "Can I apply for an internship that starts in June?",
        "Where can I get the internship support letter again?",
    ):
        assert not is_contextual_followup(question, history)
        assert build_retrieval_query(question, history) == question
        assert format_prompt_history(question, history) == ""


def test_detailed_question_does_not_inherit_unrelated_salary_topic() -> None:
    history = [ConversationMessage("user", "Do I need a salary for the internship?")]
    question = (
        "can you give me the link for that letter i forgot the name that the "
        "company needs to make sure i need the internship"
    )
    assert retrieval_plan(question, history).query == question
    assert format_prompt_history(question, history) == ""


def test_followup_uses_latest_substantive_subject_after_switches() -> None:
    history = [
        ConversationMessage("user", "What GPA do I need for CO-OP?"),
        ConversationMessage("assistant", "CO-OP needs a GPA of 3.3."),
        ConversationMessage("user", "What services does the mentorship program offer?"),
        ConversationMessage("assistant", "MentorPlus+ connects students with alumni."),
    ]
    assert build_retrieval_query("Is it mandatory?", history) == (
        "Is mentorship program mandatory?"
    )
    assert contextual_question("Is it mandatory?", history) == (
        "Is mentorship program mandatory?"
    )
    assert "CO-OP" not in format_prompt_history("Is it mandatory?", history)
    switched_back = history + [
        ConversationMessage("user", "What GPA do I need for CO-OP?"),
        ConversationMessage("assistant", "The minimum is 3.3."),
    ]
    assert build_retrieval_query("Is it mandatory?", switched_back) == (
        "Is CO-OP mandatory?"
    )


def test_repeated_ellipsis_keeps_last_substantive_subject() -> None:
    history = [
        ConversationMessage("user", "Is a support letter available from the CDC?"),
        ConversationMessage("assistant", "Yes."),
        ConversationMessage("user", "Where do I get it?"),
        ConversationMessage("assistant", "Use the CDC form."),
    ]
    assert build_retrieval_query("How long is it?", history) == (
        "How long is support letter?"
    )


def test_substantive_ambiguous_followup_keeps_both_retrieval_paths() -> None:
    history = [ConversationMessage("user", "Can I do 6 weeks of internship only?")]
    question = "so I need two weeks of research after six at a company?"
    plan = retrieval_plan(question, history)
    assert plan.standalone_query == question
    assert "research" in plan.query
    assert "internship" in plan.query
    assert "Earlier student" not in plan.query


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
    assert needs_condition_focus("Can I do eight weeks while enrolled in a class?")
    assert not needs_condition_focus("Are six weeks enough for the 6+2 option?")
    assert not needs_condition_focus("What happens while I take another course?")
