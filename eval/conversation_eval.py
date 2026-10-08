"""Paired retrieval audit for short conversations and topic changes.

The default path makes no LLM requests. Use --live-ids sparingly to review answers.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from msfea_bot.config import settings
from msfea_bot.generation.answer import retrieve_context
from msfea_bot.generation.conversation import ConversationMessage
from msfea_bot.retrieval.store import RetrievedChunk, retrieval_depth


def _rank(
    chunks: list[RetrievedChunk], section: str | None,
    evidence: str | None, source_doc: str | None,
) -> int | None:
    for rank, chunk in enumerate(chunks, 1):
        if evidence is not None and evidence.casefold() in chunk.text.casefold() and (
            source_doc is None or chunk.source_doc == source_doc
        ):
            return rank
        if evidence is None and section and section in chunk.section:
            return rank
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--live-ids", help="Comma-separated case IDs to answer with the LLM")
    parser.add_argument("--delay", type=float, default=6.0)
    args = parser.parse_args()
    live_ids = set(args.live_ids.split(",")) if args.live_ids else set()
    cases = [
        json.loads(line)
        for line in (Path(__file__).parent / "conversation_set.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    records: list[dict[str, Any]] = []
    for case in cases:
        question = case["question"]
        history = [ConversationMessage(**item) for item in case["history"]]
        k = retrieval_depth(question, settings.top_k)
        # Compare the same production pipeline with and without history, including
        # linked context and conservative recovery. Expected evidence is unchanged.
        bare = retrieve_context(question, k, case["department"], None)
        chunks = retrieve_context(question, k, case["department"], history)
        expected = case.get("expected_section")
        expected_evidence = case.get("expected_evidence")
        expected_source_doc = case.get("expected_source_doc")
        record = {
            "id": case["id"],
            "independent": case["independent"],
            "expected_section": expected,
            "expected_evidence": expected_evidence,
            "expected_source_doc": expected_source_doc,
            "max_expected_rank": case.get("max_expected_rank"),
            "bare_rank": _rank(bare, expected, expected_evidence, expected_source_doc),
            "history_rank": _rank(chunks, expected, expected_evidence, expected_source_doc),
            "bare_ids": [chunk.id for chunk in bare],
            "history_ids": [chunk.id for chunk in chunks],
            "history_sections": [chunk.section for chunk in chunks],
        }
        if case["id"] in live_ids:
            from msfea_bot.generation.answer import generate_answer

            answer = generate_answer(question, department=case["department"], history=history)
            record["answer"] = {
                "text": answer.text,
                "citations": answer.citations,
                "refused": answer.refused,
                "error_code": answer.error_code,
            }
            print(f"ANSWER {case['id']}: {answer.text}", flush=True)
            time.sleep(args.delay)
        records.append(record)
        print(
            f"{case['id']}: bare={record['bare_rank']} history={record['history_rank']} "
            f"same={record['bare_ids'] == record['history_ids']}",
            flush=True,
        )
    independent = [record for record in records if record["independent"]]
    summary = {
        "cases": len(records),
        "evidence_hit_at_7": sum(record["history_rank"] is not None for record in records),
        "evidence_top_1": sum(record["history_rank"] == 1 for record in records),
        "independent_exact_parity": sum(
            record["bare_ids"] == record["history_ids"] for record in independent
        ),
        "independent_cases": len(independent),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"summary": summary, "records": records}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary), flush=True)
    if args.gate and (
        summary["evidence_hit_at_7"] != summary["cases"]
        or summary["independent_exact_parity"] != summary["independent_cases"]
        or any(
            record["max_expected_rank"] is not None
            and (record["history_rank"] is None
                 or record["history_rank"] > record["max_expected_rank"])
            for record in records
        )
    ):
        raise SystemExit("Conversational retrieval regression")


if __name__ == "__main__":
    main()
