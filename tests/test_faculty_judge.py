"""A model judge cannot silently promote uncertain or incomplete answers."""

from __future__ import annotations

import json

import pytest

from eval.faculty_judge import _parse_batch, _parse_judgment


def _verdict(**updates: object) -> str:
    payload: dict[str, object] = {
        "retrieval_sufficient": True,
        "policy_correct": True,
        "conditions_complete": True,
        "grounded": True,
        "relevant": True,
        "refusal_appropriate": True,
        "uncertain": False,
        "reason": "supported",
    }
    payload.update(updates)
    return json.dumps(payload)


def test_incomplete_or_uncertain_cannot_pass_answer_accuracy() -> None:
    assert _parse_judgment(_verdict())["overall_correct"] is True
    assert _parse_judgment(_verdict(conditions_complete=False))["overall_correct"] is False
    assert _parse_judgment(_verdict(uncertain=True))["overall_correct"] is False


def test_missing_retrieval_judgment_is_rejected() -> None:
    incomplete = json.loads(_verdict())
    del incomplete["retrieval_sufficient"]
    with pytest.raises(ValueError, match="retrieval_sufficient"):
        _parse_judgment(json.dumps(incomplete))


def test_batch_requires_every_requested_case() -> None:
    first = json.loads(_verdict())
    first["id"] = "one"
    second = json.loads(_verdict(conditions_complete=False))
    second["id"] = "two"
    parsed = _parse_batch(json.dumps({"judgments": [first, second]}), ["one", "two"])
    assert parsed["one"]["overall_correct"] is True
    assert parsed["two"]["overall_correct"] is False
    with pytest.raises(ValueError, match="IDs differ"):
        _parse_batch(json.dumps({"judgments": [first, second]}), ["one", "three"])
    first.pop("id")
    second.pop("id")
    positional = _parse_batch(json.dumps({"judgments": [first, second]}), ["one", "two"])
    assert positional["two"]["overall_correct"] is False
    second["id"] = "two"
    with pytest.raises(ValueError, match="IDs differ"):
        _parse_batch(json.dumps({"judgments": [first, second]}), ["one", "two"])
