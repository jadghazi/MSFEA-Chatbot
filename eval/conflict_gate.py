"""Measure conflict-review candidate coverage independently of student retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eval.metrics import evidence_present
from msfea_bot.curation.validation import review_candidates


def load_cases() -> list[dict[str, Any]]:
    path = Path(__file__).with_name("conflict_review_set.jsonl")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def main() -> None:
    misses: list[str] = []
    flagged = 0
    false_positive_flags = 0
    cases = load_cases()
    for case in cases:
        related, flags = review_candidates(
            case["question"], case["answer"], case["department"]
        )
        surfaced = evidence_present(
            [item["text"] for item in related], case["expected_evidence"]
        )
        if case["must_surface"] and not surfaced:
            misses.append(case["id"])
        if flags:
            flagged += 1
            if not case["should_flag"]:
                false_positive_flags += 1
        print(
            f"{'PASS' if surfaced else 'MISS'} {case['id']}: "
            f"candidates={len(related)} flags={len(flags)}"
        )
    print(
        "Conflict candidate coverage: "
        f"{len(cases) - len(misses)}/{len(cases)}; flagged={flagged}; "
        f"known false-positive fixtures={false_positive_flags}"
    )
    if misses:
        raise SystemExit("Missing designated conflict evidence: " + ", ".join(misses))


if __name__ == "__main__":
    main()
