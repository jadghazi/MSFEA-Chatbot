"""Walking skeleton (CLAUDE.md §5.3).

The thinnest end-to-end path: chunk -> embed -> store -> retrieve -> LLM ->
printed grounded answer. Deliberately crude; citations, the refusal threshold,
and the real guardrail prompt are Phase 6.

Usage:
    python -m msfea_bot.skeleton ingest        # (re)build the vector store
    python -m msfea_bot.skeleton "<question>"  # retrieve + answer
"""

from __future__ import annotations

import sys

from msfea_bot.ingestion.chunking import chunk_normalized_dir
from msfea_bot.retrieval.store import index_chunks


def ingest() -> int:
    """Chunk the normalized KB and (re)build the vector store."""
    chunks = chunk_normalized_dir()
    count = index_chunks(chunks)
    print(f"Indexed {count} chunks into the vector store.")
    return count


def answer(question: str) -> None:
    """Run guarded generation and print the answer (or graceful refusal)."""
    from msfea_bot.generation import generate_answer

    result = generate_answer(question)
    if result.refused:
        print("Refused / escalated:")
        print("  " + result.text)
    else:
        print("Answer:")
        print("  " + result.text)
        print("\nSources:")
        for citation in result.citations:
            print("  - " + citation)
    print(f"\n[{result.disclaimer}]")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print('Usage: python -m msfea_bot.skeleton ingest | "<question>"')
        return
    if args[0] == "ingest":
        ingest()
        return
    answer(" ".join(args))


if __name__ == "__main__":
    main()
