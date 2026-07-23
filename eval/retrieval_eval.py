"""Measure retrieval quality against the golden set (recall@k).

For each answerable golden question, retrieve the top-k chunks and check whether
a chunk from the expected ``source_doc`` is among them (document-level recall).
This is the retrieval metric from CLAUDE.md §4, kept independent of the LLM.

Prerequisites: the vector store is populated (`python -m msfea_bot.skeleton
ingest`) and Docker is up.

Run: `python -m eval.retrieval_eval`
"""

from __future__ import annotations

from eval.loader import GoldenItem, load_golden_set
from eval.metrics import recall_at_k
from msfea_bot.retrieval.store import search


def evaluate_retrieval(ks: tuple[int, ...] = (1, 3, 5)) -> None:
    items = [i for i in load_golden_set() if not i.should_refuse]
    top = max(ks)

    # Retrieve once at the largest k; recall at smaller k is a prefix of that.
    results: list[tuple[GoldenItem, list[str]]] = []
    for item in items:
        retrieved_docs = [c.source_doc for c in search(item.question, top)]
        results.append((item, retrieved_docs))

    print(f"Retrieval recall on {len(items)} answerable golden questions")
    print("(document-level: is a chunk from the expected source_doc in top-k?)\n")
    for k in ks:
        hits = sum(
            1
            for item, docs in results
            if item.source_doc and recall_at_k(docs, item.source_doc, k)
        )
        bar = "#" * round(20 * hits / len(items))
        print(f"  recall@{k}: {hits:2}/{len(items)} = {hits / len(items):5.0%}  {bar}")

    print(f"\nMisses at k={top} (expected doc not retrieved):")
    misses = [
        (item, docs)
        for item, docs in results
        if item.source_doc and not recall_at_k(docs, item.source_doc, top)
    ]
    if not misses:
        print("  none")
    for item, docs in misses:
        print(f"  [{item.id}] expected {item.source_doc}")
        print(f"     got: {docs}")


def main() -> None:
    evaluate_retrieval()


if __name__ == "__main__":
    main()
