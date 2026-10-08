"""Exercise private preview, repair and queue ownership using isolated databases."""

from __future__ import annotations

import json
from dataclasses import replace

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Json

import msfea_bot.api.app as api
from msfea_bot.config import settings
from msfea_bot.curation import workspace
from msfea_bot.curation.assistance import accept_draft, checked_report
from msfea_bot.curation.publication import PublicationResult
from msfea_bot.curation.revisions import list_revisions
from msfea_bot.curation.validation import REQUIRED_STEPS, start_validation
from msfea_bot.curation.validation import record_human_review
from msfea_bot.generation.answer import Answer
from msfea_bot.ingestion.chunking import Chunk
from msfea_bot.retrieval import store
import test_curation_validation
import test_studio_assistance

isolated_pair = test_curation_validation.isolated_pair
studio_database = test_studio_assistance.studio_database
_publication_database = test_studio_assistance._publication_database


def reviewed(database: str) -> int:
    report_data = test_studio_assistance.response()
    report_data.update(classification="new_information", findings=[])
    report = checked_report(json.dumps(report_data), test_studio_assistance.INTAKE, [])
    report["draft"]["retrieval_questions"] = ["When is the weekly CDC advising window?"]
    review = test_studio_assistance.saved_review(database, report)
    return accept_draft(review, test_studio_assistance.payload(report), "CDC reviewer")[1]


def passed_run(database: str, revision_id: int, candidate_generation: str = "private-generation") -> str:
    run_id = start_validation(revision_id)
    with psycopg.connect(database) as conn:
        conn.execute("UPDATE curation_validation_runs SET status='passed',candidate_generation=%s WHERE id=%s", (candidate_generation, run_id))
        for step in REQUIRED_STEPS:
            conn.execute("INSERT INTO curation_validation_results (run_id,step,status,details) VALUES (%s,%s,'passed','{}')", (run_id, step))
        workspace.schedule(conn, run_id, revision_id, "preview")
    return run_id


def test_preview_uses_private_candidate_and_original_question_without_logging_student_feedback(studio_database, monkeypatch):
    monkeypatch.setattr(settings, "validation_database_url", "postgresql://private-only/not-serving")
    revision = reviewed(studio_database)
    passed_run(studio_database, revision)
    monkeypatch.setattr(workspace, "indexed_generation", lambda _dsn: "private-generation")
    monkeypatch.setattr(workspace, "get_preview_provider", lambda **_kw: object())
    seen = []
    def generate(question, **kwargs):
        seen.append((question, kwargs))
        return Answer(text="Thursday from 2 to 4 p.m.", citations=["CDC Knowledge > Weekly advising"])
    monkeypatch.setattr(workspace, "generate_answer", generate)
    before = store.indexed_generation()
    assert workspace.process_next_workspace_job()
    state = workspace.workspace(revision)
    assert state["jobs"][0]["result"]["passed"]
    assert seen[0][0] == test_studio_assistance.INTAKE.question
    assert all(kwargs["database_url"] == settings.validation_database_url for _, kwargs in seen)
    assert store.indexed_generation() == before
    assert not state["revision"]["active"]
    with psycopg.connect(studio_database) as conn:
        assert conn.execute("SELECT resolved_at FROM interactions WHERE id=7").fetchone()[0] is None


