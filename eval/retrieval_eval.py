"""Measure retrieval quality against the golden set (recall@k).

For each answerable golden question, retrieve the top-k chunks and check whether
a chunk from the expected ``source_doc`` is among them (document-level recall).
This is the retrieval metric from CLAUDE.md §4, kept independent of the LLM.

Prerequisites: the vector store is populated (`python -m msfea_bot.skeleton
ingest`) and Docker is up.

Run: `python -m eval.retrieval_eval`
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from eval.curated_cases import curated_eval_items
from eval.loader import GoldenItem, load_golden_set
from eval.metrics import evidence_present, recall_at_k
from msfea_bot.retrieval.store import search


@dataclass
class _Result:
    item: GoldenItem
    docs: list[str]  # source_doc of each retrieved chunk, in rank order
    texts: list[str]  # text of each retrieved chunk, in rank order


def _pct_bar(hits: int, total: int) -> str:
    return "#" * round(20 * hits / total) if total else ""


def evaluate_retrieval(ks: tuple[int, ...] = (1, 3, 5)) -> float:
    golden = [i for i in load_golden_set() if not i.should_refuse]
    curated = curated_eval_items()  # live cases from the curated table (all answerable)
    items = golden + curated
    top = max(ks)

    # Retrieve once at the largest k; recall at smaller k is a prefix of that.
    results: list[_Result] = []
    for item in items:
        chunks = search(item.question, top)
        results.append(
            _Result(item, [c.source_doc for c in chunks], [c.text for c in chunks])
        )

    n = len(items)
    print(
        f"Retrieval on {n} answerable questions "
        f"({len(golden)} golden + {len(curated)} live curated)\n"
    )

    print("Document-level recall (is a chunk from the expected source_doc in top-k?)")
    for k in ks:
        hits = sum(
            1 for r in results if r.item.source_doc and recall_at_k(r.docs, r.item.source_doc, k)
        )
        print(f"  recall@{k}: {hits:2}/{n} = {hits / n:5.0%}  {_pct_bar(hits, n)}")

    print("\nContext recall (is the answer's evidence text in top-k?) - the stricter metric")
    with_ev = [r for r in results if r.item.evidence]
    m = len(with_ev)
    for k in ks:
        hits = sum(1 for r in with_ev if evidence_present(r.texts[:k], r.item.evidence or ""))
        print(f"  context-recall@{k}: {hits:2}/{m} = {hits / m:5.0%}  {_pct_bar(hits, m)}")

    print(f"\nContext-recall misses at k={top} (evidence not retrieved - the real gaps):")
    misses = [
        r for r in with_ev if not evidence_present(r.texts[:top], r.item.evidence or "")
    ]
    if not misses:
        print("  none")
    for r in misses:
        print(f"  [{r.item.id}] evidence '{r.item.evidence}' not in top-{top}")

    top_hits = sum(1 for r in with_ev if evidence_present(r.texts[:top], r.item.evidence or ""))
    return top_hits / m if m else 1.0


def main() -> None:
    score = evaluate_retrieval()
    # CI gate (CLAUDE.md §4): fail the build if context-recall drops below a floor.
    # Off by default for local runs; CI sets EVAL_MIN_CONTEXT_RECALL (e.g. 0.90).
    floor = os.getenv("EVAL_MIN_CONTEXT_RECALL")
    if floor:
        limit = float(floor)
        if score < limit:
            print(f"\nFAIL: context-recall@top {score:.1%} is below the floor {limit:.1%}")
            raise SystemExit(1)
        print(f"\nOK: context-recall@top {score:.1%} meets the floor {limit:.1%}")


if __name__ == "__main__":
    main()
