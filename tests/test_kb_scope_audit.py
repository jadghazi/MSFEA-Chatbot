"""Frozen scope/provenance invariants for the publication guard (Step 1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from msfea_bot.departments import DEPARTMENTS
from msfea_bot.ingestion.chunking import chunk_normalized_dir, parse_frontmatter


ROOT = Path(__file__).resolve().parents[1]
EMAIL_SOURCE = ROOT / "kb" / "source" / "email-clarifications.md"
EMAIL_NORMALIZED = ROOT / "kb" / "normalized" / "email-clarifications.md"

SCOPED_POLICY_EVIDENCE = {
    "mech": "Internships cannot be split into two separate 4-week periods",
    "ece": "six company weeks and two faculty-research weeks",
    "chem": "A recorded 3-minute presentation is required",
    "iem": "Final presentations are generally not required unless specified",
    "cee": "at least one period is in civil or construction engineering",
}


def test_every_normalized_chunk_has_explicit_department_and_program() -> None:
    """Missing scope must not silently become general during retrieval."""
    chunks = chunk_normalized_dir()
    allowed_departments = {"all", *(department.code for department in DEPARTMENTS)}

    assert chunks
    assert not [chunk.id for chunk in chunks if chunk.metadata.get("department") not in allowed_departments]
    assert not [chunk.id for chunk in chunks if not chunk.metadata.get("program")]


@pytest.mark.parametrize("department, evidence", SCOPED_POLICY_EVIDENCE.items())
def test_each_department_has_explicitly_scoped_policy_evidence(
    department: str, evidence: str
) -> None:
    """Exercise all five departments, not only the historically common ECE cases."""
    matches = [chunk for chunk in chunk_normalized_dir() if evidence in chunk.text]

    assert matches, f"missing reviewed policy fixture for {department}"
    assert {chunk.metadata.get("department") for chunk in matches} == {department}


@pytest.mark.parametrize("path", [EMAIL_SOURCE, EMAIL_NORMALIZED])
def test_email_clarifications_have_reviewable_provenance(path: Path) -> None:
    metadata, _ = parse_frontmatter(path.read_text(encoding="utf-8"))

    assert metadata["department"] == "all"
    assert metadata["program"] == "internship"
    assert metadata["last_updated"] == "2026-09"
    assert metadata["source_id"] == "approved-internship-email-clarifications"
    assert metadata["source_type"] == "approved_clarification"
    assert metadata["approval_reference"] == "project-review-2026-09"


@pytest.mark.xfail(
    strict=True,
    reason="Step 3 draft semantics must replace legacy unscoped direct publication",
)
def test_legacy_curated_chunks_are_not_publishable_without_explicit_scope() -> None:
    """Keep the current direct-curation defect visible until the revision migration."""
    from msfea_bot.curation.service import _to_chunks

    chunks = _to_chunks(1, "Can I split the internship?", "Yes for this department.", "admin")

    assert all(chunk.metadata.get("department") in SCOPED_POLICY_EVIDENCE for chunk in chunks)
    assert all(chunk.metadata.get("program") for chunk in chunks)
