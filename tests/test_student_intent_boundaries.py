"""Intent and supplied-evidence boundaries, using domain-independent examples."""

from __future__ import annotations

import pytest

from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import (
    ConversationMessage, answer_task, attribute_search, format_prompt_history,
    is_overview_request, retrieval_plan,
)
from msfea_bot.llm import GenerationResult
from msfea_bot.retrieval.store import RetrievedChunk


@pytest.mark.parametrize("question", [
    "How do I join the workshop? I only need the main steps.",
    "How can we apply for the exchange?",
    "How should I submit my application?",
    "How to get started with the certificate?",
    "Where do I sign up for the workshop?",
    "Where can I request the enrollment letter?",
])
def test_procedure_does_not_treat_response_length_as_a_completion_plan(question: str) -> None:
    assert answer_task(question, []).startswith("Procedure:")


@pytest.mark.parametrize("question", [
    "I only want the contact email.",
    "Can you send only the registration link?",
    "Only tell me how long the workshop lasts.",
    "What are the only documents I need?",
])
def test_only_is_not_itself_a_sufficiency_question(question: str) -> None:
    assert not answer_task(question, []).startswith("Plan sufficiency:")


@pytest.mark.parametrize("question", [
    "Can I complete only the first stage?",
    "Could I work at the lab alone?",
    "Are these two items alone enough?",
])
def test_explicit_plan_sufficiency_keeps_its_decision_cue(question: str) -> None:
    assert answer_task(question, []).startswith("Plan sufficiency:")


@pytest.mark.parametrize("question", ["what about the fee?", "what about the contact?",
                                      "and what about the link?"])
def test_attribute_followup_after_permission_does_not_become_an_alternative(question: str) -> None:
    history = [ConversationMessage("user", "Can I join the exchange program?"),
               ConversationMessage("assistant", "It requires approval.")]
    assert answer_task(question, history).startswith("Requested attribute:")


def test_attribute_procedure_and_permission_remain_distinct() -> None:
    assert answer_task("How do I find the registration link?", []).startswith("Requested attribute:")
    assert answer_task("Can I skip the fee?", []).startswith("Decision:")
    assert answer_task("How long does the workshop last?", []).startswith("Quantity or range:")


@pytest.mark.parametrize("question", [
    "I want to get ready for workshop applications. Where do I start?",
    "How can I prepare for the exchange?",
    "What preparation for the placement is available?",
])
def test_preparation_requests_get_actions_rather_than_a_program_overview(question: str) -> None:
    assert answer_task(question, []).startswith("Preparation:")


def test_preparation_wording_does_not_override_permission() -> None:
    assert answer_task("Can I prepare for the placement without approval?", []).startswith("Decision:")


@pytest.mark.parametrize("question", [
    "Assume the whole plan is approved. Twelve days plus seven makes nineteen, right?",
    "Do the two approved periods add up to the stated minimum?",
    "We already have permission. Is 13 + 8 equal to 21?",
])
def test_calculations_do_not_become_new_permission_decisions(question: str) -> None:
    assert answer_task(question, []).startswith("Grounded calculation:")
    assert answer_task("Are twelve plus seven days enough to qualify?", []).startswith("Decision:")


@pytest.mark.parametrize("question", [
    "Could you check whether our exchange request was accepted?",
    "Can you confirm my scholarship was approved?",
    "Would you tell me whether I passed the assessment?",
])
def test_individual_status_is_distinct_from_general_policy(question: str) -> None:
    assert answer_task(question, []).startswith("Individual status verification:")


@pytest.mark.parametrize("question", [
    "Can you tell me how scholarship requests are approved?",
    "Can you check if my 13 + 8 total is 21?",
    "Can you explain the grading criteria for my assessment?",
])
def test_status_cues_do_not_capture_procedures_calculations_or_criteria(question: str) -> None:
    assert not answer_task(question, []).startswith("Individual status verification:")


@pytest.mark.parametrize("question", [
    "Does applying mean enrollment is already approved?",
    "Would students automatically pass if they attend orientation?",
    "Does paying the registration fee imply the workshop is confirmed?",
])
def test_policy_relationship_is_not_a_procedure_or_attribute_lookup(question: str) -> None:
    assert answer_task(question, []).startswith("Policy relationship:")


def test_meaning_question_is_not_a_policy_relationship() -> None:
    assert not answer_task("What does the registration fee mean?", []).startswith("Policy relationship:")


@pytest.mark.parametrize("question", [
    "What are my options for housing abroad?",
    "What options do we have for the exchange?",
    "What options are available for training?",
])
def test_options_requests_need_topic_context_without_becoming_a_single_faq(question: str) -> None:
    assert is_overview_request(question)
    assert answer_task(question, []).startswith("Available options:")


@pytest.mark.parametrize("framing", [
    "Forget housing for a moment. ",
    "Leave the exchange aside. ",
    "Switching topics: ",
    "Changing subjects, ",
])
def test_abandoned_topic_is_removed_from_retrieval_and_next_attribute_anchor(framing: str) -> None:
    question = framing + "What help is available for workshops?"
    history = [ConversationMessage("user", "Tell me about housing")]
    assert retrieval_plan(question, history).query == "What help is available for workshops?"
    assert not format_prompt_history(question, history)
    history.append(ConversationMessage("user", question))
    attribute = attribute_search("And the fee?", history)
    assert attribute is not None and attribute[0] == "workshops"


