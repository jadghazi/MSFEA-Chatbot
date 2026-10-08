"""Summarize trace coverage without pretending lexical checks measure correctness."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any

from eval.metrics import evidence_present


def rows(name: str) -> dict[str, dict[str, Any]]:
    path = Path("eval/results") / name
    return {row["id"]: row for row in (json.loads(line) for line in path.read_text(
        encoding="utf-8").splitlines())}


def coverage(records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    # Q47's authored generic template phrase is invalid for the ECE override.
    evidence = [row for row in records.values() if row.get("evidence_all") and row["id"] != "Q47"]
    return {
        "cases": len(records), "evidence_cases": len(evidence),
        "all_evidence_hits": sum(all(row["evidence_hits"]) for row in evidence),
        "evidence_phrases": sum(len(row["evidence_hits"]) for row in evidence),
        "evidence_phrase_hits": sum(sum(row["evidence_hits"]) for row in evidence),
        "all_context_hits": sum(all(row["context_hits"]) for row in evidence),
        "live_answers": sum(row.get("answer") is not None for row in records.values()),
        "provider_errors": sum("provider_error" in row for row in records.values()),
        "overview": {
            "cases": sum(row["category"] == "overview" for row in evidence),
            "all_evidence_hits": sum(row["category"] == "overview" and all(row["evidence_hits"])
                                     for row in evidence),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--completion", action="store_true")
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--scoped", action="store_true")
    parser.add_argument("--contextual", action="store_true")
    args = parser.parse_args()
    if args.scoped and not args.completion:
        parser.error("--scoped requires --completion")
    if args.contextual and not args.scoped:
        parser.error("--contextual requires --scoped")
    if args.completion:
        if args.retrieval_only:
            before = rows("student_quality_paired_after_20261007.jsonl")
            before.update(rows("student_quality_classes_before_20261007.jsonl"))
            before.update(rows("student_quality_comparative_before_20261007.jsonl"))
            after = rows("student_quality_completion_retrieval_release_20261007.jsonl")
            if args.scoped:
                after = rows("student_quality_completion_scope_gate_retrieval_20261007.jsonl")
            if args.contextual:
                after = rows("student_quality_completion_catalogue_retrieval_20261007.jsonl")
        else:
            prefix = "student_quality_completion_scoped_alternate" if args.scoped else "student_quality_completion"
            if args.contextual:
                prefix = "student_quality_completion_context_alternate"
            before = rows(f"{prefix}_paired_before_20261007.jsonl")
            after = rows(f"{prefix}_paired_after_20261007.jsonl")
        output: dict[str, Any] = {"before": coverage(before), "after": coverage(after)}
        output["categories"] = {
            category: {
                variant: coverage({key: row for key, row in records.items()
                                   if row["category"] == category})
                for variant, records in (("before", before), ("after", after))
            } for category in sorted({row["category"] for row in after.values()})
        }
        output["seed_vs_context"] = {
            variant: {
                "cases_with_companions": sum(row.get("companion_count", 0) > 0
                                             for row in records.values()),
                "repaired_queries": sum(any("query_correction" in c["metadata"]
                                            for c in row["chunks"])
                                        for row in records.values()),
                "supplemental_spelling_cases": sum(any(
                    c["metadata"].get("retrieval_role") == "spelling_candidate"
                    for c in row["chunks"]) for row in records.values()),
                "primary_seed_all_evidence_hits": sum(all(evidence_present(
                    [c["text"] for c in row["chunks"]
                     if c["metadata"].get("retrieval_role") not in {"companion", "spelling_candidate"}],
                    phrase) for phrase in row["evidence_all"])
                    for row in records.values() if row.get("evidence_all") and row["id"] != "Q47"),
            } for variant, records in (("before", before), ("after", after))
        }
        retrieval = rows("student_quality_completion_scope_gate_retrieval_20261007.jsonl" if args.scoped
                         else "student_quality_completion_retrieval_release_20261007.jsonl")
        # The sufficiency-gate trace replays the same immutable scoped search;
        # serving timings come from the actual retrieval run, not replay overhead.
        if args.scoped:
            retrieval = rows("student_quality_completion_scoped_retrieval_20261007.jsonl")
        if args.contextual:
            retrieval = rows("student_quality_completion_context_retrieval_20261007.jsonl")
        times = sorted(row["retrieval_ms"] for row in retrieval.values())
        output["warm_local_retrieval_ms"] = {
            "median": statistics.median(times), "p95": times[int(len(times) * 0.95)],
            "note": "Isolated local run with concurrent checks; not serving latency",
        }
        output_name = "retrieval_metrics" if args.retrieval_only else "metrics"
        prefix = "student_quality_completion_scoped" if args.scoped else "student_quality_completion"
        if args.contextual:
            prefix = "student_quality_completion_context"
        Path(f"eval/results/{prefix}_{output_name}_20261007.json").write_text(
            json.dumps(output, indent=2), encoding="utf-8")
        print(json.dumps(output, indent=2))
        return
    baseline = rows("student_quality_baseline_20261007.jsonl")
    for case_id, row in rows("student_quality_baseline_replay_remaining_20261007.jsonl").items():
        baseline[case_id] = row
    output = {"baseline": coverage(baseline),
              "k12": coverage(rows("student_quality_k12_20261007.jsonl")),
              "candidate": coverage(rows("student_quality_retrieval_frozen_20261007.jsonl")),
              "holdout_before": coverage(rows("student_quality_holdout_frozen_before_20261007.jsonl")),
              "holdout_after": coverage(rows("student_quality_holdout_retrieval_after_20261007.jsonl"))}
    Path("eval/results/student_quality_metrics_20261007.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
