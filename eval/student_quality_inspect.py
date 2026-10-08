"""Inspect corpus representation and write compact paired audit summaries."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from msfea_bot.ingestion.chunking import chunk_normalized_dir
from msfea_bot.ingestion.embeddings import get_model


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="eval/results/student_quality_corpus_20261007.json")
    args = parser.parse_args()
    chunks = chunk_normalized_dir()
    model = get_model()
    limit = model.max_seq_length
    if limit is None:
        raise ValueError("Embedding model has no declared input limit")
    token_counts = [len(model.tokenizer.encode(chunk.retrieval_text or chunk.text,
                                              truncation=False)) for chunk in chunks]
    oversized = [{"id": chunk.id, "section": chunk.section, "tokens": length}
                 for chunk, length in zip(chunks, token_counts, strict=True)
                 if length > limit]
    empty = [chunk.id for chunk in chunks
             if all(line.startswith(("#", "Topic:")) or not line.strip()
                    for line in chunk.text.splitlines())]
    report = {"chunks": len(chunks), "documents": dict(Counter(c.source_doc for c in chunks)),
              "qa_chunks": sum("**Question/topic:**" in c.text or "**Q:" in c.text for c in chunks),
              "heading_only": empty, "embedding_limit": limit,
              "truncated_embeddings": oversized}
    Path(args.output).write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
