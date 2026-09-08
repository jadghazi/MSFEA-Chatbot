"""Read-only retrieval/gate audit across golden, threshold and synthesis cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eval.loader import load_golden_set
from eval.metrics import evidence_present
from eval.threshold_eval import load_threshold_set
from msfea_bot.generation.conversation import ConversationMessage, build_retrieval_query
from msfea_bot.retrieval.store import search


def main() -> None:
    root = Path(__file__).parent
    cases: list[dict[str, Any]] = [
        {"id": i.id, "question": i.question, "department": i.department,
         "history": i.history, "valid": True, "suite": "golden",
         "evidence": [i.evidence] if i.evidence else []}
        for i in load_golden_set() if not i.should_refuse
    ]
    cases += [
        {"id": i.id, "question": i.question, "department": i.department,
         "history": [], "valid": i.should_pass_threshold, "suite": "threshold",
         "evidence": []}
        for i in load_threshold_set()
    ]
    cases += [
        {"id": i["id"], "question": i["question"], "department": i.get("department"),
         "history": [ConversationMessage(**m) for m in i.get("history", [])],
         "valid": not i["should_refuse"], "suite": "synthesis",
         "evidence": i["evidence_all"]}
        for i in map(json.loads, (root / "synthesis_set.jsonl").read_text().splitlines())
    ]
    rows: list[dict[str, Any]] = []
    for case in cases:
        query = build_retrieval_query(case["question"], case["history"])
        for k in (3, 7, 12):
            chunks = search(query, k, department=case["department"])
            rows.append({
                "id": case["id"], "suite": case["suite"], "valid": case["valid"], "k": k,
                "first_score": chunks[0].score if chunks else -1,
                "max_score": max((c.score for c in chunks), default=-1),
                "evidence_hits": [evidence_present([c.text for c in chunks], p)
                                  for p in case["evidence"]],
            })
    output = root / "results" / "synthesis" / "retrieval_audit.json"
    output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    for k in (3, 7, 12):
        subset = [r for r in rows if r["k"] == k]
        valid = [r for r in subset if r["valid"]]
        off = [r for r in subset if not r["valid"] and r["suite"] == "threshold"]
        print(f"k={k}", flush=True)
        for metric in ("first_score", "max_score"):
            print(metric, "valid passed", sum(r[metric] >= .60 for r in valid), len(valid),
                  "off-topic blocked", sum(r[metric] < .60 for r in off), len(off), flush=True)
        for suite in ("golden", "synthesis"):
            evid = [r for r in subset if r["suite"] == suite and r["evidence_hits"]]
            print(suite, "all-premise recall", sum(all(r["evidence_hits"]) for r in evid),
                  len(evid), "misses", [r["id"] for r in evid if not all(r["evidence_hits"])],
                  flush=True)


if __name__ == "__main__":
    main()