@pytest.mark.parametrize("setting,value", [
    ("llm_model", "different-student-model"),
    ("llm_gemini_thinking_level", "high"),
    ("llm_max_output_tokens", 8192),
])
def test_profile_change_blocks_approval_and_retries_only_previews(studio_database, monkeypatch, setting, value):
    revision = reviewed(studio_database)
    run_id = passed_run(studio_database, revision)
    monkeypatch.setattr(workspace, "indexed_generation", lambda _dsn: "private-generation")
    monkeypatch.setattr(workspace, "get_preview_provider", lambda **_kw: object())
    monkeypatch.setattr(workspace, "generate_answer", lambda *_args, **_kw: Answer(text="Thursday from 2 to 4 p.m.", citations=["CDC Knowledge > Weekly advising"]))
    assert workspace.process_next_workspace_job()
    old = workspace.workspace(revision)["jobs"][0]["result"]
    monkeypatch.setattr(settings, setting, value)
    state = workspace.workspace(revision)
    assert not state["stale"] and state["run"]["id"] == run_id
    assert state["jobs"][0]["error_code"] == "preview_profile_changed"
    assert not state["jobs"][0]["result"]["passed"]
    monkeypatch.setattr(settings, "admin_token", "test-admin")
    client = TestClient(api.app)
    body = {"revision_id": revision, "run_id": run_id, "reviewer_label": "CDC reviewer", "decision": "confirm_no_conflict", "reason": "Reviewed the source."}
    assert client.post('/admin/api/studio/approve', json=body, headers={"Authorization": "Bearer test-admin"}).status_code == 409
    workspace.retry_preview(revision)
    with psycopg.connect(studio_database) as conn:
        saved = conn.execute("SELECT payload FROM curation_events WHERE event_type='preview_retried'").fetchone()[0]
        assert saved["result"] == old
        assert conn.execute("SELECT count(*) FROM curation_validation_results WHERE run_id=%s", (run_id,)).fetchone()[0] == len(REQUIRED_STEPS)
    assert workspace.process_next_workspace_job()
    assert workspace.workspace(revision)["jobs"][0]["result"]["passed"]
    with pytest.raises(ValueError, match="no failed preview"):
        workspace.retry_preview(revision)


def test_legacy_preview_requires_refresh(studio_database):
    revision = reviewed(studio_database)
    run_id = passed_run(studio_database, revision)
    with psycopg.connect(studio_database) as conn:
        conn.execute("UPDATE curation_workspace_jobs SET status='completed',result=%s WHERE run_id=%s", (Json({"passed": True}), run_id))
    assert workspace.workspace(revision)["jobs"][0]["error_code"] == "preview_profile_changed"
    workspace.retry_preview(revision)
    assert workspace.workspace(revision)["jobs"][0]["status"] == "queued"


def test_publication_rechecks_profile_and_human_approval_after_preview_retry(studio_database, monkeypatch):
    from msfea_bot.curation.publication import PublicationError, _assert_authorized
    from msfea_bot.curation.validation import get_revision, validation_fingerprint

    revision_id = reviewed(studio_database)
    run_id = passed_run(studio_database, revision_id)
    monkeypatch.setattr(workspace, "indexed_generation", lambda _dsn: "private-generation")
    monkeypatch.setattr(workspace, "get_preview_provider", lambda **_kw: object())
    monkeypatch.setattr(workspace, "generate_answer", lambda *_args, **_kw: Answer(text="Thursday from 2 to 4 p.m.", citations=["CDC Knowledge > Weekly advising"]))
    assert workspace.process_next_workspace_job()
    record_human_review(run_id, "CDC reviewer", "confirm_no_conflict", "Source and current previews checked.")
    revision = get_revision(revision_id)
    fingerprint = validation_fingerprint(revision)
    with psycopg.connect(studio_database) as conn:
        _assert_authorized(conn, revision, run_id, fingerprint)
    monkeypatch.setattr(settings, "llm_model", "changed-student-model")
    with psycopg.connect(studio_database) as conn, pytest.raises(PublicationError, match="refreshing"):
        _assert_authorized(conn, revision, run_id, fingerprint)
    workspace.retry_preview(revision_id)
    assert workspace.process_next_workspace_job()
    with psycopg.connect(studio_database) as conn, pytest.raises(PublicationError, match="approval must follow"):
        _assert_authorized(conn, revision, run_id, fingerprint)
    record_human_review(run_id, "CDC reviewer", "confirm_no_conflict", "Refreshed previews checked again.")
    with psycopg.connect(studio_database) as conn:
        _assert_authorized(conn, revision, run_id, fingerprint)


def test_preview_refusal_is_visible_and_cannot_become_a_success(studio_database, monkeypatch):
    revision = reviewed(studio_database)
    passed_run(studio_database, revision)
    monkeypatch.setattr(workspace, "indexed_generation", lambda _dsn: "private-generation")
    monkeypatch.setattr(workspace, "get_preview_provider", lambda **_kw: object())
    monkeypatch.setattr(workspace, "generate_answer", lambda *_args, **_kwargs: Answer(text="Please contact the CDC.", refused=True))
    assert workspace.process_next_workspace_job()
    job = workspace.workspace(revision)["jobs"][0]
    assert job["status"] == "completed"
    assert job["result"]["passed"] is False
    assert job["result"]["previews"][0]["refused"]


