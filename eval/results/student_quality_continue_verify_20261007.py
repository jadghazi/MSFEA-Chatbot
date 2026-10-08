"""Verify frozen source identity and final trace parity without provider calls."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from unittest.mock import patch

from msfea_bot.config import settings
from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import ConversationMessage
from msfea_bot.llm import GenerationResult
from msfea_bot.retrieval.store import RetrievedChunk


def records(paths: list[Path]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["id"] in rows:
                raise ValueError(f"Duplicate trace ID: {row['id']}")
            rows[row["id"]] = row
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retrieval", type=Path, nargs="+", required=True)
    parser.add_argument("--answers", type=Path, nargs="+", required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--attempts", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frozen = records(args.retrieval)
    answers = records(args.answers)
    mismatches: list[str] = []
    hashes = json.loads(args.freeze.read_text(encoding="utf-8"))["runtime_and_sources_sha256"]
    for name, expected in hashes.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != expected:
            mismatches.append("source hash: " + name)
    for case_id, row in answers.items():
        original = frozen.get(case_id)
        if original is None:
            mismatches.append(case_id + ": unexpected ID")
            continue
        if (row.get("diagnostic_only") or row.get("generation_config")
                or row.get("provider_error") or row.get("answer") is None):
            mismatches.append(case_id + ": not an accepted default-configuration answer")
            continue
        for key in ("question", "department", "history", "k", "chunks", "prompt", "context", "model"):
            if row.get(key) != original.get(key):
                mismatches.append(case_id + ": frozen " + key)
        prompts: list[str] = []

        class Recorder:
            def generate(self, prompt: str) -> GenerationResult:
                prompts.append(prompt)
                return GenerationResult(text=pipeline.REFUSAL_MARKER)

        chunks = [RetrievedChunk(**chunk) for chunk in row["chunks"]]
        history = [ConversationMessage(**item) for item in row.get("history", [])]
        with patch.object(pipeline, "retrieve_context", return_value=chunks):
            result = pipeline.generate_answer(
                row["question"], k=row["k"], department=row.get("department"),
                history=history, provider=Recorder(),
            )
        if (prompts[0] if prompts else None) != row["prompt"]:
            mismatches.append(case_id + ": current prompt")
        if not prompts and asdict(result) != row["answer"]:
            mismatches.append(case_id + ": current local reply")
        if row["model"] != settings.llm_model:
            mismatches.append(case_id + ": configured model")
        supplied = pipeline._answer_context(row["question"], chunks, history)
        labels = {f"{chunk.source_doc} > {chunk.section}" for chunk in supplied}
        if prompts and not row["answer"]["refused"]:
            if any(label not in labels for label in row["answer"]["citations"]):
                mismatches.append(case_id + ": unsupported citation")
    if mismatches:
        raise ValueError(mismatches)
    missing = sorted(set(frozen) - set(answers))
    attempts = [json.loads(line) for path in args.attempts
                for line in path.read_text(encoding="utf-8").splitlines()]
    manifest = {
        "expected_cases": len(frozen), "verified_cases": len(answers),
        "complete": not missing, "missing_case_ids": missing,
        "current_prompt_and_local_reply_parity": True,
        "source_freeze_matches": True, "source_freeze": str(args.freeze),
        "answer_model": settings.llm_model,
        "production_model_acceptance": False,
        "default_generation_parameters": {"temperature": settings.llm_temperature,
            "seed": settings.llm_seed, "max_output_tokens": settings.llm_max_output_tokens,
            "thinking_level": "provider default"},
        "provider_answers": sum(row["prompt"] is not None for row in answers.values()),
        "local_replies": sum(row["prompt"] is None for row in answers.values()),
        "reused_provider_answers": sum(bool(row.get("generation_reuse_from"))
                                       for row in answers.values()),
        "retained_failed_attempts": sum("provider_error" in row for row in attempts),
        "attempt_files": [str(path) for path in args.attempts],
        "semantic_accuracy_verified_by_this_script": False,
        "artifact_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in [*args.retrieval, *args.answers, *args.attempts]},
    }
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2)
    print(json.dumps({key: value for key, value in manifest.items()
                      if key != "artifact_sha256"}, indent=2))


if __name__ == "__main__":
    main()
