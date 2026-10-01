"""Structured staff reviews must remain evidence-bound and human-gated."""

from __future__ import annotations

import json
from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Json

import msfea_bot.api.app as api
from msfea_bot.config import settings
from msfea_bot.curation import assistance
from msfea_bot.curation.assistance import Intake, accept_draft, checked_report, enqueue
from msfea_bot.curation.revisions import DraftPayload, list_revisions
from msfea_bot.curation.validation import (
    REQUIRED_STEPS, execute_step, record_human_review, start_validation, validation_runs,
)
from msfea_bot.curation.publication import PublicationError, request_publication
from msfea_bot.llm import GenerationResult, LLMRateLimitError
from msfea_bot.retrieval.store import indexed_generation
import test_curation_publication


_publication_database = test_curation_publication.publication_database


@pytest.fixture
def studio_database(_publication_database: str):
    from msfea_bot.observability.store import _init_schema

    with psycopg.connect(_publication_database, autocommit=True) as conn:
        _init_schema(conn)
        conn.execute(
            "INSERT INTO interactions (id, question, refused, answer) VALUES"
            " (7, 'When can I attend the weekly CDC advising window?', true, 'Synthetic refusal.')"
        )
    yield _publication_database

GUIDANCE = "The weekly CDC advising window is Thursday from 2 to 4 p.m."
INTAKE = Intake(
    guidance=GUIDANCE, question="When can I attend the weekly CDC advising window?",
    department="all", programs=["internship"], linked_feedback_ids=[7],
)
EVIDENCE = [{
    "id": "policy-1", "text": "The weekly CDC advising window is Wednesday from 2 to 4 p.m.",
    "source_doc": "advising.md", "section": "Advising", "department": "all", "entry_id": None,
}]


def response(category: str = "direct_conflict") -> dict:
    return {
        "one_focused_topic": True,
        "question_supported": True,
        "classification": category, "summary": "The proposed advising day differs from the existing day.",
        "document_title": "Weekly CDC advising window",
        "question": "When is the weekly CDC advising window?",
        "paraphrase_question": "What time can I attend weekly CDC advising?",
        "expected_evidence": "Thursday from 2 to 4 p.m.",
        "clarifications": [],
        "findings": [{
            "category": category, "candidate_id": "policy-1",
            "proposed_claim_id": "c1", "existing_claim_id": "c1",
            "explanation": "Thursday and Wednesday cannot both be the weekly advising day under the same scope.",
        }],
    }


def payload(report: dict) -> DraftPayload:
    draft = report["draft"]
    return DraftPayload(
        **draft, department="all", programs=("internship",), evidence_refs=(),
        change_reason="Add a reviewed CDC advising clarification.", linked_feedback_ids=(7,),
        source_kind="admin_authored", authority_label="MSFEA CDC",
    )


def saved_review(database: str, report: dict, intake: Intake = INTAKE) -> str:
    review_id = uuid4().hex
    with psycopg.connect(database, autocommit=True) as conn:
        conn.execute(
            "INSERT INTO curation_assistance (id, request_key, intake, status, model,"
            " prompt_version, kb_generation, evidence, report)"
            " VALUES (%s, %s, %s, 'completed', 'test-model', %s, %s, %s, %s)",
            (review_id, uuid4().hex, Json(intake.model_dump()), assistance.PROMPT_VERSION,
             indexed_generation(), Json(EVIDENCE), Json(report)),
        )
    return review_id


def test_verbatim_policy_and_exact_claims_are_kept_separate_from_suggestions() -> None:
    report = checked_report(json.dumps(response()), INTAKE, EVIDENCE)
    assert report["draft"]["answer"] == GUIDANCE
    assert report["requires_decision"]
    assert report["findings"][0]["source_doc"] == "advising.md"
    assert report["findings"][0]["existing_claim"] == EVIDENCE[0]["text"]