def test_repair_preserves_facts_scope_and_original_tests_and_is_bounded(studio_database, monkeypatch):
    revision_id = reviewed(studio_database)
    original = list_revisions()[0]
    run_id = start_validation(revision_id)
    with psycopg.connect(studio_database) as conn:
        conn.execute("UPDATE curation_validation_runs SET status='failed',candidate_generation='private-generation' WHERE id=%s", (run_id,))
        conn.execute("UPDATE curation_revision_state SET state='blocked' WHERE revision_id=%s", (revision_id,))
        conn.execute("INSERT INTO curation_validation_results (run_id,step,status,details) VALUES (%s,'positive_retrieval','failed',%s)", (run_id, Json({"cases": [{"question": original.representative_question, "candidate_hit": False}]})))
        workspace.schedule(conn, run_id, revision_id, "repair")
    monkeypatch.setattr(workspace, "indexed_generation", lambda _dsn: "private-generation")
    monkeypatch.setattr(workspace, "prepare_retrieval", lambda *_args: (["Which hours is the weekly drop-in advising window open?"], {"supported": True, "missing_details": [], "explanation": "A focused service question is fully supported."}))
    assert workspace.process_next_workspace_job()
    job = workspace.workspace(revision_id)["jobs"][0]
    assert job["status"] == "completed"
    successor_id = job["result"]["successor_revision_id"]
    successor = next(revision for revision in list_revisions() if revision.id == successor_id)
    assert (successor.answer, successor.department, successor.programs, successor.representative_question, successor.paraphrase_question, successor.expected_evidence) == (original.answer, original.department, original.programs, original.representative_question, original.paraphrase_question, original.expected_evidence)
    assert successor.retrieval_questions != original.retrieval_questions
    assert successor.state == "validating" and not successor.active
    with psycopg.connect(studio_database) as conn:
        workspace.schedule(conn, job["result"]["run_id"], successor_id, "repair")
        assert conn.execute("SELECT count(*) FROM curation_workspace_jobs WHERE kind='repair'").fetchone()[0] == 1


def test_enrichment_is_embedded_but_never_returned_as_answer_evidence(studio_database):
    canonical = "The advising window is Thursday from 2 to 4 p.m."
    chunk = Chunk("test-enrichment", canonical, "demo.md", "Advising", retrieval_text=canonical + " Which day is drop-in advising available?")
    store.index_chunks([chunk])
    result = store.search("Which day is drop-in advising available?", 1)
    assert result[0].text == canonical
    assert "drop-in" not in result[0].text


def test_candidate_reuses_only_identical_search_text(studio_database, monkeypatch):
    chunks = [Chunk("unchanged", "An unchanged canonical rule.", "demo.md", "Rule")]
    store.index_chunks(chunks)
    calls = []
    def embed(texts):
        calls.append(texts)
        return [[0.0] * 384 for _ in texts]
    monkeypatch.setattr(store, "embed_texts", embed)
    prepared = store.prepare_chunks(chunks, studio_database)
    assert len(prepared) == 1 and calls == []
    changed = [replace(chunks[0], retrieval_text="A different verified search representation.")]
    store.prepare_chunks(changed, studio_database)
    assert calls == [[changed[0].retrieval_text]]


def test_search_keyword_ties_are_stable_across_source_rebuild_order(studio_database):
    chunks = [Chunk("alpha", "Advising tokenexample.", "a.md", "A"), Chunk("beta", "Advising tokenexample.", "b.md", "B")]
    store.index_chunks(chunks)
    before = [item.id for item in store.search("tokenexample", 2)]
    store.index_chunks(list(reversed(chunks)))
    assert [item.id for item in store.search("tokenexample", 2)] == before


