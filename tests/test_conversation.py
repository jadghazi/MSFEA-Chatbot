"""Deterministic same-chat contextualization (no DB and no LLM)."""

import pytest

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
    is_overview_request,
    unresolved_reference,
    attribute_search,
)


def _history() -> list[ConversationMessage]:
    return [
        ConversationMessage("user", "Is a support letter available from the CDC?"),
        ConversationMessage("assistant", "Yes. Request it from the CDC."),
    ]


@pytest.mark.parametrize("prefix", ["", "So ", "Okay, ", "Well, ", "Hey, ", "OK, so "])
@pytest.mark.parametrize("question", ["What can you help me with?", "What can you do?",
                                      "What do you offer?"])
def test_capability_orientation_accepts_conversational_prefixes(prefix: str, question: str) -> None:
    assert retrieval_plan(prefix + question, _history()).query == (
        "What services and career support does the CDC offer?"
    )


def test_capability_prefix_does_not_override_a_named_request() -> None:
    question = "So what can you help me with regarding a support letter?"
    assert retrieval_plan(question, []).query == question


def test_pronoun_question_uses_history_for_retrieval() -> None:
    query = build_retrieval_query("Where do I get it?", _history())
    assert "support letter" in query
    assert "Where do I get support letter?" == query
    assert "Earlier student" not in query


def test_independent_topic_switch_omits_history() -> None:
    question = "What GPA do I need for CO-OP?"
    assert build_retrieval_query(question, _history()) == question
    assert format_prompt_history(question, _history()) == ""


def test_bare_document_referent_precedes_provider_acronym() -> None:
    history = [ConversationMessage(
        "user", "The employer asked for a letter proving my internship is required. "
        "Can the CDC provide one?",
    )]
    assert build_retrieval_query("Where do I get it?", history) == "Where do I get letter?"
    assert contextual_question("Where do I get it?", history) == "Where do I get letter?"


def test_named_what_about_topic_switch_omits_history() -> None:
    for question in ("What about CO-OP?", "what about Career+"):
        assert not is_contextual_followup(question, _history())
        assert build_retrieval_query(question, _history()) == question
        assert format_prompt_history(question, _history()) == ""


def test_named_subject_after_and_overrides_prior_topic() -> None:
    prior = [ConversationMessage("user", "Is CO-OP paid?"),
             ConversationMessage("assistant", "Yes, CO-OP work terms are paid.")]
    question = "And does the internship count for credit?"
    assert not is_contextual_followup(question, prior)
    assert retrieval_plan(question, prior).query == question
    assert format_prompt_history(question, prior) == ""


def test_switch_back_becomes_anchor_for_next_short_followup() -> None:
    prior = [
        ConversationMessage("user", "What is the internship?"),
        ConversationMessage("assistant", "It is the required training course."),
        ConversationMessage("user", "What is CO-OP?"),
        ConversationMessage("assistant", "It is a paid work program."),
        ConversationMessage("user", "Back to the internship: what is it for?"),
        ConversationMessage("assistant", "It applies classroom skills."),
    ]
    assert retrieval_plan("Back to the internship: how long must it last?", prior).query == (
        "Back to the internship: how long must it last?"
    )
    query = retrieval_plan("And how long is it?", prior).query
    assert "internship" in query.lower()
    assert "CO-OP" not in query


def test_hyphenated_acronym_is_not_truncated_in_followup() -> None:
    prior = [ConversationMessage("user", "How do I apply to CO-OP?"),
             ConversationMessage("assistant", "Apply through the CDC.")]
    assert "CO-OP" in retrieval_plan("What about the deadline?", prior).query


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


def test_short_complete_question_keeps_literal_search_after_related_history() -> None:
    history = [
        ConversationMessage("user", "How can I get a co-op internship?"),
        ConversationMessage("assistant", "Please use the CO-OP application process."),
    ]
    question = "Does co-op count for credits?"
    plan = retrieval_plan(question, history)
    assert plan.standalone_query == question
    assert "co-op internship" in plan.query
    assert contextual_question(question, history) == question


def test_elliptical_question_still_uses_resolved_subject() -> None:
    plan = retrieval_plan("How long is it?", [ConversationMessage("user", "What is CO-OP?")])
    assert plan.query == "How long is CO-OP?"
    assert plan.standalone_query is None


