"""Tests for the department registry (B-1 / B-2).

The important one is `test_contacts_match_the_knowledge_base`: the registry is a
hand-maintained copy of data that lives in the KB, so it needs a tripwire against
drift. If someone updates a coordinator in the source document, this fails.
"""

from __future__ import annotations

from pathlib import Path

from msfea_bot.departments import (
    DEPARTMENTS,
    GENERAL_CONTACT,
    contact_for,
    describe,
    from_code,
    from_heading,
)

GUIDELINES = (
    Path(__file__).resolve().parents[1]
    / "kb"
    / "normalized"
    / "summer-training-guidelines-2026.md"
)


def test_contacts_match_the_knowledge_base() -> None:
    """Every address and coordinator here must still exist in the source document."""
    kb = GUIDELINES.read_text(encoding="utf-8")
    for dept in DEPARTMENTS:
        assert dept.contact_email in kb, f"{dept.code}: {dept.contact_email} not in the KB"
        assert dept.contact_name in kb, f"{dept.code}: {dept.contact_name} not in the KB"
    assert GENERAL_CONTACT in kb


def test_every_department_has_a_rules_section() -> None:
    """Each department we offer must actually have rules in the KB to scope to."""
    kb = GUIDELINES.read_text(encoding="utf-8")
    for dept in DEPARTMENTS:
        assert f"({dept.abbr})" in kb, f"no '### ... ({dept.abbr})' section in the KB"


def test_from_code_is_case_insensitive_and_safe() -> None:
    assert from_code("mech") is not None
    assert from_code("MECH") is not None
    assert from_code("  Cee  ") is not None
    # Untrusted input from the browser must not resolve to a department.
    assert from_code("") is None
    assert from_code(None) is None
    assert from_code("../../etc/passwd") is None
    assert from_code("physics") is None


def test_from_heading_matches_the_kb_style() -> None:
    assert from_heading("### Mechanical Engineering (MECH)").code == "mech"  # type: ignore[union-attr]
    assert from_heading("### Civil and Environmental Engineering (CEE)").code == "cee"  # type: ignore[union-attr]
    # General sections must not be tagged, even when they name departments.
    assert from_heading("## Department Contacts") is None
    assert from_heading("## Internship Requirements") is None


def test_contact_routing_falls_back_to_the_cdc() -> None:
    assert contact_for("ece") == "rd39@aub.edu.lb"
    assert contact_for(None) == GENERAL_CONTACT
    assert contact_for("not-a-department") == GENERAL_CONTACT


def test_describe() -> None:
    assert describe("iem") == "Industrial Engineering and Management (IEM)"
    assert describe(None) is None
