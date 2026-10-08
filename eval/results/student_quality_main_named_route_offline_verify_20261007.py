"""Verify candidate identity and the interrupted actual-history prefix without SDK calls."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from msfea_bot.config import settings
from msfea_bot.curation.service import curated_chunks
from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import ConversationMessage, bounded_history
from msfea_bot.ingestion.chunking import chunk_normalized_dir
from msfea_bot.llm import GenerationResult
from msfea_bot.retrieval.store import _generation_hash, indexed_generation, retrieval_depth


def main() -> None:
    assert "test-db" in settings.database_url and settings.database_url.endswith("/msfea_test")
    root = Path("eval/results")
    freeze_path = root / "student_quality_main_named_route_freeze_20261007.json"
    hashes = json.loads(freeze_path.read_text(encoding="utf-8"))["runtime_and_sources_sha256"]
    for name, expected in hashes.items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
    generation = indexed_generation()
    assert _generation_hash(chunk_normalized_dir() + curated_chunks()) == generation
    trace_path = root / "student_quality_main_alternative_paths_dialogue_20261007.jsonl"
    rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    case = json.loads(Path("eval/student_quality_dialogue_set.jsonl").read_text().splitlines()[0])
    history: list[ConversationMessage] = []
    checks = []
    chain_verified = True
    for index, row in enumerate(rows, 1):
        assert row["id"] == f"{case['id']}.{index}"
        assert row["question"] == case["turns"][index - 1]["question"]
        assert row["expected_behavior"] == case["turns"][index - 1]["expected_behavior"]
        assert row["model"] == settings.llm_model
        assert row["history"] == [asdict(message) for message in bounded_history(history)]
        if row.get("provider_error"):
            break
        assert indexed_generation() == generation
        chunks = pipeline.retrieve_context(row["question"], row["k"], row["department"], history)
        assert row["k"] == retrieval_depth(row["question"], settings.top_k)
        prompts: list[str] = []

        class Recorder:
            def generate(self, prompt: str) -> GenerationResult:
                prompts.append(prompt)
                return GenerationResult(text=pipeline.REFUSAL_MARKER)

        with patch.object(pipeline, "retrieve_context", return_value=chunks):
            pipeline.generate_answer(
                row["question"], k=row["k"], department=row["department"],
                history=history, provider=Recorder(),
            )
        exact = (prompts[0] if prompts else None) == row["prompt"]
        chain_verified = chain_verified and exact
        checks.append({"id": row["id"], "current_prompt_exact": exact,
                       "current_chain_verified": chain_verified})
        history.extend([ConversationMessage("user", row["question"]),
                        ConversationMessage("assistant", row["answer"]["text"])])
    result = {
        "source_freeze": str(freeze_path), "source_hashes_verified": len(hashes),
        "canonical_index_matches": True, "index_generation": generation,
        "model": settings.llm_model, "fresh_provider_calls": 0, "prefix": checks,
        "complete_dialogue_evaluation": False,
        "note": "Exact current prompts and actual prior replies only; not independent repetitions or semantic grading.",
    }
    output = root / "student_quality_main_named_route_offline_verify_20261007.json"
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
