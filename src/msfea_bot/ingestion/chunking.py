"""Section-aware chunking (CLAUDE.md §5.4).

Splits a normalized Markdown document at headings (level >= 2), then further
splits any oversized section into smaller overlapping windows so that specific
facts (e.g. "75%") get focused embeddings instead of being diluted inside a large
section. Each sub-chunk keeps its section heading for context. Window size and
overlap are tuned against the eval set (context-recall).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

NORMALIZED_DIR = Path(__file__).resolve().parents[3] / "kb" / "normalized"

# Defaults chosen by measuring context-recall on the golden set (see ADR-0006):
# 500 is the largest window that still reaches 100% context-recall@5.
DEFAULT_MAX_CHARS = 500
DEFAULT_OVERLAP = 150


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


def split_windows(text: str, max_chars: int, overlap: int) -> list[str]:
    """Split text into <=max_chars windows on line boundaries, with overlap.

    Returns [text] unchanged when it already fits.

    Splits only on newlines, so a run-on paragraph with no line breaks comes back
    as one oversized window — callers feeding free-form text (see
    curation.service) must introduce line boundaries first.

    Public because curated answers are windowed with the same rules as KB content
    (ADR-0013); `chunk_markdown` is the KB-side caller.
    """
    if len(text) <= max_chars:
        return [text]
    windows: list[str] = []
    current: list[str] = []
    length = 0
    for line in text.split("\n"):
        if length + len(line) + 1 > max_chars and current:
            windows.append("\n".join(current))
            # Keep trailing lines (~overlap chars) as the start of the next window.
            kept: list[str] = []
            kept_len = 0
            for prev in reversed(current):
                if kept_len + len(prev) + 1 > overlap:
                    break
                kept.insert(0, prev)
                kept_len += len(prev) + 1
            current = kept
            length = kept_len
        current.append(line)
        length += len(line) + 1
    if current:
        windows.append("\n".join(current))
    return windows


def chunk_markdown(
    md: str,
    source_doc: str,
    max_chars: int = DEFAULT_MAX_CHARS,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Chunk]:
    """Split one Markdown document into section chunks (oversized sections windowed)."""
    meta, body = parse_frontmatter(md)
    section = meta.get("title", source_doc)
    chunks: list[Chunk] = []
    buffer: list[str] = []

    def flush() -> None:
        text = "\n".join(buffer).strip()
        if not text:
            return
        heading = buffer[0] if buffer and _heading_level(buffer[0]) >= 2 else f"## {section}"
        for window in split_windows(text, max_chars, overlap):
            # Ensure every window carries its section heading for context.
            window_text = window if window.lstrip().startswith(heading) else f"{heading}\n{window}"
            chunks.append(
                Chunk(
                    id=f"{source_doc}#{len(chunks):02d}-{_slug(section)}",
                    text=window_text,
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


def chunk_file(
    path: Path, max_chars: int = DEFAULT_MAX_CHARS, overlap: int = DEFAULT_OVERLAP
) -> list[Chunk]:
    """Chunk a single normalized Markdown file."""
    return chunk_markdown(path.read_text(encoding="utf-8"), path.name, max_chars, overlap)


def chunk_normalized_dir(
    directory: Path = NORMALIZED_DIR,
    max_chars: int = DEFAULT_MAX_CHARS,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Chunk]:
    """Chunk every ``*.md`` file in the normalized KB directory."""
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        chunks.extend(chunk_file(path, max_chars, overlap))
    return chunks
