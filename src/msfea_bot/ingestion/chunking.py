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
    """One retrievable passage plus where it came from.

    `text` is the retrieval text: it is what gets embedded *and* what the full-text
    index is built from. `display_prefix` is context shown to the reader/LLM but
    deliberately kept out of both — currently the header row of a table whose body
    was split across windows.

    Keeping them separate is not fussiness, it was measured. Folding a table header
    into `text` cost context-recall@5 (97% -> 93%), because the same boilerplate then
    competes with the facts in every window of that table; letting it reach the
    full-text column cost context-recall@1 (90% -> 83%) by shifting keyword ranks.
    Prepending at read time gives the reader the column labels at zero retrieval cost.
    """

    id: str
    text: str
    source_doc: str
    section: str
    metadata: dict[str, str] = field(default_factory=dict)
    display_prefix: str = ""


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


def _window_spans(lines: list[str], max_chars: int, overlap: int) -> list[tuple[int, int]]:
    """Half-open [start, end) line spans for each window.

    Spans rather than strings so callers can tell *where* a window starts — needed
    to repair markdown tables split across windows (see `_table_headers`).
    """
    spans: list[tuple[int, int]] = []
    start = 0
    length = 0
    for i, line in enumerate(lines):
        if length + len(line) + 1 > max_chars and i > start:
            spans.append((start, i))
            # Step back so the next window repeats ~overlap chars of trailing lines.
            kept = 0
            j = i
            while j > start and kept + len(lines[j - 1]) + 1 <= overlap:
                j -= 1
                kept += len(lines[j]) + 1
            start = j
            length = kept
        length += len(line) + 1
    if start < len(lines):
        spans.append((start, len(lines)))
    return spans


def _is_table_row(line: str) -> bool:
    return line.strip().startswith("|")


def _is_table_separator(line: str) -> bool:
    """A markdown header underline like ``|---|:---:|``."""
    stripped = line.strip()
    return (
        stripped.startswith("|")
        and "-" in stripped
        and set(stripped) <= set("|-: \t")
    )


def _table_headers(lines: list[str]) -> dict[int, tuple[str, str]]:
    """Map each table *body* line index to its (header, separator) rows.

    A window that starts inside a table body would otherwise present bare columns
    with no labels — the reader (and the model) can't tell a deadline column from a
    submission-channel column.
    """
    headers: dict[int, tuple[str, str]] = {}
    for i in range(len(lines) - 1):
        if _is_table_row(lines[i]) and _is_table_separator(lines[i + 1]):
            j = i + 2
            while j < len(lines) and _is_table_row(lines[j]):
                headers[j] = (lines[i], lines[i + 1])
                j += 1
    return headers


def split_windows(text: str, max_chars: int, overlap: int) -> list[str]:
    """Split text into <=max_chars windows on line boundaries, with overlap.

    Returns [text] unchanged when it already fits.

    Splits only on newlines, so a run-on paragraph with no line breaks comes back
    as one oversized window — callers feeding free-form text (see
    curation.service) must introduce line boundaries first.

    Public because curated answers are windowed with the same rules as KB content
    (ADR-0013); `chunk_markdown` is the KB-side caller. Note this plain form does
    not repair split tables — that is markdown-specific and lives in
    `chunk_markdown`.
    """
    if len(text) <= max_chars:
        return [text]
    lines = text.split("\n")
    return ["\n".join(lines[a:b]) for a, b in _window_spans(lines, max_chars, overlap)]


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
        lines = text.split("\n")
        spans = (
            [(0, len(lines))]
            if len(text) <= max_chars
            else _window_spans(lines, max_chars, overlap)
        )
        table_headers = _table_headers(lines)

        def with_heading(body_lines: list[str]) -> str:
            joined = "\n".join(body_lines)
            # Ensure every window carries its section heading for context.
            return joined if joined.lstrip().startswith(heading) else f"{heading}\n{joined}"

        for start, end in spans:
            # A window starting inside a table body has lost its column labels, so a
            # reader sees bare columns. Carry the header as a *display prefix* only —
            # it must not enter `text`, which is both embedded and full-text indexed.
            carried = table_headers.get(start)
            chunks.append(
                Chunk(
                    id=f"{source_doc}#{len(chunks):02d}-{_slug(section)}",
                    text=with_heading(lines[start:end]),
                    source_doc=source_doc,
                    section=section,
                    metadata=meta,
                    display_prefix="\n".join(carried) if carried is not None else "",
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
