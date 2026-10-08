"""Mixed-turn retrieval audit with optional focused answer generation."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from msfea_bot.config import settings
from msfea_bot.generation.answer import (
    _answer_context, build_prompt, parse_answer, passes_similarity_gate,
    retrieve_context,
)
from msfea_bot.generation.conversation import ConversationMessage, retrieval_plan
from msfea_bot.llm import get_llm_provider
from msfea_bot.retrieval.store import RetrievedChunk, retrieval_depth


def _rank(chunks: list[RetrievedChunk], case: dict[str, Any], phrase: str | None) -> int | None:
    for rank, chunk in enumerate(chunks, 1):
        if phrase is not None:
            if phrase.casefold() in chunk.text.casefold() and (
                case.get("expected_source_doc") is None
                or case["expected_source_doc"] == chunk.source_doc
            ):
                return rank
        elif case.get("expected_section") and case["expected_section"] in chunk.section:
            return rank
    return None


def _cases() -> list[dict[str, Any]]:
    folder = Path(__file__).parent
    cases: list[dict[str, Any]] = []
    for name in ("conversation_set.jsonl", "conversation_stress_set.jsonl"):
        cases.extend(json.loads(line) for line in (folder / name).read_text(
            encoding="utf-8").splitlines() if line.strip())
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--answer-ids", help="Comma-separated focused cases; spends answer quota")
    parser.add_argument("--ids", help="Comma-separated cases for a focused retrieval run")
    parser.add_argument("--delay", type=float, default=5.0)
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()
    selected = set(args.answer_ids.split(",")) if args.answer_ids else set()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    records: list[dict[str, Any]] = []
    answer_provider = get_llm_provider() if selected else None
    selected_cases = set(args.ids.split(",")) if args.ids else None
    for case in _cases():
        if selected_cases is not None and case["id"] not in selected_cases:
            continue
        question = case["question"]
        history = [ConversationMessage(**item) for item in case["history"]]
        plan = retrieval_plan(question, history)
        k = retrieval_depth(question, settings.top_k)
        chunks = retrieve_context(question, k, case.get("department"), history)
        phrases = case.get("evidence_all") or [case.get("expected_evidence")]
        ranks = [_rank(chunks, case, phrase) for phrase in phrases]
        bare = retrieve_context(question, k, case.get("department"), None)
        record: dict[str, Any] = {
            "id": case["id"], "query": plan.query,
            "literal_query": plan.standalone_query,
            "independent": case.get("independent", case.get("route") == "standalone"),
            "ranks": ranks, "hit": all(rank is not None for rank in ranks),
            "top3": all(rank is not None and rank <= 3 for rank in ranks),
            "bare_parity": [c.id for c in chunks] == [c.id for c in bare],
            "sections": [c.section for c in chunks],
        }
        if case["id"] in selected and answer_provider is not None:
            if passes_similarity_gate(chunks, settings.similarity_threshold):
                prompt_chunks = _answer_context(question, chunks, history)
                generation = answer_provider.generate(build_prompt(
                    question, prompt_chunks, case.get("department"), history,
                ))
                answer = parse_answer(generation.text, prompt_chunks, case.get("department"))
                record["answer"] = answer.text
                record["refused"] = answer.refused
                record["citations"] = answer.citations
            else:
                record["answer"] = None
                record["refused"] = True
            time.sleep(args.delay)
        records.append(record)
        print(f"{case['id']}: {ranks}", flush=True)
    summary = {
        "cases": len(records), "hit_at_7": sum(r["hit"] for r in records),
        "all_evidence_top_3": sum(r["top3"] for r in records),
        "independent_parity": sum(r["bare_parity"] for r in records if r["independent"]),
        "independent_cases": sum(r["independent"] for r in records),
    }
    path.write_text(json.dumps({"summary": summary, "records": records}, indent=2),
                    encoding="utf-8")
    print(json.dumps(summary), flush=True)
    if args.gate and (
        summary["hit_at_7"] != summary["cases"]
        or summary["independent_parity"] != summary["independent_cases"]
    ):
        raise SystemExit("Conversational stress retrieval regression")


if __name__ == "__main__":
    main()
