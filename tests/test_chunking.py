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


def test_chunk_real_kb() -> None:
    chunks = chunk_normalized_dir()
    assert len(chunks) > 10
    # Each department-specific rule set should surface as its own chunk.
    assert any("Mechanical" in c.section for c in chunks)
    assert all(c.source_doc.endswith(".md") for c in chunks)
    assert all(c.id for c in chunks)
