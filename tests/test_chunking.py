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


def test_chunk_real_kb() -> None:
    chunks = chunk_normalized_dir()
    assert len(chunks) > 10
    # Each department-specific rule set should surface as its own chunk.
    assert any("Mechanical" in c.section for c in chunks)
    assert all(c.source_doc.endswith(".md") for c in chunks)
    assert all(c.id for c in chunks)