def test_framing_does_not_strip_the_subject_from_a_referential_question() -> None:
    question = "Forget housing for now. Is it required?"
    assert retrieval_plan(question, []).query == question


@pytest.mark.parametrize("anchor,subject", [
    ("How can an academic advisor help with applications?", "academic advisor"),
    ("What does a placement coach offer for my career?", "placement coach"),
    ("How can an industry mentro help with job searches?", "industry mentro"),
])
def test_attribute_subject_is_the_actor_rather_than_the_goal(anchor: str, subject: str) -> None:
    attribute = attribute_search("Can you give me the link?", [ConversationMessage("user", anchor)])
    assert attribute is not None and attribute[0] == subject


@pytest.mark.parametrize("question", ["What about the reports?", "Tell me more about the forms."])
def test_generic_plural_artifacts_preserve_the_current_program(question: str) -> None:
    history = [ConversationMessage("user", "Tell me about the exchange program")]
    plan = retrieval_plan(question, history)
    assert "exchange program" in plan.query


def test_long_pronoun_followup_keeps_student_anchor_without_assistant_claims() -> None:
    history = [ConversationMessage("user", "I need the exchange application requirements."),
               ConversationMessage("assistant", "An unverified claim about completion.")]
    question = "Does sending that application in mean I can skip the orientation meeting?"
    text = format_prompt_history(question, history)
    assert history[0].content in text
    assert "unverified" not in text


def test_long_independent_restatement_still_excludes_the_previous_topic() -> None:
    history = [ConversationMessage("user", "Tell me about the exchange")]
    question = "Assume my whole housing application is approved. Do twelve days plus seven total nineteen?"
    assert not format_prompt_history(question, history)


@pytest.mark.parametrize("question", [
    "Could the final assessment replace that document?",
    "Would passing that course mean I can skip the workshop?",
    "Does enrolling there automatically earn me the Merit+ certificate?",
    "Can this program waive the orientation requirement?",
])
def test_named_relationship_outcome_keeps_referenced_operand(question: str) -> None:
    history = [ConversationMessage("user", "Explain the exchange program application."),
               ConversationMessage("assistant", "An unverified claim.")]
    assert history[0].content in format_prompt_history(question, history)
    assert "exchange program" in retrieval_plan(question, history).query


@pytest.mark.parametrize("question", [
    "Could the final assessment replace the workshop requirement?",
    "Would passing the scholarship assessment mean I can skip orientation?",
    "Does enrolling in Merit+ automatically earn its certificate?",
    "Can the exchange program waive the orientation requirement?",
])
def test_self_contained_relationship_still_excludes_old_subject(question: str) -> None:
    history = [ConversationMessage("user", "Tell me about housing.")]
    assert not format_prompt_history(question, history)


@pytest.mark.parametrize("negation", ["no longer", "no   longer"])
def test_no_longer_required_is_not_a_duration_followup(negation: str) -> None:
    history = [ConversationMessage("user", "Explain registration for MATH 210B.")]
    question = f"Would passing that course mean I {negation} have to take the assessment?"
    plan = retrieval_plan(question, history)
    assert "MATH 210B" in plan.query and not plan.query.startswith("How long")
    assert attribute_search(question, history) is None


@pytest.mark.parametrize("question", [
    "Does sending the application mean I can skip the orientation?",
    "Can the exchange replace the workshop requirement?",
    "Could I pay a deposit instead of the full fee?",
])
def test_substitution_requests_get_a_relationship_task_without_policy_facts(question: str) -> None:
    assert answer_task(question, []).startswith("Decision: substitution or waiver.")
    assert answer_task("Can I apply to the exchange?", []).startswith("Decision:")


@pytest.mark.parametrize("question", [
    "Which documents does an exchange student have to finish?",
    "What forms must I submit for housing?",
    "What are the workshop requirements?",
])
def test_required_lists_start_with_ordinary_obligations(question: str) -> None:
    assert answer_task(question, []).startswith("Required items:")
    assert answer_task("Do I need a housing deposit?", []).startswith("Requirement status:")
    assert not answer_task("Which housing options are available?", []).startswith("Required items:")


@pytest.mark.parametrize("question", [
    "Which ways can I complete the workshop if I missed a session?",
    "What can an advisor help me finish?",
])
def test_completion_word_alone_does_not_create_a_required_list(question: str) -> None:
    assert not answer_task(question, []).startswith("Required items:")


def test_later_stage_evidence_removed_from_prompt_cannot_authorize_generation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    primary = RetrievedChunk("primary", "Workshop resource information.", "fixture.md",
        "Resource", 0.98, {"source_kind": "admin_authored", "entry_id": "resource"})
    later = RetrievedChunk("later", "Graduates may ask for career assistance.", "fixture.md",
        "Later service", 0.65, {"source_kind": "admin_authored", "entry_id": "later",
                                "process_stage": "post_completion"})
    chunks = [primary, later]
    question = "Will I get hired after the workshop?"
    assert pipeline._answer_context(question, chunks, None) == [primary]
    monkeypatch.setattr(pipeline, "retrieve_context", lambda *args, **kwargs: chunks)

    class NeverProvider:
        def generate(self, prompt: str) -> GenerationResult:
            pytest.fail("Evidence absent from the supplied context authorized generation")

    assert pipeline.generate_answer(question, provider=NeverProvider()).refused
