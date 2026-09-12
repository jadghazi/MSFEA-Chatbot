"""Keep the synthesis suite useful and the experiment comparisons attributable."""

import json
from pathlib import Path

from eval.loader import GoldenItem
from eval.synthesis_report import premise_hits
from msfea_bot.ingestion.chunking import chunk_normalized_dir


def test_synthesis_cases_have_sources_qualities_and_distinct_intents() -> None:
    root = Path(__file__).resolve().parents[1]
    cases = [json.loads(line) for line in (root / "eval/synthesis_set.jsonl").read_text().splitlines()]
    assert 8 <= len(cases) <= 12
    assert len({case["id"] for case in cases}) == len(cases)
    chunks = [c.text for c in chunk_normalized_dir()]
    for case in cases:
        GoldenItem.model_validate(case)
        assert case["expected_answer_or_behavior"]
        if not case["should_refuse"]:
            assert case["evidence_all"]
            assert all(any(e.lower() in c.lower() for c in chunks) for e in case["evidence_all"])
    assert sum(bool(c.get("history")) for c in cases) >= 3
    assert any("multi-hop" in c["tags"] for c in cases)
    assert any("comparison" in c["tags"] for c in cases)
    assert any(c["should_refuse"] and "why" in c["tags"] for c in cases)


def test_comparison_probe_accepts_equivalent_eight_week_source() -> None:
    row = {
        "id": "s06-comparison",
        "evidence_required": ["over-specific eight-week quote", "no longer required"],
        "chunks": [{"text": "Internship minimum duration: **8 weeks**"}],
    }
    assert premise_hits(row) == [True, False]


def test_followup_regression_cases_are_valid_and_source_grounded() -> None:
    root = Path(__file__).resolve().parents[1]
    cases = [json.loads(line) for line in
             (root / "eval/followup_set.jsonl").read_text(encoding="utf-8").splitlines()]
    chunks = [c.text for c in chunk_normalized_dir()]
    assert len(cases) == 9
    for case in cases:
        GoldenItem.model_validate(case)
        assert all(any(e.lower() in c.lower() for c in chunks) for e in case["evidence_all"])
