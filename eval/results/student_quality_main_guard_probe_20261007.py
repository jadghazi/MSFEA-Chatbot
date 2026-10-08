"""Synthetic, no-provider reproduction of evidence removed before generation."""

from __future__ import annotations

import json
from unittest.mock import patch

from msfea_bot.generation import answer as pipeline
from msfea_bot.llm import GenerationResult
from msfea_bot.retrieval.store import RetrievedChunk


def main() -> None:
    primary = RetrievedChunk("primary", "Workshop resource information.", "fixture.md",
        "Resource", 0.98, {"source_kind": "admin_authored", "entry_id": "resource"})
    later = RetrievedChunk("later", "Graduates may ask for career assistance.", "fixture.md",
        "Later service", 0.65, {"source_kind": "admin_authored", "entry_id": "later",
                                "process_stage": "post_completion"})
    chunks = [primary, later]
    calls: list[str] = []

    class Recorder:
        def generate(self, prompt: str) -> GenerationResult:
            calls.append(prompt)
            return GenerationResult(text=pipeline.REFUSAL_MARKER)

    question = "Will I get hired after the workshop?"
    with patch.object(pipeline, "retrieve_context", return_value=chunks):
        answer = pipeline.generate_answer(question, provider=Recorder())
    print(json.dumps({"synthetic_no_sdk_calls": True, "generation_calls": len(calls),
        "retrieved_post_completion": True,
        "supplied_post_completion": any(chunk.metadata.get("process_stage") == "post_completion"
                                       for chunk in pipeline._answer_context(question, chunks, None)),
        "refused": answer.refused}))


if __name__ == "__main__":
    main()
