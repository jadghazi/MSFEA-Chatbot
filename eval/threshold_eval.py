"""Calibrate the pre-LLM similarity gate without spending provider quota.

The gate uses the maximum cosine score among supplied hybrid/RRF results, exactly as
``generate_answer`` does. All answerable golden questions plus terse/misspelled
valid queries must pass. The separate off-topic stress set measures how many clearly
unrelated requests avoid an LLM call; topical-but-unanswerable questions remain the
prompt refusal layer's responsibility.

Run after changing the KB, embedding model, or retrieval logic:
    python -m eval.threshold_eval
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from eval.loader import load_golden_set
from msfea_bot.config import settings
from msfea_bot.generation.conversation import build_retrieval_query
from msfea_bot.retrieval.store import retrieval_depth, search

THRESHOLD_SET_PATH = Path(__file__).parent / "threshold_set.jsonl"
MIN_OFFTOPIC_BLOCK_RATE = 0.50


class ThresholdCase(BaseModel):
    """One supplemental calibration query."""

    id: str
    question: str
    should_pass_threshold: bool
    department: str | None = None


@dataclass(frozen=True)
class ScoredCase:
    id: str
    score: float
    should_pass_threshold: bool


def load_threshold_set(path: Path = THRESHOLD_SET_PATH) -> list[ThresholdCase]:
    """Load the retrieval-only stress cases."""
    cases: list[ThresholdCase] = []
    with path.open(encoding="utf-8") as source:
        for line_number, raw in enumerate(source, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                cases.append(ThresholdCase.model_validate_json(line))
            except Exception as exc:  # noqa: BLE001 - report the malformed data line
                raise ValueError(f"threshold_set.jsonl line {line_number}: {exc}") from exc
    return cases


def _best_score(query: str, question: str, department: str | None) -> float:
    chunks = search(query, retrieval_depth(question, settings.top_k), department=department)
    return max((chunk.score for chunk in chunks), default=-1.0)


def evaluate_threshold() -> tuple[int, int, int]:
    """Print calibration metrics; return false refusals, blocked off-topic, total off-topic."""
    scored: list[ScoredCase] = []

    synthesis = load_golden_set(Path(__file__).parent / "synthesis_set.jsonl")
    for golden_item in load_golden_set() + synthesis:
        if golden_item.should_refuse:
            continue
        query = build_retrieval_query(golden_item.question, golden_item.history)
        scored.append(
            ScoredCase(
                golden_item.id,
                _best_score(query, golden_item.question, golden_item.department),
                True,
            )
        )

    for supplemental_item in load_threshold_set():
        scored.append(
            ScoredCase(
                supplemental_item.id,
                _best_score(supplemental_item.question, supplemental_item.question,
                            supplemental_item.department),
                supplemental_item.should_pass_threshold,
            )
        )

    threshold = settings.similarity_threshold
    valid = [item for item in scored if item.should_pass_threshold]
    off_topic = [item for item in scored if not item.should_pass_threshold]
    false_refusals = [item for item in valid if item.score < threshold]
    blocked = [item for item in off_topic if item.score < threshold]

    print(f"Similarity threshold: {threshold:.2f}")
    print(
        f"Valid queries passing: {len(valid) - len(false_refusals)}/{len(valid)} "
        f"(lowest score {min(item.score for item in valid):.4f})"
    )
    print(
        f"Off-topic queries blocked before the LLM: {len(blocked)}/{len(off_topic)} "
        f"({len(blocked) / len(off_topic):.0%})"
    )
    if false_refusals:
        print("False refusals:")
        for scored_item in sorted(false_refusals, key=lambda value: value.score):
            print(f"  [{scored_item.id}] score={scored_item.score:.4f}")

    return len(false_refusals), len(blocked), len(off_topic)


def main() -> None:
    false_refusals, blocked, off_topic = evaluate_threshold()
    if false_refusals:
        raise SystemExit("FAIL: the threshold rejects valid calibration questions")
    if blocked / off_topic < MIN_OFFTOPIC_BLOCK_RATE:
        raise SystemExit(
            "FAIL: the threshold blocks fewer than half of the off-topic stress cases"
        )
    print("PASS: no valid calibration query is rejected and off-topic savings remain useful")


if __name__ == "__main__":
    main()