@pytest.mark.parametrize("preview_passed", [True, False])
def test_guided_approval_requires_successful_private_previews(studio_database, monkeypatch, preview_passed):
    revision = reviewed(studio_database)
    run_id = passed_run(studio_database, revision)
    with psycopg.connect(studio_database) as conn:
        conn.execute("UPDATE curation_workspace_jobs SET status='completed',result=%s WHERE run_id=%s", (Json({"passed": preview_passed, "profile_fingerprint": workspace.preview_fingerprint()}), run_id))
    monkeypatch.setattr(settings, "admin_token", "test-admin")
    requested = []
    monkeypatch.setattr(api, "request_publication", lambda *args, **kwargs: requested.append(args) or PublicationResult("fake-attempt", revision, "publishing", None))
    client = TestClient(api.app)
    body = {"revision_id": revision, "run_id": run_id, "reviewer_label": "CDC reviewer", "decision": "confirm_no_conflict", "reason": "Verified the synthetic source and both student previews."}
    assert client.post('/admin/api/studio/approve', json=body).status_code == 401
    result = client.post('/admin/api/studio/approve', json=body, headers={"Authorization": "Bearer test-admin"})
    assert result.status_code == (200 if preview_passed else 409)
    assert bool(requested) == preview_passed


def test_repair_interruption_preserves_successor_and_never_changes_the_live_kb(studio_database, monkeypatch):
    revision_id = reviewed(studio_database)
    run_id = start_validation(revision_id)
    with psycopg.connect(studio_database) as conn:
        conn.execute("UPDATE curation_validation_runs SET status='failed',candidate_generation='private-generation' WHERE id=%s", (run_id,))
        workspace.schedule(conn, run_id, revision_id, "repair")
    before = store.indexed_generation()
    monkeypatch.setattr(workspace, "indexed_generation", lambda _dsn: "private-generation")
    monkeypatch.setattr(workspace, "prepare_retrieval", lambda *_args: (["Which hours is the weekly drop-in advising window open?"], {"supported": True, "missing_details": [], "explanation": "Only the search wording changes."}))
    monkeypatch.setattr(workspace, "start_validation", lambda *_args: (_ for _ in ()).throw(RuntimeError("interrupted")))
    assert workspace.process_next_workspace_job()
    job = workspace.workspace(revision_id)["jobs"][0]
    assert job["status"] == "failed" and job["error_code"] == "service_unavailable"
    assert job["result"]["successor_revision_id"]
    assert len(list_revisions()) == 2
    assert store.indexed_generation() == before


def test_manual_review_cannot_override_a_verified_conflicting_official_source(studio_database):
    revision = reviewed(studio_database)
    run_id = passed_run(studio_database, revision)
    with psycopg.connect(studio_database) as conn:
        conn.execute("UPDATE curation_validation_results SET details=%s WHERE run_id=%s AND step='conflict_review'", (Json({"flags": [{"reason": "ai_direct_conflict", "entry_id": None}]}), run_id))
    with pytest.raises(ValueError, match="remain active"):
        record_human_review(run_id, "CDC reviewer", "valid_scoped_exception", "An attempted generic approval cannot authorize two contradictory active rules.")


def test_explicit_service_retry_reuses_one_repair_and_cannot_retry_a_completed_correction(studio_database):
    revision = reviewed(studio_database)
    run_id = start_validation(revision)
    with psycopg.connect(studio_database) as conn:
        conn.execute("UPDATE curation_validation_runs SET status='failed' WHERE id=%s", (run_id,))
        workspace.schedule(conn, run_id, revision, "repair")
        conn.execute("UPDATE curation_workspace_jobs SET status='failed',error_code='quota'")
    workspace.retry_repair(revision)
    with psycopg.connect(studio_database) as conn:
        assert conn.execute("SELECT count(*) FROM curation_workspace_jobs").fetchone()[0] == 1
        assert conn.execute("SELECT status FROM curation_workspace_jobs").fetchone()[0] == 'queued'
        conn.execute("UPDATE curation_workspace_jobs SET status='failed',error_code='interrupted',result=%s", (Json({'successor_revision_id':revision}),))
    with pytest.raises(ValueError, match='no interrupted'):
        workspace.retry_repair(revision)