def test_referential_dual_search_uses_resolved_subject_in_answer_question() -> None:
    history = [ConversationMessage("user", "What is CO-OP?")]
    question = "Does it count for credits?"
    assert retrieval_plan(question, history).standalone_query == question
    assert contextual_question(question, history) == "Does CO-OP count for credits?"


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


def test_overview_intent_generalizes_across_subjects_without_overriding_decisions() -> None:
    for question in ("Tell me about housing", "Give me an overview of the exchange",
                     "Can you walk me through registration?", "What's the whole process?",
                     "Explain the program like I've never heard of it"):
        assert is_overview_request(question)
        assert answer_task(question, []).startswith("Topic overview:")
    for question in ("Is six weeks enough?", "Can I combine two placements?",
                     "What is the deadline?", "Explain how to submit the form"):
        assert not is_overview_request(question)
    assert not is_overview_request("what about the 6+2", _history())


def test_reference_without_subject_needs_clarification_but_named_questions_do_not() -> None:
    for question in ("How does this work?", "What about that?", "Is it required?"):
        assert unresolved_reference(question, [])
        assert not unresolved_reference(question, _history())
    for question in ("How does an internship work?", "Is CO-OP required?",
                     "How does this internship work?", "What about research?"):
        assert not unresolved_reference(question, [])


def test_attribute_followup_is_not_forced_into_an_alternative_plan_task() -> None:
    history = [ConversationMessage("user", "What is the exchange program?")]
    assert not answer_task("what about the fee?", history).startswith("Alternative")
    assert answer_task("what about the 6+2", history).startswith("Alternative")


def test_generic_deadline_after_overview_needs_a_document_referent() -> None:
    history = [ConversationMessage("user", "Tell me about registration")]
    assert answer_task("When is the deadline?", history).startswith("Clarification:")
    assert not answer_task("When is the deadline?", _history()).startswith("Clarification:")


def test_status_and_outcome_cues_do_not_treat_silence_as_permission_or_transfer_stages() -> None:
    assert answer_task("Do I need approval before enrolling?", []).startswith("Requirement status:")
    assert "absence of a listed prerequisite" in answer_task("Is membership required?", [])
    assert "ask which" in answer_task("is that mandatory?", _history())
    assert not answer_task("What are the required forms?", []).startswith("Requirement status:")
    assert not answer_task("Why is that required?", []).startswith("Requirement status:")


def test_singular_status_after_service_menu_needs_a_subject_without_policy_inference() -> None:
    history = [ConversationMessage("user", "What services does the center offer?"),
               ConversationMessage("assistant", "Placement, mentoring, and preparation.")]
    assert unresolved_reference("Is that mandatory?", history)
    assert unresolved_reference("Do I have to do that?", history)
    assert not unresolved_reference("Is mentoring mandatory?", history)
    assert not unresolved_reference("Is that mandatory?", _history())


def test_attributes_preserve_subject_across_several_followups() -> None:
    history = [ConversationMessage("user", "Tell me about the exchange program"),
               ConversationMessage("assistant", "A study exchange."),
               ConversationMessage("user", "what about the fee?"),
               ConversationMessage("assistant", "See the tuition information.")]
    for question in ("and the duration?", "who do I contact?", "and the cost?"):
        assert is_contextual_followup(question, history)
        assert attribute_search(question, history)[0] == "exchange program"
        assert "fee" not in retrieval_plan(question, history).query


def test_named_switches_override_discourse_markers_without_losing_pronouns() -> None:
    for question in ("Actually, what help is there for housing?",
                     "Instead, can you explain scholarships?",
                     "Now, how does enrollment work?"):
        assert not is_contextual_followup(question, _history())
        assert retrieval_plan(question, _history()).query == question
        assert not format_prompt_history(question, _history())
    assert is_contextual_followup("Actually, can it be shorter?", _history())


def test_comparative_retrieval_does_not_redefine_generation_intent() -> None:
    history = [ConversationMessage("user", "Tell me about workshops")]
    for question in ("Can it be shorter?", "Could it be longer?"):
        assert retrieval_plan(question, history).query == "How long is workshops?"
        assert contextual_question(question, history) == question.replace("it", "workshops")
        assert retrieval_plan("Actually, " + question.lower(), history).standalone_query is None
    assert retrieval_plan("Does that mean it can be shorter?", history).standalone_query is None


def test_quantity_task_generalizes_without_overriding_explicit_decisions() -> None:
    for question in ("How much time do I need?", "How long is the workshop?",
                     "How many pages should the document contain?", "Could it be shorter?"):
        assert answer_task(question, []).startswith("Quantity or range:")
    assert answer_task("Can I combine two placements?", []).startswith("Decision:")