def test_short_negative_answer_keeps_its_rule_and_literal_spacing() -> None:
    text = "**Answer:** No.  Company internships cannot be split into two four-week periods."
    assert assistance.claim_units(text) == {"c1": text}


def test_saved_draft_keeps_real_ai_feedback_and_can_reenter_guided_review(
    studio_database: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = checked_report(json.dumps(response()), INTAKE, EVIDENCE)
    review_id = saved_review(studio_database, report)
    entry_id, revision_id = accept_draft(review_id, payload(report), "CDC staff")
    monkeypatch.setattr(settings, "admin_token", "test-admin")
    client = TestClient(api.app)
    assert client.get('/admin/api/revisions').status_code == 401
    result = client.get('/admin/api/revisions', headers={"Authorization": "Bearer test-admin"})
    assert result.status_code == 200
    stored = next(item for item in result.json() if item['id'] == revision_id)['assistance']
    assert stored['id'] == review_id
    assert stored['model'] == 'test-model'
    assert stored['report'] == report
    assert stored['intake']['guidance'] == GUIDANCE
    with psycopg.connect(studio_database, autocommit=True) as conn:
        conn.execute("UPDATE curation_revision_state SET state='blocked' WHERE revision_id=%s", (revision_id,))
    monkeypatch.setattr(assistance, "validate_intake", lambda value: value)
    retry = INTAKE.model_copy(update={"entry_id": entry_id, "guidance": GUIDANCE.replace('Thursday', 'Monday')})
    next_review = enqueue(retry, uuid4().hex)
    assert assistance.get_review(next_review)['intake']['entry_id'] == entry_id
    next_response = response()
    next_response['expected_evidence'] = 'Monday from 2 to 4 p.m.'
    next_report = checked_report(json.dumps(next_response), retry, EVIDENCE)
    new_id = saved_review(studio_database, next_report, retry)
    _, corrected_id = accept_draft(new_id, payload(next_report), "CDC staff")
    correction = next(item for item in list_revisions() if item.id == corrected_id)
    assert correction.revision_number == 2 and correction.predecessor_revision_id == revision_id
    assert not correction.active and correction.linked_feedback_ids == [7]


def test_identical_draft_from_a_second_ai_review_has_a_readable_conflict(
    studio_database: str,
) -> None:
    report = checked_report(json.dumps(response()), INTAKE, EVIDENCE)
    entry_id, _ = accept_draft(saved_review(studio_database, report), payload(report), 'CDC staff')
    same = INTAKE.model_copy(update={'entry_id': entry_id})
    with pytest.raises(ValueError, match='identical reviewed draft already exists'):
        accept_draft(saved_review(studio_database, report, same), payload(report), 'CDC staff')


def test_regression_failure_shows_the_original_question_and_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from eval.loader import GoldenItem
    from msfea_bot.curation import validation
    from msfea_bot.generation.conversation import ConversationMessage
    from msfea_bot.retrieval.store import RetrievedChunk

    history = [ConversationMessage("user", "Can the CDC issue an internship letter?")]
    case = GoldenItem(
        id="letter-followup", question="Where do I get it?", history=history,
        expected_answer_or_behavior="Use the letter request form.", should_refuse=False,
        source_doc="guidelines.md", evidence="letter request form",
    )
    monkeypatch.setattr(validation, "load_golden_set", lambda: [case])
    monkeypatch.setattr(validation, "_jsonl_cases", lambda _: [])
    monkeypatch.setattr(validation, "retrieve_context", lambda *_a, **kw: [] if kw else [
        RetrievedChunk("letter", "Use the letter request form.", "guidelines.md", "Letters", .9),
    ])
    passed, details = validation._regression("private-candidate")
    assert not passed and details["newly_lost_previously_passing"] == ["letter-followup"]
    lost = details["lost_cases"][0]
    assert lost["question"] == "Where do I get it?"
    assert lost["history"] == [{"role": "user", "content": history[0].content}]
    assert lost["source_doc"] == "guidelines.md"


def test_assisted_update_keeps_the_active_source_until_approved(
    studio_database: str,
) -> None:
    from msfea_bot.curation.publication import publish_revision

    old_report = response()
    old_report.update(classification="new_information", findings=[])
    checked = checked_report(json.dumps(old_report), INTAKE, EVIDENCE)
    entry_id, first_id = accept_draft(saved_review(studio_database, checked), payload(checked), "CDC staff")
    run = test_curation_publication._authorize(first_id)
    publish_revision(first_id, run, smoke=lambda *_: (True, "Test passage retained."), invalidate_cache=lambda: None)

    updated = INTAKE.model_copy(update={
        "guidance": GUIDANCE.replace("Thursday", "Monday"), "entry_id": entry_id,
        "linked_feedback_ids": [],
    })
    evidence = assistance._evidence(updated)
    predecessor = next(item for item in evidence if item["id"] == f"predecessor-{first_id}")
    assert predecessor["entry_id"] == entry_id and predecessor["text"] == GUIDANCE
    proposed = response()
    proposed["expected_evidence"] = "Monday from 2 to 4 p.m."
    proposed["findings"][0]["candidate_id"] = predecessor["id"]
    report = checked_report(json.dumps(proposed), updated, [predecessor])
    update_payload = replace(payload(report), linked_feedback_ids=())
    same_entry, second_id = accept_draft(
        saved_review(studio_database, report, updated), update_payload, "CDC staff",
    )
    revisions = {item.id: item for item in list_revisions()}
    assert same_entry == entry_id
    assert revisions[second_id].predecessor_revision_id == first_id
    assert revisions[first_id].active and not revisions[second_id].active
    assert revisions[second_id].state == "draft" and report["requires_decision"]
    _, flags = assistance.revision_findings(second_id)
    assert flags[0]["existing_claim"] == GUIDANCE


@pytest.mark.parametrize("field,value", [
    ("candidate_id", "invented-document"),
    ("proposed_claim_id", "invented"),
    ("existing_claim_id", "invented"),
])
def test_fabricated_sources_and_quotes_fail_closed(field: str, value: str) -> None:
    result = response()
    result["findings"][0][field] = value
    with pytest.raises(ValueError):
        checked_report(json.dumps(result), INTAKE, EVIDENCE)


@pytest.mark.parametrize("mutate", ["phrase", "json", "empty_quotes", "same_question", "extra"])
def test_unverifiable_output_never_becomes_a_report(mutate: str) -> None:
    result = response()
    if mutate == "phrase":
        result["expected_evidence"] = "Monday from 9 to 5"
    elif mutate == "empty_quotes":
        result["findings"] = []
    elif mutate == "same_question":
        result["paraphrase_question"] = result["question"]
    elif mutate == "extra":
        result["publish_automatically"] = True
    text = json.dumps(result) if mutate != "json" else "{invalid"
    with pytest.raises(ValueError):
        checked_report(text, INTAKE, EVIDENCE)


def test_serious_findings_cannot_hide_behind_new_information_label() -> None:
    result = response()
    result["classification"] = "new_information"
    report = checked_report(json.dumps(result), INTAKE, EVIDENCE)
    assert report["classification"] == "direct_conflict"
    assert report["requires_decision"]


def test_clarification_blocks_draft_instead_of_inventing_missing_policy() -> None:
    result = response()
    result.update(classification="needs_clarification", findings=[],
                  clarifications=["Does this guidance apply during the summer term?"])
    report = checked_report(json.dumps(result), INTAKE, [])
    assert report["blocked"]
    assert report["draft"]["answer"] == GUIDANCE


def test_unfocused_entry_requires_splitting_even_if_comparison_is_complementary() -> None:
    result = response()
    result.update(classification="complementary", findings=[], one_focused_topic=False)
    report = checked_report(json.dumps(result), INTAKE, [])
    assert report["blocked"]
    assert report["classification"] == "needs_clarification"
    assert report["clarifications"]


def test_generated_questions_cannot_silently_replace_an_unanswered_student_question() -> None:
    result = response()
    result.update(classification="new_information", findings=[], question_supported=False)
    report = checked_report(json.dumps(result), INTAKE, [])
    assert report["blocked"]
    assert report["classification"] == "needs_clarification"


def test_linked_question_cannot_be_swapped_for_a_different_topic(studio_database: str) -> None:
    with pytest.raises(ValueError, match="original unanswered question"):
        enqueue(INTAKE.model_copy(update={"question": "What is the internship tuition?"}), uuid4().hex)


def test_unrelated_passages_do_not_require_displaying_all_retrieved_text() -> None:
    result = response()
    result.update(classification="new_information", findings=[])
    report = checked_report(json.dumps(result), INTAKE, EVIDENCE)
    assert report["findings"] == []
    assert report["comparison_count"] == 1
    assert not report["requires_decision"]


@pytest.mark.parametrize("guidance", [
    "John Smith submitted the advising question for the CDC.",
    "Please contact student123@example.com about the new advising rule.",
    "The student identifier is 202612345 and advising is Thursday.",
])
def test_private_student_data_is_rejected_before_persistence_or_model_call(guidance: str) -> None:
    with pytest.raises(ValueError, match="Remove personal"):
        assistance.validate_intake(INTAKE.model_copy(update={"guidance": guidance}))


def test_missing_local_privacy_model_blocks_staff_review(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(assistance, "_ner", lambda: None)
    with pytest.raises(ValueError, match="name redaction"):
        assistance.validate_intake(INTAKE)


def test_policy_dates_survive_identifier_redaction() -> None:
    assert assistance._safe_text("This guideline takes effect on 2026-10-01.") == (
        "This guideline takes effect on 2026-10-01."
    )
    assert assistance._safe_text("The course is graded Pass (P) or Fail (F).") == (
        "The course is graded Pass (P) or Fail (F)."
    )


def test_request_replay_is_idempotent_and_different_input_is_rejected(
    studio_database: str,
) -> None:
    key = uuid4().hex
    first = enqueue(INTAKE, key)
    assert enqueue(INTAKE, key) == first
    with pytest.raises(ValueError, match="different guidance"):
        enqueue(INTAKE.model_copy(update={"guidance": GUIDANCE + " No appointment is needed."}), key)


def test_review_acceptance_is_atomic_idempotent_and_does_not_publish(
    studio_database: str,
) -> None:
    report = checked_report(json.dumps(response()), INTAKE, EVIDENCE)
    review_id = saved_review(studio_database, report)
    before = indexed_generation()
    entry_id, revision_id = accept_draft(review_id, payload(report), "CDC reviewer")
    assert accept_draft(review_id, payload(report), "CDC reviewer") == (entry_id, revision_id)
    assert indexed_generation() == before
    assert not list_revisions()[0].active
    related, flags = assistance.revision_findings(revision_id)
    assert flags[0]["reason"] == "ai_direct_conflict"
    assert related[0]["text"] == EVIDENCE[0]["text"]
    with pytest.raises(ValueError, match="different saved draft"):
        accept_draft(review_id, replace(payload(report), authority_label="Different owner"), "CDC reviewer")


def test_semantic_conflict_reaches_mandatory_review_and_cannot_be_bypassed(
    studio_database: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = checked_report(json.dumps(response()), INTAKE, EVIDENCE)
    review_id = saved_review(studio_database, report)
    _, revision_id = accept_draft(review_id, payload(report), "CDC reviewer")
    run_id = start_validation(revision_id)
    # Pure orchestration test: other checks have dedicated real retrieval coverage.
    monkeypatch.setattr("msfea_bot.curation.validation._candidate_chunks", lambda _: [])
    monkeypatch.setattr("msfea_bot.curation.validation._source_check", lambda _: (True, {}))
    monkeypatch.setattr("msfea_bot.curation.validation._positive_retrieval", lambda *_: (True, {}))
    monkeypatch.setattr("msfea_bot.curation.validation._department_isolation", lambda *_: (True, {}))
    monkeypatch.setattr("msfea_bot.curation.validation._unknown_department", lambda *_: (True, {}))
    monkeypatch.setattr("msfea_bot.curation.validation._regression", lambda *_: (True, {}))
    monkeypatch.setattr("msfea_bot.curation.validation.review_candidates", lambda *_args, **_kw: ([], []))
    # Use an isolated candidate DB from the existing fixture's temporary database
    # only after candidate_index; no writes go to the serving index.
    from psycopg.conninfo import conninfo_to_dict, make_conninfo
    from psycopg import sql
    candidate_name = "studio_candidate_" + uuid4().hex
    base = conninfo_to_dict(studio_database)
    admin = make_conninfo(**{**base, "dbname": "postgres"})
    candidate = make_conninfo(**{**base, "dbname": candidate_name})
    with psycopg.connect(admin, autocommit=True) as conn:
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(candidate_name)))
    try:
        for step in REQUIRED_STEPS:
            execute_step(run_id, step, candidate)
        assert list_revisions()[0].state == "blocked"
        conflict = next(result for result in validation_runs()[0]["results"]
                        if result["step"] == "conflict_review")
        assert conflict["details"]["flags"][0]["reason"] == "ai_direct_conflict"
        with pytest.raises(ValueError):
            record_human_review(run_id, "Reviewer", "confirm_no_conflict", "Approve automatically.")
        with pytest.raises(PublicationError):
            request_publication(revision_id, run_id)
    finally:
        with psycopg.connect(admin, autocommit=True) as conn:
            conn.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(candidate_name)))


