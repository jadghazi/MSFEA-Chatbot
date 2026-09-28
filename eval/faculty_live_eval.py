"""Run the frozen faculty questions through the deployed retrieval/generation path.

Run inside the app container against its existing index. This calls generate_answer
directly, so evaluation traffic does not enter student interaction logs. Output is
append-only JSONL and can be resumed after transient Gemini failures.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import cast
from unittest.mock import patch

from msfea_bot.config import settings
from msfea_bot.generation import answer as pipeline
from msfea_bot.llm import LLMRateLimitError, LLMServiceError
from msfea_bot.retrieval.store import RetrievedChunk, retrieval_depth, search


def _source_hit(chunks: list[RetrievedChunk], expected: list[str]) -> bool:
    return any(chunk.source_doc in expected for chunk in chunks)


def _case_result(case: dict[str, object], retrieval_only: bool) -> dict[str, object]:
    question = str(case["question"])
    department = str(case["department"])
    expected = cast(list[str], case["source_doc_candidates"])
    captured: list[RetrievedChunk] = []
    if retrieval_only:
        depth = retrieval_depth(question, settings.top_k)
        captured = search(question, depth, department=department)
        answer: dict[str, object] | None = None
    else:
        real_search = search

        def capture(query: str, k: int, department: str | None = None) -> list[RetrievedChunk]:
            chunks = real_search(query, k, department=department)
            captured.extend(chunks)
            return chunks

        with patch.object(pipeline, "search", capture):
            answer = asdict(pipeline.generate_answer(question, department=department))
    return {
        "id": case["id"],
        "question": question,
        "department": department,
        "source_doc_candidates": expected,
        "retrieved": [
            {"id": c.id, "source_doc": c.source_doc, "section": c.section,
             "score": round(c.score, 4), "text": c.text}
            for c in captured
        ],
        "source_document_hit": _source_hit(captured, expected),
        "answer": answer,
        "error": None,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "model": settings.llm_model,
        "retrieval_only": retrieval_only,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--delay", type=float, default=8.0,
                        help="Minimum seconds between Gemini calls (8s = at most 7.5 RPM)")
    parser.add_argument("--max-cases", type=int)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--completed-from", type=Path)
    args = parser.parse_args()
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        parser.error("shard-index must be between zero and shard-count minus one")
    cases = [json.loads(line) for line in args.cases.read_text(encoding="utf-8").splitlines()]
    if args.max_cases:
        cases = cases[:args.max_cases]
    cases = [case for index, case in enumerate(cases)
             if index % args.shard_count == args.shard_index]
    completed: set[str] = set()
    for path in (args.output, args.completed_from):
        if path and path.exists():
            completed.update(
                record["id"] for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() and (record := json.loads(line)).get("error") is None
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("a", encoding="utf-8") as stream:
        for number, case in enumerate(cases, 1):
            if case["id"] in completed:
                continue
            started = time.monotonic()
            for attempt in range(4):
                try:
                    result = _case_result(case, args.retrieval_only)
                    break
                except (LLMRateLimitError, LLMServiceError) as exc:
                    if attempt == 3:
                        result = {"id": case["id"], "error": type(exc).__name__,
                                  "retrieval_only": args.retrieval_only,
                                  "evaluated_at": datetime.now(timezone.utc).isoformat()}
                    else:
                        time.sleep(8.0 * (attempt + 1))
            stream.write(json.dumps(result, ensure_ascii=False) + "\n")
            stream.flush()
            print(f"{number}/{len(cases)} {case['id']} "
                  f"source_hit={result.get('source_document_hit')} "
                  f"error={result.get('error')}", flush=True)
            if not args.retrieval_only:
                time.sleep(max(0.0, args.delay - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
