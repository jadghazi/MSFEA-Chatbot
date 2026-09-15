"""Unit tests for curated-answer windowing used only after guarded publication."""


LONG_ANSWER = (
    "Students must submit the Notice of Arrival form during the first week. " * 100
) + "The very last deadline is the final Friday of September."


def test_long_curated_answer_is_windowed_not_truncated() -> None:
    """A long answer must be split, not silently half-indexed (ADR-0013).

    Written as one run-on paragraph on purpose: that is what the dashboard textarea
    produces, and it is the case the plain windower cannot split on its own.
    """
    from msfea_bot.curation.service import _to_chunks

    chunks = _to_chunks(7, "How do I submit my internship forms?", LONG_ANSWER, "admin")

    assert len(chunks) > 1, "an 8000-char answer must not stay a single chunk"
    # The tail is the point: before windowing, everything past ~3,143 chars was
    # stored but unreachable, because the embedding model truncates at 512 tokens.
    assert any("final Friday of September" in c.text for c in chunks), "tail must be indexed"
    assert all(c.text.startswith("Q: How do I submit") for c in chunks), (
        "every window keeps the question, so each chunk is self-describing"
    )
    assert all(len(c.text) < 1200 for c in chunks), "windows stay well inside the token limit"
    assert len({c.id for c in chunks}) == len(chunks), "ids must be unique"


def test_curated_chunk_ids_are_prefix_delete_safe() -> None:
    """`curated-1-` must not also match `curated-10-` — the original footgun."""
    from msfea_bot.curation.service import _chunk_id

    assert not _chunk_id(10, 0).startswith("curated-1-")
    assert _chunk_id(1, 0).startswith("curated-1-")


def test_short_curated_answer_stays_one_chunk() -> None:
    from msfea_bot.curation.service import _to_chunks

    chunks = _to_chunks(3, "How many credits?", "The internship is 3 credits.", "admin")
    assert len(chunks) == 1
    assert chunks[0].id == "curated-3-00"