@pytest.mark.parametrize("change", ["answer", "department", "questions", "feedback", "title", "stale"])
def test_edited_or_stale_review_cannot_authorize_a_different_draft(
    studio_database: str, monkeypatch: pytest.MonkeyPatch, change: str,
) -> None:
    report = checked_report(json.dumps(response()), INTAKE, EVIDENCE)
    review_id = saved_review(studio_database, report)
    proposed = payload(report)
    if change == "answer":
        proposed = replace(proposed, answer="The new advising time is Monday from 2 to 4 p.m.")
    elif change == "department":
        proposed = replace(proposed, department="ece")
    elif change == "questions":
        proposed = replace(proposed, paraphrase_question="An entirely different question?")
    elif change == "feedback":
        proposed = replace(proposed, linked_feedback_ids=(9,))
    elif change == "title":
        proposed = replace(proposed, document_title="Different title")
    else:
        monkeypatch.setattr(assistance, "indexed_generation", lambda: "changed")
    with pytest.raises(ValueError, match="changed"):
        accept_draft(review_id, proposed, "CDC reviewer")
    assert list_revisions() == []


@pytest.mark.parametrize("failure", ["quota", "malformed", "interrupted"])
def test_worker_failures_are_durable_safe_and_never_replayed_automatically(
    studio_database: str, monkeypatch: pytest.MonkeyPatch, failure: str,
) -> None:
    review_id = enqueue(INTAKE, uuid4().hex)
    calls = []

    def generate(_: str) -> GenerationResult:
        calls.append(1)
        if failure == "quota":
            raise LLMRateLimitError("private provider body must not be stored")
        return GenerationResult(text="{broken}")

    monkeypatch.setattr(assistance, "_evidence", lambda _: EVIDENCE)
    monkeypatch.setattr(assistance, "get_curation_provider", lambda _, **_kw: SimpleNamespace(generate=generate))
    if failure == "interrupted":
        with psycopg.connect(studio_database, autocommit=True) as conn:
            conn.execute(
                "UPDATE curation_assistance SET status='running', started_at=now()-interval '6 minutes',"
                " lease_expires_at=now()-interval '1 minute' WHERE id=%s", (review_id,),
            )
    assistance.process_next()
    review = assistance.get_review(review_id)
    assert review is not None and review["status"] == "failed"
    assert review["error_code"] == {
        "quota": "quota", "malformed": "invalid_review", "interrupted": "interrupted",
    }[failure]
    assert not assistance.process_next()
    assert len(calls) == (0 if failure == "interrupted" else 1)


