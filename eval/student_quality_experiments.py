"""Compare generic overview query alternatives using existing canonical evidence."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from eval.metrics import evidence_present
from msfea_bot.config import settings
from msfea_bot.retrieval.store import search


def main() -> None:
    if "test-db" not in settings.database_url:
        raise ValueError("Use the isolated development service")
    cases = [json.loads(line) for line in Path("eval/student_quality_audit_set.jsonl").read_text(
        encoding="utf-8").splitlines()]
    # Subjects are experimental query inputs, never an application topic allowlist.
    subjects = {"Q01": "internships", "Q02": "internships", "Q03": "internship",
                "Q04": "CO-OP", "Q05": "IAESTE", "Q06": "CDC career preparation",
                "Q07": "mentorship", "Q08": "Career+", "Q10": "internship",
                "Q40": "CDC", "Q52": "internship", "Q53": "Approved Experience",
                "Q54": "CDC career support"}
    records = []
    for case in cases:
        if case["id"] not in subjects:
            continue
        subject = subjects[case["id"]]
        for name, query in (
            ("literal", case["question"]),
            ("definition", f"What is {subject}?"),
            ("guide", f"{subject}: overview purpose requirements how to apply"),
            ("start", f"{subject}: what it is and how to get started"),
        ):
            chunks = search(query, 12, department=case.get("department"))
            record = {"id": case["id"], "variant": name, "query": query,
                      "chunks": [asdict(chunk) for chunk in chunks],
                      "hits7": [evidence_present([c.text for c in chunks[:7]], item)
                                for item in case["evidence_all"]],
                      "hits12": [evidence_present([c.text for c in chunks], item)
                                 for item in case["evidence_all"]]}
            records.append(record)
            print(case["id"], name, record["hits7"], record["hits12"], flush=True)
    Path("eval/results/student_quality_query_experiments_20261007.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
