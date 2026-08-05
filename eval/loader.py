"""Load and validate the golden set (`golden_set.jsonl`).

One JSON object per line. Fields follow CLAUDE.md §4 (`question`,
`expected_answer_or_behavior`, `source_doc`, `should_refuse`) plus a few helpers
(`id`, `source_section`, `tags`, `is_synthetic`, `notes`).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, model_validator

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.jsonl"


class GoldenItem(BaseModel):
    """One golden-set case: a question paired with the expected outcome."""

    id: str
    question: str
    expected_answer_or_behavior: str
    should_refuse: bool
    source_doc: str | None = None
    source_section: str | None = None
    # A verbatim fact that must appear in retrieved context for the question to be
    # answerable (used by the context-recall retrieval metric). None for refusals.
    evidence: str | None = None
    # The asking student's department, for cases where the correct answer depends on
    # it (ADR-0015). None = a general question, asked with no department set — which
    # is also how every pre-existing case keeps its original meaning.
    department: str | None = None
    tags: list[str] = []
    is_synthetic: bool = False
    notes: str | None = None

    @model_validator(mode="after")
    def _check_source_matches_behavior(self) -> GoldenItem:
        # Answerable questions must point at a source doc; refusals must not
        # (the answer is "escalate", there is no grounding document).
        if not self.should_refuse and not self.source_doc:
            raise ValueError(f"{self.id}: answerable item must have a source_doc")
        if self.should_refuse and self.source_doc:
            raise ValueError(f"{self.id}: should_refuse item must not have a source_doc")
        return self


def load_golden_set(path: Path = GOLDEN_SET_PATH) -> list[GoldenItem]:
    """Parse every non-blank line of the golden set into validated items."""
    items: list[GoldenItem] = []
    with path.open(encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                items.append(GoldenItem.model_validate_json(line))
            except Exception as exc:  # noqa: BLE001 - re-raised with line context
                raise ValueError(f"golden_set.jsonl line {lineno}: {exc}") from exc
    return items