def test_queue_waits_instead_of_bursting_the_curation_model(
    studio_database: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = enqueue(INTAKE, uuid4().hex)
    second = enqueue(INTAKE, uuid4().hex)
    result = response()
    result.update(classification="new_information", findings=[])
    monkeypatch.setattr(assistance, "_evidence", lambda _: EVIDENCE)
    monkeypatch.setattr(assistance, "get_curation_provider", lambda _, **_kw: SimpleNamespace(
        generate=lambda _: GenerationResult(text=json.dumps(result)),
    ))
    assert assistance.process_next()
    assert not assistance.process_next()
    assert assistance.get_review(first)["status"] == "completed"
    assert assistance.get_review(second)["status"] == "queued"


def test_queued_review_from_older_rules_requires_a_fresh_request(
    studio_database: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    review_id = enqueue(INTAKE, uuid4().hex)
    with psycopg.connect(studio_database, autocommit=True) as conn:
        conn.execute(
            "UPDATE curation_assistance SET prompt_version='older-rules' WHERE id=%s", (review_id,),
        )
    monkeypatch.setattr(assistance, "get_curation_provider", lambda *_a, **_kw: pytest.fail("No model call"))
    assert not assistance.process_next()
    review = assistance.get_review(review_id)
    assert review["status"] == "failed" and review["error_code"] == "stale_review"


def test_model_budget_counts_each_attempt_and_is_separate_per_model(
    studio_database: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "curation_llm_daily_call_limit", 18)
    with psycopg.connect(studio_database, autocommit=True) as conn:
        for _ in range(18):
            conn.execute(
                "INSERT INTO curation_events (event_type, actor_type, payload)"
                " VALUES ('staff_model_requested', 'worker', %s)",
                (Json({"assistance_id": uuid4().hex, "model": "limited-model"}),),
            )
        conn.execute("UPDATE curation_events SET created_at=now()-interval '30 seconds'")
    with pytest.raises(LLMRateLimitError):
        assistance.reserve_model_call(uuid4().hex, "limited-model")
    assistance.reserve_model_call("different-review", "another-model")
    with psycopg.connect(studio_database, autocommit=True) as conn:
        model = conn.execute(
            "SELECT payload->>'model' FROM curation_events"
            " WHERE payload->>'assistance_id'='different-review'"
        ).fetchone()
    assert model[0] == "another-model"


def test_studio_endpoints_require_admin_and_worker_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "admin_token", "test-admin")
    client = TestClient(api.app)
    assert client.get("/admin/api/studio/reviews/unknown").status_code == 401
    monkeypatch.setattr(settings, "curation_worker_token", "")
    result = client.post("/admin/api/studio/reviews",
                         json={"intake": INTAKE.model_dump(), "request_key": uuid4().hex},
                         headers={"Authorization": "Bearer test-admin"})
    assert result.status_code == 503


def test_curation_provider_does_not_change_student_settings_or_retry_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from google import genai
    from msfea_bot.llm import get_curation_provider

    monkeypatch.setattr(settings, "llm_api_key", "fake")
    monkeypatch.setattr(settings, "llm_provider", "gemini")
    monkeypatch.setattr(settings, "llm_model", "student-model")
    seen = {}
    monkeypatch.setattr(genai, "Client", lambda **kw: seen.update(kw) or SimpleNamespace())
    provider = get_curation_provider(assistance.ReviewReport.model_json_schema())
    assert settings.llm_model == "student-model"
    assert provider._model == settings.curation_llm_model
    assert provider._retry_transient is True
    assert provider._config.response_mime_type == "application/json"
    assert seen["http_options"].timeout == 90_000
