"""Crude section-based chunking for the walking skeleton (CLAUDE.md §5.3).

Splits a normalized Markdown document into chunks at Markdown headings
(level >= 2), carrying the source doc and section as metadata. This is
intentionally simple — proper semantic chunking (overlap, tuned against the eval
set) is Phase 4. It is good enough here because our normalized docs already have
clean section headings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

NORMALIZED_DIR = Path(__file__).resolve().parents[3] / "kb" / "normalized"


@dataclass
class Chunk:
    """One retrievable passage plus where it came from."""

    id: str
    text: str
    source_doc: str
    section: str
    metadata: dict[str, str] = field(default_factory=dict)


def parse_frontmatter(md: str) -> tuple[dict[str, str], str]:
    """Split a leading ``---`` YAML-ish frontmatter block from the body.

    Only simple ``key: value`` lines are parsed (enough for our frontmatter);
    returns ``({}, md)`` when there is no frontmatter.
    """
    if not md.startswith("---"):
        return {}, md
    end = md.find("\n---", 3)
    if end == -1:
        return {}, md
    block = md[3:end].strip()
    body = md[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, body


def _heading_level(line: str) -> int:
    """Markdown heading level (1 for ``# x``, 2 for ``## x`` ...); 0 if not a heading."""
    stripped = line.lstrip("#")
    level = len(line) - len(stripped)
    if level > 0 and stripped.startswith(" "):
        return level
    return 0


def _slug(text: str) -> str:
    lowered = text.lower().replace(" ", "-")
    return "".join(c for c in lowered if c.isalnum() or c == "-")[:50]


def chunk_markdown(md: str, source_doc: str) -> list[Chunk]:
    """Split one Markdown document into section chunks."""
    meta, body = parse_frontmatter(md)
    section = meta.get("title", source_doc)
    chunks: list[Chunk] = []
    buffer: list[str] = []

    def flush() -> None:
        text = "\n".join(buffer).strip()
        if text:
            chunks.append(
                Chunk(
                    id=f"{source_doc}#{len(chunks):02d}-{_slug(section)}",
                    text=text,
                    source_doc=source_doc,
                    section=section,
                    metadata=meta,
                )
            )

    for line in body.splitlines():
        if _heading_level(line) >= 2:
            flush()
            section = line.lstrip("#").strip()
            buffer = [line]
        else:
            buffer.append(line)
    flush()
    return chunks


def chunk_file(path: Path) -> list[Chunk]:
    """Chunk a single normalized Markdown file."""
    return chunk_markdown(path.read_text(encoding="utf-8"), path.name)


def chunk_normalized_dir(directory: Path = NORMALIZED_DIR) -> list[Chunk]:
    """Chunk every ``*.md`` file in the normalized KB directory."""
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        chunks.extend(chunk_file(path))
    return chunks
