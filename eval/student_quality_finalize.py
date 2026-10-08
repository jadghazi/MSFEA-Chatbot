"""Assemble immutable paired traces and verify they match the final prompt code."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any
from unittest.mock import patch

from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import ConversationMessage
from msfea_bot.llm import GenerationResult
from msfea_bot.retrieval.store import RetrievedChunk

RESULTS = Path("eval/results")


def merged(names: list[str]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for name in names:
        for line in (RESULTS / name).read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            records[row["id"]] = {**row, "trace_file": name}
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--completion", action="store_true", help="Verify the 114-case completion candidate")
    parser.add_argument("--partial", action="store_true", help="Preserve verified completion results without claiming full acceptance")
    parser.add_argument("--alternate", action="store_true", help="Verify separately labelled temporary-model diagnostic answers")
    parser.add_argument("--after-traces", nargs="+", help="Successful and failed answer-attempt filenames under eval/results")
    parser.add_argument("--scoped", action="store_true", help="Verify the candidate with process-stage filtering and topic parent context")
    parser.add_argument("--contextual", action="store_true", help="Verify the final catalogue scope and grounded-link candidate")
    parser.add_argument("--before-traces", nargs="+", help="Baseline trace filenames under eval/results")
    args = parser.parse_args()
    if args.partial and not args.completion:
        parser.error("--partial requires --completion")
    if args.alternate and not args.completion:
        parser.error("--alternate requires --completion")
    if args.scoped and not (args.completion and args.alternate):
        parser.error("--scoped requires --completion --alternate")
    if args.contextual and not args.scoped:
        parser.error("--contextual requires --scoped")
    before_names = [
        "student_quality_baseline_20261007.jsonl",
        "student_quality_baseline_replay_remaining_20261007.jsonl",
        "student_quality_holdout_frozen_before_20261007.jsonl",
    ]
    after_names = [
        "student_quality_answers_after_20261007.jsonl",
        "student_quality_holdout_answers_after_20261007.jsonl",
        "student_quality_status_final_main_20261007.jsonl",
        "student_quality_status_final_holdout_20261007.jsonl",
    ]
    expected_count = 80
    prefix = "student_quality"
    if args.completion:
        before_names = ["student_quality_paired_after_20261007.jsonl",
                        "student_quality_classes_before_20261007.jsonl",
                        "student_quality_comparative_before_20261007.jsonl"]
        after_names = ["student_quality_completion_answers_final_20261007.jsonl",
                       "student_quality_completion_answers_resumed_20261007.jsonl",
                       "student_quality_completion_smoke_release_20261007.jsonl"]
        expected_count = 114
        prefix = "student_quality_completion"
        if args.alternate:
            after_names = ["student_quality_completion_alternate_answers_20261007.jsonl"]
            prefix += "_alternate"
        if args.scoped:
            before_names = ["student_quality_completion_alternate_answers_20261007.jsonl"]
            after_names = ["student_quality_completion_scoped_answers_20261007.jsonl"]
            prefix = "student_quality_completion_scoped_alternate"
            if args.contextual:
                after_names = ["student_quality_completion_catalogue_final_reused_20261007.jsonl"]
                prefix = "student_quality_completion_context_alternate"
    if args.after_traces:
        after_names = args.after_traces
    if args.before_traces:
        before_names = args.before_traces
    before = merged(before_names)
    attempts = [json.loads(line) for name in after_names
                for line in (RESULTS / name).read_text(encoding="utf-8").splitlines()]
    after = {row["id"]: {**row, "trace_file": name}
             for name in after_names
             for line in (RESULTS / name).read_text(encoding="utf-8").splitlines()
             if (row := json.loads(line)).get("answer") is not None
             and "provider_error" not in row}
    if args.partial:
        frozen_name = ("student_quality_completion_catalogue_retrieval_20261007.jsonl" if args.contextual
                       else "student_quality_completion_scope_gate_retrieval_20261007.jsonl" if args.scoped
                       else "student_quality_completion_retrieval_release_20261007.jsonl")
        for case_id, row in merged([frozen_name]).items():
            if row["prompt"] is None and case_id not in after:
                after[case_id] = {**row, "verification": "local deterministic answer"}
    mismatches: list[str] = []
    for case_id, row in after.items():
        prompts: list[str] = []

        class Recorder:
            def generate(self, prompt: str) -> GenerationResult:
                prompts.append(prompt)
                return GenerationResult(text=pipeline.REFUSAL_MARKER)

        chunks = [RetrievedChunk(**chunk) for chunk in row["chunks"]]
        history = [ConversationMessage(**message) for message in row.get("history", [])]
        with patch.object(pipeline, "retrieve_context", return_value=chunks):
            result = pipeline.generate_answer(
                row["question"], k=row["k"], department=row.get("department"),
                history=history, provider=Recorder(),
            )
        if (prompts[0] if prompts else None) != row["prompt"]:
            mismatches.append(case_id)
        if not prompts:
            if row.get("verification") == "local deterministic answer":
                row["answer"] = asdict(result)
            elif asdict(result) != row["answer"]:
                mismatches.append(case_id + ": local answer")
    if len(before) != expected_count or not set(after).issubset(before):
        raise ValueError("Baseline or candidate case IDs do not match the frozen set")
    if not args.partial and (set(before) != set(after) or len(after) != expected_count):
        raise ValueError(f"Paired audit must contain the same {expected_count} cases")
    if mismatches:
        raise ValueError(f"Final prompt differs from live trace: {mismatches}")
    models = sorted({row["model"] for row in after.values() if row.get("prompt") is not None})
    if len(models) != 1:
        raise ValueError(f"Do not combine model configurations in one result: {models}")
    if args.partial:
        prefix += "_partial"
    for name, records in (("before", {key: before[key] for key in after}), ("after", after)):
        (RESULTS / f"{prefix}_paired_{name}_20261007.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n"
                    for _, row in sorted(records.items())), encoding="utf-8",
        )
    paths = [Path("eval/student_quality_audit_set.jsonl"),
             Path("eval/student_quality_holdout_set.jsonl"),
             *Path("src/msfea_bot/generation").glob("*.py"),
             Path("src/msfea_bot/ingestion/chunking.py"),
             Path("src/msfea_bot/retrieval/store.py"),
             *Path("kb/normalized").glob("*.md")]
    if args.completion:
        paths += [Path("eval/student_quality_failure_classes_set.jsonl"),
                  Path("eval/student_quality_comparative_validation_set.jsonl"),
                  Path("eval/student_quality_completion_set.jsonl"),
                  Path("src/msfea_bot/retrieval/repair.py")]
    if args.scoped:
        paths.append(Path("src/msfea_bot/retrieval/scope.py"))
        paths.append(Path("src/msfea_bot/curation/service.py"))
    reuse_paths = sorted({row["generation_reuse_from"] for row in after.values()
                          if row.get("generation_reuse_from")})
    reuse_errors = sum("provider_error" in json.loads(line) for name in reuse_paths
                       for line in Path(name).read_text(encoding="utf-8").splitlines())
    manifest = {
        "baseline_commit": "a0caa4d", "cases": len(after),
        "expected_cases": expected_count, "complete": len(after) == expected_count,
        "missing_case_ids": sorted(set(before) - set(after)),
        "verified_provider_answers": sum(row.get("prompt") is not None for row in after.values()),
        "verified_local_answers": sum(row.get("prompt") is None for row in after.values()),
        "reused_provider_answers": sum(bool(row.get("generation_reuse_from")) for row in after.values()),
        "fresh_provider_answers": sum(row.get("prompt") is not None
                                      and not row.get("generation_reuse_from") for row in after.values()),
        "comparison": ("same temporary model: before scope/overview refinement to final candidate" if args.scoped
                       else "first local candidate to completion candidate" if args.completion
                       else "original to first candidate"),
        "answer_models": models,
        "baseline_answer_models": sorted({row["model"] for row in before.values()}),
        "temporary_model_diagnostic": args.alternate,
        "production_model_acceptance": False,
        "final_prompt_matches_live_traces": True,
        "provider_errors_before": sum("provider_error" in row for row in before.values()),
        "provider_errors_after": sum("provider_error" in row for row in after.values()),
        "retained_failed_answer_attempts": sum("provider_error" in row for row in attempts),
        "reuse_source_files": reuse_paths,
        "retained_provider_errors_in_reuse_sources": reuse_errors,
        "attempt_files": after_names,
        "source_review": "Codex review, not independent human calibration",
        "invalid_phrase_probe": "Q47: generic report length conflicts with ECE override; excluded from phrase metrics",
        "sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
    }
    (RESULTS / f"{prefix}_manifest_20261007.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8",
    )
    print(json.dumps({key: value for key, value in manifest.items() if key != "sha256"}, indent=2))


if __name__ == "__main__":
    main()
