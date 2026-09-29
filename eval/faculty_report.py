"""Summarize a faculty-question evaluation without hiding incomplete provider calls."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def latest(path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            record = json.loads(line)
            records[str(record["id"])] = record
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--retrieval", type=Path, required=True)
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--judgments", type=Path)
    parser.add_argument("--review-labels", type=Path)
    args = parser.parse_args()
    cases = latest(args.cases)
    retrieval = latest(args.retrieval)
    answers = latest(args.answers) if args.answers and args.answers.exists() else {}
    judgments = latest(args.judgments) if args.judgments and args.judgments.exists() else {}
    reviews = latest(args.review_labels) if args.review_labels and args.review_labels.exists() else {}
    stale_judgments: list[str] = []
    for case_id, record in list(judgments.items()):
        answer = answers.get(case_id, {}).get("answer")
        answer_hash = (hashlib.sha256(json.dumps(answer, sort_keys=True).encode()).hexdigest()
                       if answer else None)
        if record.get("answer_sha256") != answer_hash:
            stale_judgments.append(case_id)
            del judgments[case_id]

    print(f"Frozen faculty cases: {len(cases)} from "
          f"{len({(c['source_sheet'], c['question_cell']) for c in cases.values()})} workbook rows")
    retrieved = [retrieval[cid] for cid in cases if cid in retrieval and not retrieval[cid].get("error")]
    hits = sum(bool(r["source_document_hit"]) for r in retrieved)
    print(f"Source-document hit@7, all cases: {hits}/{len(retrieved)} "
          f"({hits / len(retrieved):.1%})" if retrieved else "Source-document hit: unavailable")
    answerable_retrieved = [r for r in retrieved if not cases[r["id"]]["should_refuse"]]
    if answerable_retrieved:
        answerable_hits = sum(bool(r["source_document_hit"]) for r in answerable_retrieved)
        print(f"Answerable source-document hit@7: {answerable_hits}/{len(answerable_retrieved)} "
              f"({answerable_hits / len(answerable_retrieved):.1%})")
    primary_retrieved = [r for r in answerable_retrieved
                         if cases[r["id"]]["primary_workbook_case"]]
    if primary_retrieved:
        primary_hits = sum(bool(r["source_document_hit"]) for r in primary_retrieved)
        print(f"Original-question source-document hit: {primary_hits}/{len(primary_retrieved)} "
              f"({primary_hits / len(primary_retrieved):.1%})")
    by_department: dict[str, Counter[str]] = defaultdict(Counter)
    for case_id, case in cases.items():
        dept = str(case["department"])
        if case_id in retrieval and not retrieval[case_id].get("error"):
            by_department[dept]["retrieval_total"] += 1
            by_department[dept]["retrieval_hit"] += bool(retrieval[case_id]["source_document_hit"])
        answer = answers.get(case_id)
        if answer and not answer.get("error") and answer.get("answer"):
            by_department[dept]["answer_completed"] += 1
            by_department[dept]["answer_refused"] += bool(answer["answer"]["refused"])
            if not answer["answer"]["refused"]:
                by_department[dept]["substantive"] += 1
                by_department[dept]["citation_present"] += bool(answer["answer"]["citations"])
            by_department[dept]["disclaimer_present"] += "AI-generated" in str(
                answer["answer"].get("disclaimer", "")
            )
        judgment = judgments.get(case_id, {}).get("judgment")
        if judgment and not judgment["uncertain"]:
            by_department[dept]["judged"] += 1
            by_department[dept]["correct"] += bool(judgment["overall_correct"])
            by_department[dept]["evidence_sufficient"] += bool(
                judgment.get("retrieval_sufficient", False)
            )

    completed_answers = sum(c["answer_completed"] for c in by_department.values())
    refusal_checked = [cid for cid in cases if cid in answers and not answers[cid].get("error")
                       and answers[cid].get("answer")]
    refusal_matches = sum(bool(answers[cid]["answer"]["refused"]) ==
                          bool(cases[cid]["should_refuse"]) for cid in refusal_checked)
    print(f"Completed answers: {completed_answers}/{len(cases)}; "
          f"provider/unattempted: {len(cases) - completed_answers}")
    print(f"Refusal-behavior match: {refusal_matches}/{len(refusal_checked)}"
          if refusal_checked else "Refusal-behavior match: unavailable")
    print(f"Refusals: {sum(c['answer_refused'] for c in by_department.values())}; "
          f"citations on substantive answers: "
          f"{sum(c['citation_present'] for c in by_department.values())}/"
          f"{sum(c['substantive'] for c in by_department.values())}; disclaimers: "
          f"{sum(c['disclaimer_present'] for c in by_department.values())}/"
          f"{completed_answers}")
    judged = sum(c["judged"] for c in by_department.values())
    correct = sum(c["correct"] for c in by_department.values())
    if judged:
        evidence_sufficient = sum(c["evidence_sufficient"] for c in by_department.values())
        print(f"Judge-rated policy-evidence sufficiency, all judged: "
              f"{evidence_sufficient}/{judged} ({evidence_sufficient / judged:.1%})")
        answerable_judged = [cid for cid, case in cases.items() if not case["should_refuse"]
                             and judgments.get(cid, {}).get("judgment")
                             and not judgments[cid]["judgment"]["uncertain"]]
        if answerable_judged:
            answerable_evidence = sum(bool(judgments[cid]["judgment"][
                "retrieval_sufficient"]) for cid in answerable_judged)
            print(f"Answerable policy-evidence sufficiency: {answerable_evidence}/"
                  f"{len(answerable_judged)} "
                  f"({answerable_evidence / len(answerable_judged):.1%})")
        print(f"Judge-rated answer accuracy: {correct}/{judged} ({correct / judged:.1%}); "
              f"unjudged/uncertain: {len(cases) - judged}")
        primary_judged = [cid for cid, case in cases.items() if case["primary_workbook_case"]
                          and judgments.get(cid, {}).get("judgment")
                          and not judgments[cid]["judgment"]["uncertain"]]
        if primary_judged:
            primary_correct = sum(bool(judgments[cid]["judgment"]["overall_correct"])
                                  for cid in primary_judged)
            print(f"Original-question judge-rated accuracy: "
                  f"{primary_correct}/{len(primary_judged)} "
                  f"({primary_correct / len(primary_judged):.1%})")
    else:
        print("Judge-rated answer accuracy: unavailable")
    if stale_judgments:
        print(f"Stale judgments excluded: {len(stale_judgments)}")
    print("Department | source document | answers completed | evidence / judged | accurate / judged")
    for dept in ("ece", "mech", "chem", "iem", "cee"):
        row = by_department[dept]
        print(f"{dept:4} | {row['retrieval_hit']}/{row['retrieval_total']} | "
              f"{row['answer_completed']} | {row['evidence_sufficient']}/{row['judged']} | "
              f"{row['correct']}/{row['judged']}")
    if retrieval:
        misses = [cid for cid, case in cases.items() if not case["should_refuse"]
                  and cid in retrieval and not retrieval[cid].get("source_document_hit", False)]
        print("Answerable source-document misses: " + (", ".join(misses) or "none"))
    if judgments:
        failed = [cid for cid in cases if judgments.get(cid, {}).get("judgment") and not
                  judgments[cid]["judgment"]["overall_correct"]]
        print("Judge-rated failures: " + (", ".join(failed) or "none"))
    if reviews:
        reviewed = [cid for cid in cases if cid in reviews]
        review_correct = sum(bool(reviews[cid]["overall_correct"]) for cid in reviewed)
        print(f"Codex source-reviewed sample: {review_correct}/{len(reviewed)} correct")
        compared = [cid for cid in reviewed if judgments.get(cid, {}).get("judgment")]
        disagreements = [cid for cid in compared if bool(reviews[cid]["overall_correct"])
                         != bool(judgments[cid]["judgment"]["overall_correct"])]
        if compared:
            print(f"Judge agreement with Codex source review: "
                  f"{len(compared) - len(disagreements)}/{len(compared)}; "
                  f"disagreements: {', '.join(disagreements) or 'none'}")


if __name__ == "__main__":
    main()
