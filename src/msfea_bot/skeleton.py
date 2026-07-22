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
from msfea_bot.retrieval.store import RetrievedChunk, index_chunks, search

PROMPT_TEMPLATE = """You are an assistant for the AUB MSFEA Career Development Center.
Answer the student's question using ONLY the context below. If the answer is not
in the context, say you don't have that information and suggest contacting the CDC.
Cite the section(s) you used.

Context:
{context}

Question: {question}

Answer:"""


def ingest() -> int:
    """Chunk the normalized KB and (re)build the vector store."""
    chunks = chunk_normalized_dir()
    count = index_chunks(chunks)
    print(f"Indexed {count} chunks into the vector store.")
    return count


def build_prompt(question: str, retrieved: list[RetrievedChunk]) -> str:
    context = "\n\n".join(f"[{c.source_doc} > {c.section}]\n{c.text}" for c in retrieved)
    return PROMPT_TEMPLATE.format(context=context, question=question)


def answer(question: str, k: int = 5) -> None:
    """Retrieve top-k chunks, print them, then print the LLM's grounded answer."""
    retrieved = search(question, k)
    print("Retrieved chunks (score  source > section):")
    for c in retrieved:
        print(f"  {c.score:.3f}  {c.source_doc} > {c.section}")
    print()

    # The LLM call is the last step and needs a provider/key; import lazily so
    # retrieval can be exercised even before the key is set.
    from msfea_bot.llm import get_llm_provider

    llm = get_llm_provider()
    print("Answer:\n" + llm.generate(build_prompt(question, retrieved)))


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
