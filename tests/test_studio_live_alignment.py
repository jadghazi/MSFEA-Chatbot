"""Opt-in bounded live staff smoke; private disposable DB, never publication."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from msfea_bot.config import settings
from msfea_bot.curation import assistance, suggestions
from msfea_bot.llm import LLMRateLimitError, get_curation_provider
from msfea_bot.retrieval.store import indexed_generation
import test_studio_assistance

studio_database = test_studio_assistance.studio_database
_publication_database = test_studio_assistance._publication_database


@pytest.mark.skipif(os.getenv("STUDIO_LIVE_ALIGNMENT") != "1", reason="Live Gemini smoke is opt-in")
def test_live_claim_comparison_and_source_backed_suggestion(studio_database, monkeypatch):
    assert settings.curation_llm_model == "gemini-3.1-flash-lite", "Reprice the live smoke budget before changing its model."
    artifact = Path(os.getenv("STUDIO_LIVE_RECEIPT", "eval/results/studio_alignment_live_20261008.json"))
    records = []
    reserved = 0.0

    def factory(schema, model=None, before_request=None):
        provider = get_curation_provider(schema, model=model)
        cost = 0.0

        def admission():
            nonlocal reserved
            if reserved + cost > 0.20 or sum(item.get("attempt", 0) for item in records) >= 12:
                raise LLMRateLimitError("Bounded live smoke allowance used")
            reserved += cost
            records.append({"model": settings.curation_llm_model, "attempt": 1, "reserved_usd": cost})
            if before_request:
                before_request()

        provider._before_request = admission

        def generate(prompt):
            nonlocal cost
            # Official standard Lite prices; reserve output including reasoning.
            cost = (provider.count_input_tokens(prompt) * 0.25 + 6144 * 1.50) / 1_000_000
            result = provider.generate(prompt)
            records.append({"schema": schema["title"], "result": asdict(result)})
            artifact.write_text(json.dumps({"records": records, "reserved_upper_bound_usd": reserved}, indent=2), encoding="utf-8")
            return result

        return SimpleNamespace(generate=generate)

    monkeypatch.setattr(assistance, "get_curation_provider", factory)
    monkeypatch.setattr(suggestions, "get_curation_provider", factory)
    monkeypatch.setattr(assistance, "_evidence", lambda *_args, **_kw: test_studio_assistance.EVIDENCE)
    before = indexed_generation()
    try:
        # Full existing four-call review: compare two incompatible service schedules.
        review_id = assistance.enqueue(test_studio_assistance.INTAKE, uuid4().hex)
        assert assistance.process_next()
        review = assistance.get_review(review_id)
        assert review["status"] == "completed", review.get("error_code")
        assert review["report"]["classification"] in {"direct_conflict", "supersedes", "potential_conflict"}
        assert review["report"]["requires_decision"]
        assert review["report"]["findings"][0]["proposed_claim"] == test_studio_assistance.GUIDANCE
        # Two-call writing flow stays available during conflict, using KB facts.
        suggestion_id = suggestions.enqueue(review_id, None, uuid4().hex)
        assert assistance.process_next()
        suggested = suggestions.get(suggestion_id)
        assert suggested["status"] == "completed", suggested.get("error_code")
        report = suggested["report"]
        assert "Wednesday" in report["suggested_answer"]
        assert "Thursday" not in report["suggested_answer"]
        assert report["claim_changes"] and report["claim_changes"][0]["sources"]
        assert not report["verification"].get("unsupported_sentences")
        records.append({"review": review["report"], "suggestion": report, "index_unchanged": indexed_generation() == before})

        # A related placement rule must not contradict a later-career-support claim.
        intake = assistance.Intake(guidance="After CO-OP completion, the CDC provides career support.",
                                   question="Can I get career support after CO-OP?", department="ece", programs=["coop"])
        evidence = [{"id": "placement", "text": "CO-OP admission does not guarantee a placement.",
                     "source_doc": "synthetic-test.md", "section": "Placement", "department": "all",
                     "program": "coop", "process_stage": "entry", "entry_id": None}]
        result = factory(assistance.ReviewReport.model_json_schema()).generate(assistance.build_prompt(intake, evidence))
        comparison = assistance.checked_report(result.text, intake, evidence)
        assert comparison["classification"] in {"new_information", "complementary"}
        assert not comparison["requires_decision"]
        records.append({"stage_comparison": comparison, "passed": True})
    finally:
        artifact.write_text(json.dumps({"records": records, "reserved_upper_bound_usd": reserved}, indent=2), encoding="utf-8")
    assert indexed_generation() == before
