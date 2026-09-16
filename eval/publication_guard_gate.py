"""Gate the frozen publication-guard sample and report applicability by department."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from eval.metrics import evidence_present
from msfea_bot.config import settings
from msfea_bot.generation.answer import passes_similarity_gate
from msfea_bot.generation.conversation import ConversationMessage, build_retrieval_query
from msfea_bot.retrieval.store import retrieval_depth, search


def main() -> None:
    path = Path(__file__).with_name("publication_guard_baseline_set.jsonl")
    cases = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    groups: dict[str, list[bool]] = defaultdict(list)
    failures: list[str] = []
    for case in cases:
        if case["should_refuse"]:
            continue
        history = [ConversationMessage(**message) for message in case.get("history", [])]
        query = build_retrieval_query(case["question"], history)
        chunks = search(
            query,
            retrieval_depth(case["question"], settings.top_k),
            department=case.get("department"),
        )
        passed = all(
            evidence_present([chunk.text for chunk in chunks], evidence)
            for evidence in case["evidence_all"]
        ) and passes_similarity_gate(chunks, settings.similarity_threshold)
        label = case.get("department") or "unknown"
        groups[label].append(passed)
        if not passed:
            failures.append(case["id"])
        print(f"{'PASS' if passed else 'FAIL'} {case['id']} department={label}")
    for label in sorted(groups):
        values = groups[label]
        print(f"Department {label}: {sum(values)}/{len(values)}")
    if failures:
        raise SystemExit("Publication-guard retrieval failures: " + ", ".join(failures))


if __name__ == "__main__":
    main()
