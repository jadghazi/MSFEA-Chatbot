"""Verify actual-answer history lineage without claiming semantic correctness."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from unittest.mock import patch

from eval.index_guard import canonical_generation
from eval.paid_budget import student_profile
from msfea_bot.config import settings
from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import ConversationMessage, bounded_history, retrieval_plan
from msfea_bot.llm import GenerationResult
from msfea_bot.retrieval.store import RetrievedChunk


def verify(dataset: Path, trace: Path) -> dict[str, Any]:
    cases = [json.loads(line) for line in dataset.read_text(encoding="utf-8").splitlines()]
    rows = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
    records = {row["id"]: row for row in rows}
    expected = {f"{case['id']}.{i}" for case in cases
                for i in range(1, len(case["turns"]) + 1)}
    if len(records) != len(rows) or set(records) != expected:
        raise ValueError("Incomplete or duplicate actual-history trace")
    generation = canonical_generation()
    dataset_hash = hashlib.sha256(dataset.read_bytes()).hexdigest()
    for case in cases:
        history: list[ConversationMessage] = []
        for index, turn in enumerate(case["turns"], 1):
            row = records[f"{case['id']}.{index}"]
            prior = bounded_history(history)
            if (row["question"] != turn["question"]
                    or row["expected_behavior"] != turn["expected_behavior"]
                    or row["department"] != case.get("department")
                    or row["history"] != [asdict(message) for message in prior]
                    or row["dataset_sha256"] != dataset_hash
                    or row["index_generation"] != generation
                    or row["model"] != settings.llm_model
                    or row["generation_profile"] != student_profile()
                    or row.get("provider_error") or not row.get("answer")):
                raise ValueError(f"{row['id']}: source, profile or history lineage mismatch")
            plan = retrieval_plan(row["question"], prior)
            if row["query"] != plan.query or row["literal_query"] != plan.standalone_query:
                raise ValueError(f"{row['id']}: current query mismatch")
            chunks = [RetrievedChunk(**chunk) for chunk in row["chunks"]]
            prompts: list[str] = []

            class Recorder:
                def generate(self, prompt: str) -> GenerationResult:
                    prompts.append(prompt)
                    return GenerationResult(text=pipeline.REFUSAL_MARKER)

            with patch.object(pipeline, "retrieve_context", return_value=chunks):
                result = pipeline.generate_answer(
                    row["question"], k=row["k"], department=case.get("department"),
                    history=prior, provider=Recorder(),
                )
            if (prompts[0] if prompts else None) != row["prompt"]:
                raise ValueError(f"{row['id']}: current prompt mismatch")
            if not prompts and asdict(result) != row["answer"]:
                raise ValueError(f"{row['id']}: current deterministic reply mismatch")
            supplied = pipeline._answer_context(row["question"], chunks, prior)
            labels = {f"{chunk.source_doc} > {chunk.section}" for chunk in supplied}
            if prompts and any(label not in labels for label in row["answer"]["citations"]):
                raise ValueError(f"{row['id']}: unsupported citation label")
            history.extend((ConversationMessage("user", row["question"]),
                            ConversationMessage("assistant", row["answer"]["text"])))
    return {"dataset": str(dataset), "trace": str(trace), "verified_turns": len(rows),
            "actual_answer_history_lineage": True, "current_prompt_profile_parity": True,
            "canonical_index_generation": generation, "semantic_accuracy_verified": False,
            "sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in (dataset, trace)}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datasets", type=Path, nargs="+", required=True)
    parser.add_argument("--traces", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if (len(args.datasets) != len(args.traces) or "test-db" not in settings.database_url
            or not settings.database_url.endswith("/msfea_test")):
        raise ValueError("Use paired datasets/traces and the isolated development database")
    receipt = [verify(dataset, trace) for dataset, trace in zip(args.datasets, args.traces)]
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
