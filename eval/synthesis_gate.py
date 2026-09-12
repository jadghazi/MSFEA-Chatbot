"""CI: all required synthesis premises must survive production retrieval and its gate."""

from __future__ import annotations

import json
from pathlib import Path

from eval.synthesis_report import premise_hits
from msfea_bot.config import settings
from msfea_bot.generation.answer import passes_similarity_gate
from msfea_bot.generation.conversation import ConversationMessage, build_retrieval_query
from msfea_bot.retrieval.store import retrieval_depth, search


def main() -> None:
    cases = [json.loads(line) for name in ("synthesis_set.jsonl", "followup_set.jsonl")
             for line in (Path(__file__).parent / name).read_text(encoding="utf-8").splitlines()]
    passed = 0
    answerable = [c for c in cases if not c["should_refuse"]]
    for case in answerable:
        history = [ConversationMessage(**m) for m in case.get("history", [])]
        query = build_retrieval_query(case["question"], history)
        chunks = search(query, retrieval_depth(case["question"], settings.top_k),
                        department=case.get("department"))
        hits = premise_hits({"id": case["id"], "evidence_required": case["evidence_all"],
                             "chunks": [{"text": c.text} for c in chunks]})
        ok = all(hits) and passes_similarity_gate(chunks, settings.similarity_threshold)
        passed += ok
        if not ok:
            print(f"FAIL {case['id']}: premise hits={hits}")
    print(f"Synthesis all-premise retrieval + threshold: {passed}/{len(answerable)}")
    if passed != len(answerable):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
