"""Gate source-document retrieval on the frozen faculty-question set."""

from __future__ import annotations

import json
import os
from pathlib import Path

from msfea_bot.config import settings
from msfea_bot.retrieval.store import retrieval_depth, search


CASES = Path(__file__).parent / "faculty_questions_golden.jsonl"


def main() -> None:
    cases = [json.loads(line) for line in CASES.read_text(encoding="utf-8").splitlines()]
    answerable = [case for case in cases if not case["should_refuse"]]
    misses: list[str] = []
    for case in answerable:
        chunks = search(
            case["question"], retrieval_depth(case["question"], settings.top_k),
            department=case["department"],
        )
        if not any(chunk.source_doc in case["source_doc_candidates"] for chunk in chunks):
            misses.append(case["id"])
    score = (len(answerable) - len(misses)) / len(answerable)
    print(f"Faculty answerable source-document recall@7: "
          f"{len(answerable) - len(misses)}/{len(answerable)} "
          f"({score:.1%})")
    print("Misses: " + (", ".join(misses) or "none"))
    floor = float(os.getenv("FACULTY_MIN_SOURCE_RECALL", "0.95"))
    if score < floor:
        raise SystemExit(f"Faculty source-document recall below {floor:.0%} floor")


if __name__ == "__main__":
    main()
