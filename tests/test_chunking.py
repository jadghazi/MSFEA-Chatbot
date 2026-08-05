"""Tests for the walking-skeleton chunker."""

from msfea_bot.ingestion.chunking import (
    chunk_markdown,
    chunk_normalized_dir,
    parse_frontmatter,
)


def test_parse_frontmatter() -> None:
    meta, body = parse_frontmatter("---\ntitle: X\nsource: y.docx\n---\n\n# Head\nbody")
    assert meta["title"] == "X"
    assert meta["source"] == "y.docx"
    assert body.startswith("# Head")


def test_parse_frontmatter_absent() -> None:
    meta, body = parse_frontmatter("# Head\nbody")
    assert meta == {}
    assert body.startswith("# Head")


def test_chunk_splits_on_headings() -> None:
    md = "---\ntitle: Doc\n---\n# Doc\nintro\n## A\naaa\n## B\nbbb"
    chunks = chunk_markdown(md, "doc.md")
    sections = [c.section for c in chunks]
    assert "A" in sections
    assert "B" in sections
    for c in chunks:
        assert c.source_doc == "doc.md"
        assert c.text.strip()


def test_large_section_is_windowed_with_heading() -> None:
    body = "\n".join(f"line {i} " + "x" * 40 for i in range(60))
    md = f"---\ntitle: Doc\n---\n## Big Section\n{body}"
    chunks = chunk_markdown(md, "doc.md", max_chars=300, overlap=50)
    assert len(chunks) > 1, "oversized section should be split into multiple windows"
    assert all(c.section == "Big Section" for c in chunks)
    assert all("## Big Section" in c.text for c in chunks), "each window keeps its heading"
    assert all(len(c.text) <= 300 + 150 for c in chunks), "windows are roughly bounded"


def test_small_section_stays_one_chunk() -> None:
    md = "---\ntitle: Doc\n---\n## Small\nshort content"
    chunks = chunk_markdown(md, "doc.md", max_chars=500, overlap=100)
    assert len(chunks) == 1


TABLE_MD = """---
title: Doc
---
## Deliverables
| Timeline | Deliverable | Where |
| --- | --- | --- |
""" + "\n".join(
    f"| Week {i} | Deliverable number {i} with a fairly long description | Moodle |"
    for i in range(1, 25)
)


def test_tables_are_never_split_across_chunks() -> None:
    """A table is one unit of meaning and must survive windowing intact.

    Supersedes the older display_prefix behaviour, which patched the header back
    onto mid-table windows. Splitting was the real defect: on the real KB the 9-row
    deliverables table became 6 near-identical chunks that competed for the same
    top-k slots, the fragment holding the "Progress Report" row ranked 18th, and
    that deliverable silently disappeared from the answer. Keeping the table whole
    took the answer from 6/9 rows to 9/9.
    """
    # max_chars far below the table's size — it must still come back whole.
    chunks = chunk_markdown(TABLE_MD, "doc.md", max_chars=120, overlap=40)

    holding = [c for c in chunks if "| Timeline | Deliverable | Where |" in c.text]
    assert len(holding) == 1, "the table header must appear in exactly one chunk"

    body_rows = [
        line
        for line in TABLE_MD.splitlines()
        if line.startswith("|") and "---" not in line and "Timeline |" not in line
    ]
    assert body_rows, "fixture should contain table body rows"
    for row in body_rows:
        owners = [c for c in chunks if row in c.text]
        assert len(owners) == 1, f"row split or duplicated across chunks: {row!r}"
        assert owners[0] is holding[0], f"row separated from its header: {row!r}"

    # Kept whole even though that pushes the chunk past max_chars — deliberate.
    assert len(holding[0].text) > 120


def test_first_table_window_needs_no_prefix() -> None:
    """The window containing the real header shouldn't duplicate it."""
    chunks = chunk_markdown(TABLE_MD, "doc.md", max_chars=400, overlap=100)
    assert chunks[0].display_prefix == ""


def test_display_prefix_is_inserted_after_the_heading() -> None:
    from msfea_bot.retrieval.store import _with_display_prefix

    text = "## Deliverables\n| Week 9 | Report | Moodle |"
    out = _with_display_prefix(text, "| Timeline | Deliverable | Where |")
    assert out.splitlines()[0] == "## Deliverables", "heading stays first"
    assert out.splitlines()[1] == "| Timeline | Deliverable | Where |"
    # Curated chunks have no heading: prefix goes on top rather than being buried.
    assert _with_display_prefix("Q: x\nA: y", "| H |").startswith("| H |")
    assert _with_display_prefix("no prefix", "") == "no prefix"


def test_chunk_real_kb() -> None:
    chunks = chunk_normalized_dir()
    assert len(chunks) > 10
    # Each department-specific rule set should surface as its own chunk.
    assert any("Mechanical" in c.section for c in chunks)
    assert all(c.source_doc.endswith(".md") for c in chunks)
    assert all(c.id for c in chunks)
