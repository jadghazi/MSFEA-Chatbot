"""Evidence packets and publication tests follow the student RAG contract."""

from __future__ import annotations

import json
from types import SimpleNamespace

from msfea_bot.curation import assistance, validation
from msfea_bot.retrieval.store import RetrievedChunk
import test_studio_assistance

studio_database = test_studio_assistance.studio_database
_publication_database = test_studio_assistance._publication_database


def test_staff_comparison_restores_conditions_without_student_scope_exclusions(monkeypatch):
    general = RetrievedChunk("base", "General placement rule.", "rules.md", "Placement", 0.8,
                             {"department": "all", "program": "coop", "process_stage": "entry"})
    exception = RetrievedChunk("exception", "ECE requires prior approval.", "rules.md", "ECE condition", 0.55,
                               {"department": "ece", "program": "coop", "process_stage": "entry", "retrieval_role": "companion"})
    monkeypatch.setattr(validation, "search", lambda *_args, **_kwargs: [general])
    calls = []

    def expand(seeds, query, department, **kwargs):
        calls.append((department, kwargs))
        return seeds + [exception]

    monkeypatch.setattr(validation, "expand_evidence_links", expand)
    evidence, _ = validation.review_candidates("Placement approval?", "Prior approval is needed.", "ece")
    assert [item["id"] for item in evidence] == [general.id, exception.id]
    assert all(item["program"] == "coop" and item["process_stage"] == "entry" for item in evidence)
    assert all(department is None and "excluded_stages" not in kwargs for department, kwargs in calls)


def test_staff_prompt_keeps_scope_labels_through_sanitization(studio_database, monkeypatch):
    evidence = [{**test_studio_assistance.EVIDENCE[0], "program": "internship", "process_stage": "completion"}]
    monkeypatch.setattr(assistance, "review_candidates", lambda *_args, **_kwargs: (evidence, []))
    packet = assistance._evidence(test_studio_assistance.INTAKE)
    assert packet[0]["program"] == "internship" and packet[0]["process_stage"] == "completion"
    data = json.loads(assistance.build_prompt(test_studio_assistance.INTAKE, packet).split("DATA:\n", 1)[1])
    assert data["existing_passages"][0]["process_stage"] == "completion"


def test_positive_retrieval_requires_candidate_in_final_answer_context(monkeypatch):
    revision = SimpleNamespace(id=1, representative_question="When is advising?", paraphrase_question=None,
                               department="all", expected_evidence="Thursday")
    dominant = RetrievedChunk("existing", "Wednesday advising.", "existing", "Advising", 0.95,
                              {"source_kind": "admin_authored", "entry_id": "2"})
    candidate = RetrievedChunk("candidate-1", "Thursday advising.", "candidate", "Advising", 0.65,
                               {"source_kind": "admin_authored", "entry_id": "1"})
    monkeypatch.setattr(validation, "_candidate_ids", lambda _revision: {candidate.id})
    monkeypatch.setattr(assistance, "original_question", lambda _revision: None)
    monkeypatch.setattr(assistance, "prepared_questions", lambda _revision: [])
    calls = []

    def retrieve(question, k, department, history, database_url):
        calls.append((department, history, database_url))
        return [dominant, candidate]

    monkeypatch.setattr(validation, "retrieve_context", retrieve)
    passed, details = validation._positive_retrieval(revision, "isolated-candidate")
    assert not passed
    assert details["cases"][0]["retrieved_ids"] == [dominant.id]
    assert not details["cases"][0]["candidate_hit"]
    assert calls == [(None, None, "isolated-candidate")]
