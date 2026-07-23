"""CLI: `python -m eval.run` — load, validate, and summarize the golden set.

The retrieval metric needs a wired retriever (Phase 4 ingestion) and the answer
metric needs a generator (Phase 6). Until those exist, this reports the set's
shape so the harness is ready to measure the moment they do. The metric
functions themselves live in `eval.metrics` and are already unit-tested.
"""

from __future__ import annotations

from collections import Counter

from eval.curated_cases import curated_eval_items
from eval.loader import load_golden_set


def main() -> None:
    items = load_golden_set()
    total = len(items)
    refuse = sum(1 for i in items if i.should_refuse)
    answerable = total - refuse
    synthetic = sum(1 for i in items if i.is_synthetic)

    by_source: Counter[str] = Counter(i.source_doc for i in items if i.source_doc)
    by_tag: Counter[str] = Counter(t for i in items for t in i.tags)

    print(f"Golden set (file): {total} items ({answerable} answerable, {refuse} should-refuse)")
    print(f"  synthetic (predicted) questions: {synthetic} / {total}")

    curated = curated_eval_items()
    print(f"  + {len(curated)} live curated case(s) from the admin dashboard "
          "(derived at run time, not stored in the file)")
    print("  by source doc:")
    for doc, n in by_source.most_common():
        print(f"    {n:3}  {doc}")
    print("  by tag:")
    for tag, n in by_tag.most_common():
        print(f"    {n:3}  {tag}")
    print()
    print("Metric status:")
    print("  retrieval recall@k : PENDING retriever (Phase 4 ingestion)")
    print("  answer Layer 1     : READY (deterministic checks in eval.metrics)")
    print("  answer Layer 2     : PENDING LLM provider (Phase 6 generation)")


if __name__ == "__main__":
    main()
