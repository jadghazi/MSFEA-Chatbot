"""Tests for question anonymization (CLAUDE.md §7)."""

import pytest

from msfea_bot.observability.privacy import _ner, anonymize


def test_strips_email() -> None:
    out = anonymize("please email me at jad.ghazi@aub.edu.lb thanks")
    assert "@" not in out
    assert "[redacted-email]" in out


def test_strips_student_id_and_phone() -> None:
    assert "202012345" not in anonymize("my id is 202012345")
    assert "70123456" not in anonymize("call me on 70 123 456")


def test_preserves_domain_numbers() -> None:
    out = anonymize("8 weeks, 3.3 GPA, 75%, FEAA 500, 2-3 weeks")
    for keep in ["8 weeks", "3.3", "75%", "500", "2-3"]:
        assert keep in out, f"anonymize wrongly stripped '{keep}'"


def test_plain_question_unchanged() -> None:
    q = "How many credits is the internship?"
    assert anonymize(q) == q


def test_redacts_person_name() -> None:
    if _ner() is None:
        pytest.skip("spaCy NER model not installed")
    out = anonymize("Hi, my name is Sara Khoury and I need help with my internship.")
    assert "Sara Khoury" not in out
    assert "[redacted-name]" in out
