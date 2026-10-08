"""Reuse identical provider prompts and list changed prompts for paced evaluation.

No provider or database calls. Current deterministic replies and link guards are
replayed; all changed prompts and earlier service errors require a fresh attempt.
"""

from __future__ import annotations

import argparse
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


def records(path: Path) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for line in path.read_text(encoding="utf-8").splitlines()
            if (row := json.loads(line))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retrieval", type=Path, required=True)
    parser.add_argument("--prior", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frozen = records(args.retrieval)
    candidates: dict[str, list[dict[str, Any]]] = {}
    for path in args.prior:
        for case_id, old in records(path).items():
            candidates.setdefault(case_id, []).append({**old, "reuse_source": str(path)})
    if set(frozen) != set(candidates):
        raise ValueError("The frozen candidate and prior run must contain identical case IDs")
    reused = 0
    local = 0
    pending: list[str] = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        for case_id, row in frozen.items():
            if row["model"] != settings.llm_model:
                raise ValueError("Frozen retrieval model differs from the configured evaluation model")
            chunks = [RetrievedChunk(**chunk) for chunk in row["chunks"]]
            history = [ConversationMessage(**message) for message in row.get("history", [])]
            result: dict[str, Any] | None = None
            verification = ""
            reuse_source = None
            if row["prompt"] is None:
                class NeverProvider:
                    def generate(self, prompt: str) -> GenerationResult:
                        raise AssertionError("A local reply unexpectedly requested generation")

                with patch.object(pipeline, "retrieve_context", return_value=chunks):
                    result = asdict(pipeline.generate_answer(
                        row["question"], k=row["k"], department=row.get("department"),
                        history=history, provider=NeverProvider(),
                    ))
                verification = "current deterministic local reply"
                local += 1
            else:
                selected: dict[str, Any] | None = next((
                    item for item in reversed(candidates[case_id])
                    if item.get("answer") is not None and "provider_error" not in item
                    and not item.get("diagnostic_only") and not item.get("generation_config")
                    and item.get("generation_profile") == row.get("generation_profile")
                    and item.get("prompt") == row["prompt"]
                    and item["model"] == row["model"]), None)
                if selected is not None:
                    result = dict(selected["answer"])
                    result["retrieved"] = [
                        f"{chunk.source_doc} > {chunk.section} ({chunk.score:.2f})"
                        for chunk in chunks
                    ]
                    supplied = pipeline._answer_context(row["question"], chunks, history)
                    if pipeline.is_empty_knowledge_acknowledgement(result["text"]):
                        fallback = pipeline.escalation(row.get("department"))
                        result.update(text=fallback.text, citations=fallback.citations, refused=True)
                    else:
                        result["text"] = pipeline.grounded_answer_links(result["text"], supplied)
                    verification = "exact provider prompt reused; current deterministic answer contract reapplied"
                    reuse_source = selected["reuse_source"]
                    reused += 1
            if result is None:
                pending.append(case_id)
                continue
            stream.write(json.dumps({
                **row, "live": True, "answer": result, "verification": verification,
                "generation_reuse_from": reuse_source,
            }, ensure_ascii=False) + "\n")
    print(json.dumps({"cases": len(frozen), "reused_provider_answers": reused,
                      "local_replies": local, "pending_count": len(pending),
                      "pending_case_ids": pending, "live_ids": ",".join(pending)}, indent=2))


if __name__ == "__main__":
    main()
