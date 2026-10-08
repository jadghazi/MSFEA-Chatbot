"""Paced student-model evaluation using actual generated conversation history.

The frozen turn expectations are source-review criteria, not an automatic judge.
Only disposable development databases are accepted. No ingestion or writes occur.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any
from unittest.mock import patch

from eval.paid_budget import add_budget_arguments, evaluation_provider, student_profile
from eval.index_guard import canonical_generation

from msfea_bot.config import settings
from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import ConversationMessage, bounded_history, retrieval_plan
from msfea_bot.llm import GenerationResult, LLMError
from msfea_bot.retrieval.store import indexed_generation, retrieval_depth


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("eval/student_quality_dialogue_set.jsonl"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--delay", type=float, default=0)
    parser.add_argument("--live", action="store_true", required=True)
    add_budget_arguments(parser)
    args = parser.parse_args()
    if "test-db" not in settings.database_url or not settings.database_url.endswith("/msfea_test"):
        raise ValueError("Dialogue evaluation requires the isolated development database")
    if args.delay < 0:
        parser.error("--delay must be non-negative")
    cases = [json.loads(line) for line in args.cases.read_text(encoding="utf-8").splitlines()]
    case_hash = hashlib.sha256(args.cases.read_bytes()).hexdigest()
    generation = canonical_generation()
    provider = evaluation_provider(args)
    service_errors = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        for case in cases:
            history: list[ConversationMessage] = []
            for turn_index, turn in enumerate(case["turns"], 1):
                if indexed_generation() != generation:
                    raise RuntimeError("The evaluation index changed; retain this incomplete attempt")
                question = turn["question"]
                prior = bounded_history(history)
                k = retrieval_depth(question, settings.top_k)
                plan = retrieval_plan(question, prior)
                chunks = pipeline.retrieve_context(question, k, case.get("department"), prior)
                prompts: list[str] = []

                class Recorder:
                    def generate(self, prompt: str) -> GenerationResult:
                        prompts.append(prompt)
                        return provider.generate(prompt)

                record: dict[str, Any] = {
                    "id": f"{case['id']}.{turn_index}", **turn,
                    "department": case.get("department"), "model": settings.llm_model,
                    "generation_profile": student_profile(),
                    "history": [asdict(message) for message in prior],
                    "k": k, "query": plan.query, "literal_query": plan.standalone_query,
                    "chunks": [asdict(chunk) for chunk in chunks],
                    "index_generation": generation, "dataset_sha256": case_hash,
                }
                try:
                    with patch.object(pipeline, "retrieve_context", return_value=chunks):
                        result = pipeline.generate_answer(
                            question, k=k, department=case.get("department"),
                            history=prior, provider=Recorder(),
                        )
                    record["answer"] = asdict(result)
                    history.extend((ConversationMessage("user", question),
                                    ConversationMessage("assistant", result.text)))
                    service_errors = 0
                except LLMError as exc:
                    record["provider_error"] = type(exc).__name__
                    service_errors = service_errors + 1 if type(exc).__name__ == "LLMServiceError" else 0
                record["prompt"] = prompts[0] if prompts else None
                record["context"] = (prompts[0].split("\nContext:\n", 1)[1]
                                     .split("\n\nQuestion:", 1)[0]) if prompts else ""
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                stream.flush()
                print(json.dumps({"id": record["id"], "query": plan.query,
                                  "error": record.get("provider_error")}), flush=True)
                if prompts:
                    time.sleep(args.delay)
                if record.get("provider_error") == "LLMRateLimitError" or service_errors >= 3:
                    return
                if record.get("provider_error"):
                    # Never fabricate a preceding assistant answer for later turns.
                    break


if __name__ == "__main__":
    main()
