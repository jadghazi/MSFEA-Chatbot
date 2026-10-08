"""Source-grounded student-intent audit, isolated retrieval and optional live answers."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any
from unittest.mock import patch

from eval.metrics import evidence_present
from eval.index_guard import canonical_generation
from eval.paid_budget import add_budget_arguments, evaluation_provider, student_profile
from msfea_bot.config import settings
from msfea_bot.generation import answer as pipeline
from msfea_bot.generation import conversation as routing
from msfea_bot.generation.conversation import ConversationMessage
from msfea_bot.ingestion.chunking import chunk_normalized_dir
from msfea_bot.llm import GenerationResult, LLMError
from msfea_bot.retrieval.store import RetrievedChunk, indexed_generation, retrieval_depth


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="eval/student_quality_audit_set.jsonl")
    parser.add_argument("--output", required=True)
    parser.add_argument("--k", type=int)
    parser.add_argument("--live-ids", default="")
    parser.add_argument("--template")
    parser.add_argument("--ids", default="")
    parser.add_argument("--baseline-code", help="Frozen answer/conversation modules for exact baseline replay")
    parser.add_argument("--replay-retrieval", help="Reuse an immutable earlier retrieval trace")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--delay", type=float, default=0)
    parser.add_argument("--max-consecutive-service-errors", type=int, default=3)
    add_budget_arguments(parser)
    args = parser.parse_args()
    if args.delay < 0:
        parser.error("--delay must be non-negative")
    if args.max_consecutive_service_errors < 1:
        parser.error("--max-consecutive-service-errors must be positive")
    # Index-building and audit traces must never point at a serving database.
    if "test-db" not in settings.database_url or not settings.database_url.endswith("/msfea_test"):
        raise ValueError("Use the isolated development Compose test-db / msfea_test")
    if args.baseline_code:
        import msfea_bot.generation.conversation as conversation
        import msfea_bot.retrieval.store as store

        for module in (store, conversation, pipeline):
            source = Path(args.baseline_code) / (module.__name__.rsplit(".", 1)[1] + ".py")
            if source.exists():
                exec(compile(source.read_text(encoding="utf-8"), str(source), "exec"), vars(module))
    if args.template:
        pipeline._PROMPT = Path(args.template).read_text(encoding="utf-8")
    cases = [json.loads(line) for line in Path(args.cases).read_text(encoding="utf-8").splitlines()]
    if args.ids:
        cases = [case for case in cases if case["id"] in set(args.ids.split(","))]
    corpus = [chunk.text for chunk in chunk_normalized_dir()]
    for case in cases:
        for evidence in case.get("evidence_all", []):
            if not evidence_present(corpus, evidence):
                raise ValueError(f"Unverified evidence {case['id']}: {evidence}")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    done: set[str] = set()
    if args.resume and output.exists():
        done = {row["id"] for line in output.read_text(encoding="utf-8").splitlines()
                if "provider_error" not in (row := json.loads(line))}
    selected = set(args.live_ids.split(","))
    replay = {row["id"]: row for row in (
        json.loads(line) for line in Path(args.replay_retrieval).read_text(encoding="utf-8").splitlines()
    )} if args.replay_retrieval else {}
    provider = evaluation_provider(args) if args.live_ids else None
    generation = indexed_generation() if replay else canonical_generation()
    consecutive_service_errors = 0
    with output.open("a" if args.resume else "x", encoding="utf-8") as stream:
        for case in cases:
            if case["id"] in done:
                continue
            if not replay and indexed_generation() != generation:
                raise RuntimeError("Audit index changed during the run; retain and exclude this attempt")
            history = [ConversationMessage(**item) for item in case.get("history", [])]
            question = case["question"]
            k = args.k or retrieval_depth(question, settings.top_k)
            plan = routing.retrieval_plan(question, history)
            retrieval_started = time.perf_counter()
            chunks = ([RetrievedChunk(**chunk) for chunk in replay[case["id"]]["chunks"]]
                      if replay else pipeline.retrieve_context(question, k, case.get("department"), history))
            retrieval_ms = round((time.perf_counter() - retrieval_started) * 1000, 1)
            prompts: list[str] = []
            live = case["id"] in selected or "all" in selected

            class Recorder:
                def generate(self, prompt: str) -> GenerationResult:
                    prompts.append(prompt)
                    if live and provider is not None:
                        return provider.generate(prompt)
                    return GenerationResult(text=pipeline.REFUSAL_MARKER)

            record: dict[str, Any] = {
                **case, "query": plan.query, "literal_query": plan.standalone_query,
                "k": k, "chunks": [asdict(chunk) for chunk in chunks],
                "model": settings.llm_model, "live": live,
                "generation_profile": student_profile(),
                "index_generation": generation if not replay else "frozen retrieval replay",
                "gate_pass": pipeline.passes_similarity_gate(chunks, settings.similarity_threshold),
                "retrieval_queries": list(dict.fromkeys(
                    [plan.query, *([plan.standalone_query] if plan.standalone_query else [])]
                    + [chunk.metadata["query_correction"] for chunk in chunks
                       if "query_correction" in chunk.metadata])),
                "companion_count": sum(chunk.metadata.get("retrieval_role") == "companion"
                                       for chunk in chunks),
                "retrieval_ms": retrieval_ms if not replay else None,
            }
            try:
                with patch.object(pipeline, "retrieve_context", return_value=chunks):
                    result = pipeline.generate_answer(
                        question, k=k, department=case.get("department"), history=history,
                        provider=Recorder(),
                    )
                # A dry-run refusal is a recorder placeholder, never an answer judgment.
                record["answer"] = asdict(result) if live else None
            except LLMError as exc:
                record["provider_error"] = type(exc).__name__
            record["prompt"] = prompts[0] if prompts else None
            context = prompts[0].split("\nContext:\n", 1)[1].split("\n\nQuestion:", 1)[0] if prompts else ""
            record["context"] = context
            record["evidence_hits"] = [evidence_present([chunk.text for chunk in chunks], item)
                                       for item in case.get("evidence_all", [])]
            record["context_hits"] = [evidence_present([context], item)
                                      for item in case.get("evidence_all", [])]
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            print(json.dumps({"id": case["id"], "hits": record["evidence_hits"],
                              "gate": record["gate_pass"], "query": plan.query,
                              "refused": record["answer"]["refused"] if record.get("answer") else None,
                              "error": record.get("provider_error")}), flush=True)
            if live and prompts:
                consecutive_service_errors = (
                    consecutive_service_errors + 1
                    if record.get("provider_error") == "LLMServiceError" else 0
                )
                time.sleep(args.delay)
            if record.get("provider_error") == "LLMRateLimitError":
                break
            if consecutive_service_errors >= args.max_consecutive_service_errors:
                print("Stopping after repeated provider service errors; retain this attempt.", flush=True)
                break


if __name__ == "__main__":
    main()
