"""Scope and policy boundaries from the completed 2026-09-27 faculty review."""

from msfea_bot.ingestion.chunking import chunk_normalized_dir


def test_shared_faq_rules_are_retrievable_for_every_department() -> None:
    chunks = chunk_normalized_dir()
    for evidence in (
        "Use double spacing, size 12 font",
        "one Final Report that clearly separates",
        "If an early letter is accepted",
        "Only with course-team approval",
        "may have to complete at least ten weeks",
        "All internship departments require the student internship survey",
        "Count internship weeks from your own approved internship start date",
        "No fixed template is normally required",
        "Check the activity-completion requirements",
    ):
        matches = [chunk for chunk in chunks if evidence in chunk.text]
        assert matches, evidence
        assert {chunk.metadata["department"] for chunk in matches} == {"all"}


def test_report_length_and_mech_research_keep_department_boundaries() -> None:
    chunks = chunk_normalized_dir()
    limits = [chunk for chunk in chunks if "at least five pages and 1,500 words" in chunk.text]
    assert limits and {chunk.metadata["department"] for chunk in limits} == {"ece"}
    research = [chunk for chunk in chunks if "research includes hands-on engineering work" in chunk.text]
    assert research and {chunk.metadata["department"] for chunk in research} == {"mech"}
    assert not any("not a MECH completion option" in chunk.text for chunk in chunks)
    assert any("cannot be split into two separate 4-week periods" in chunk.text for chunk in chunks)


def test_coop_letter_is_additional_and_stays_in_coop_program() -> None:
    matches = [chunk for chunk in chunk_normalized_dir() if "does not replace either form" in chunk.text]
    assert matches
    assert {chunk.metadata["department"] for chunk in matches} == {"all"}
    assert {chunk.metadata["program"] for chunk in matches} == {"co-op"}