def test_ordinal_part_reference_preserves_topic_and_attribute() -> None:
    history = [ConversationMessage("user", "How do exchange fees work?")]
    plan = retrieval_plan("Does the second part cost extra?", history)
    assert is_contextual_followup("Does the second part cost extra?", history)
    assert "exchange" in plan.query
    assert attribute_search("Does the second part cost extra?", history)[1][0] == "fee"
    assert plan.standalone_query is None


def test_bounds_preserve_latest_dimension_but_never_cross_topic_switches() -> None:
    history = [ConversationMessage("user", "Tell me about workshops"),
               ConversationMessage("user", "How long is it?"),
               ConversationMessage("assistant", "A purported number.")]
    question = "Is that a minimum or a maximum?"
    plan = retrieval_plan(question, history)
    assert "workshops duration" in plan.query
    assert "workshops duration" in contextual_question(question, history)
    assert plan.standalone_query is None
    history.append(ConversationMessage("user", "What is the exchange program?"))
    assert "duration" not in retrieval_plan(question, history).query
    history.append(ConversationMessage("user", "What about the cost?"))
    assert "exchange program cost" in retrieval_plan(question, history).query


def test_attribute_only_queries_use_subject_but_conditional_queries_keep_both_paths() -> None:
    history = [ConversationMessage("user", "Tell me about housing")]
    for question in ("What's the email for them?", "Can you send the link again?",
                     "And how much time would I need to set aside?"):
        plan = retrieval_plan(question, history)
        assert "housing" in plan.query
        assert plan.standalone_query is None
        assert attribute_search(question, history) is not None
    assert retrieval_plan("What is its fee if I leave early?", history).standalone_query
    assert retrieval_plan("Does it cost 200 dollars?", history).standalone_query


def test_registration_reference_after_menu_clarifies_without_picking_a_program() -> None:
    history = [ConversationMessage("user", "What can the center help me with?"),
               ConversationMessage("assistant", "Housing, exchanges, and workshops.")]
    for question in ("How do I sign up for it?", "How can I apply for that?"):
        assert unresolved_reference(question, history)
    assert not unresolved_reference("How do I sign up for housing?", history)
    assert not unresolved_reference("How do I sign up for them?", history)
    assert not unresolved_reference("How do I sign up for it?", _history())


def test_activity_permission_does_not_assume_a_quantified_completion_plan() -> None:
    for question in ("Could I do online training?", "Can I do a placement overseas?",
                     "Can I complete the ACME 500 course remotely?"):
        assert answer_task(question, []).startswith("Activity permission:")
    for question in ("Can I combine two activities?", "Can I do six weeks of practice?",
                     "Can I complete the 6+2 arrangement?"):
        assert answer_task(question, []).startswith("Decision:")


def test_rule_application_recognizes_other_actors_and_document_substitution() -> None:
    for question in ("Can practical work make up the rest of my requirement?",
                     "Could the lab count toward the certificate?",
                     "Can I submit the invoice instead of the receipt?"):
        cue = answer_task(question, [])
        assert cue.startswith("Decision:")
        assert "unstated exception scenarios" in cue


def test_referential_decision_checks_for_a_real_subject_before_applying_rules() -> None:
    cue = answer_task("Someone used this before. Can I do the same?", [])
    assert cue.startswith("Referential decision:")
    assert "include the clarifying question" in cue
    assert "without asking an unnecessary clarification" in answer_task("Can I do it?", _history())


def test_overview_before_details_does_not_expand_a_specific_attribute_question() -> None:
    assert is_overview_request("Could you explain the exchange before getting into special cases?")
    assert is_overview_request("What's the big picture for workshops?")
    assert not is_overview_request("Explain the fee before we get into details")


def test_attribute_task_covers_named_properties_and_topic_followups() -> None:
    history = [ConversationMessage("user", "Tell me about workshops")]
    for question in ("How much does membership cost?", "What's the email?",
                     "Can you send the link again?", "What is the workshop fee?"):
        assert answer_task(question, history).startswith("Requested attribute:")


def test_attribute_task_keeps_permission_overview_and_quantity_priorities() -> None:
    assert answer_task("Can I skip the fee?", []).startswith("Decision:")
    assert answer_task("Tell me about the workshop", []).startswith("Topic overview:")
    assert answer_task("How long is the workshop?", []).startswith("Quantity or range:")
