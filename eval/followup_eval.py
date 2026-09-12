"""Record current production retrieval/prompts/answers against frozen follow-up cases."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch

from eval.metrics import evidence_present
from msfea_bot.config import settings
from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import ConversationMessage
from msfea_bot.llm import GenerationResult, get_llm_provider
from msfea_bot.retrieval.store import RetrievedChunk, search


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="eval/followup_set.jsonl")
    parser.add_argument("--output", required=True)
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--model")
    parser.add_argument("--thinking-level")
    parser.add_argument("--template")
    parser.add_argument("--delay", type=float, default=0)
    parser.add_argument("--ids", help="Comma-separated case IDs for a focused probe")
    args = parser.parse_args()
    if args.template:
        pipeline._PROMPT = Path(args.template).read_text(encoding="utf-8")
    if args.model:
        settings.llm_model = args.model
    if args.thinking_level:
        from google.genai import types
        from msfea_bot.llm.gemini import GeminiProvider
        provider = get_llm_provider()
        if not isinstance(provider, GeminiProvider):
            raise ValueError("Thinking comparison requires Gemini")
        provider._config.thinking_config = types.ThinkingConfig(thinking_level=args.thinking_level)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in Path(args.cases).read_text(encoding="utf-8").splitlines()]
    if args.ids:
        selected = set(args.ids.split(","))
        rows = [row for row in rows if row["id"] in selected]
    with out.open("x", encoding="utf-8") as stream:
        for row in rows:
            chunks: list[RetrievedChunk] = []
            prompts: list[str] = []

            def capture(query: str, k: int, department: str | None = None) -> list[RetrievedChunk]:
                chunks.extend(search(query, k, department=department))
                return chunks

            class Recorder:
                def generate(self, prompt: str) -> GenerationResult:
                    prompts.append(prompt)
                    if args.retrieval_only:
                        return GenerationResult(text="INSUFFICIENT_CONTEXT")
                    return get_llm_provider().generate(prompt)

            with patch.object(pipeline, "search", capture):
                result = pipeline.generate_answer(
                    row["question"], department=row.get("department"), provider=Recorder(),
                    history=[ConversationMessage(**m) for m in row.get("history", [])],
                )
            evidence = row.get("evidence_all", [])
            record = {**row, "chunks": [asdict(c) for c in chunks], "prompts": prompts,
                      "model": settings.llm_model, "retrieval_only": args.retrieval_only,
                      "answer": asdict(result),
                      "evidence_hits": [evidence_present([c.text for c in chunks], e)
                                        for e in evidence]}
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            print(json.dumps({"id": row["id"], "hits": record["evidence_hits"],
                              "answer": result.text}), flush=True)
            time.sleep(args.delay)


if __name__ == "__main__":
    main()
