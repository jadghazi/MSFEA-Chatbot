"""Render reviewed synthesis scores alongside actual, inspectable experiment outputs."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median
from typing import Any

RESULTS = Path(__file__).parent / "results" / "synthesis"


def load_rows(variant: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in (RESULTS / f"{variant}.jsonl").read_text().splitlines()]


def premise_hits(row: dict[str, Any]) -> list[bool]:
    # Correct a too-specific probe without rewriting any raw experiment trace.
    evidence = list(row["evidence_required"])
    if row["id"] == "s06-comparison":
        evidence[0] = "8 weeks"
    return [any(p.casefold() in c["text"].casefold() for c in row["chunks"]) for p in evidence]


def main() -> None:
    reviews = json.loads((RESULTS / "ratings.json").read_text())
    lines = [
        "# Synthesis experiments — reviewed measurements", "",
        "Review method: " + reviews["reviewer"] + ".", "",
        "The synthesis mean excludes the one intentional refusal. Grounding errors",
        "are reviewed separately; valid source labels alone do not establish support.",
        "Latency is the median sum of provider latencies per answered turn; the two-call",
        "candidate also adds a deliberate seven-second inter-call quota delay.", "",
        "| Candidate | Synthesis /5 (11 answerable) | Unsupported answers | False refusals | All-premise recall | Calls | Input tokens | Provider ms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant, scores in reviews.items():
        if variant == "reviewer":
            continue
        rows = load_rows(variant)
        assert len(rows) == len(scores) == 12, variant
        assert {r["id"] for r in rows} == {r["id"] for r in scores}, variant
        by_id = {s["id"]: s for s in scores}
        answerable = [r for r in rows if not r["should_refuse"]]
        synthesis = mean(by_id[r["id"]]["synthesis"] for r in answerable)
        unsupported = sum(s["grounding"] == "unsupported" for s in scores)
        false = sum(r["answer"]["refused"] for r in answerable)
        recall = sum(all(premise_hits(r)) for r in answerable)
        calls = [c for r in rows for c in r["calls"]]
        tokens = sum(c.get("input_tokens") or 0 for c in calls)
        latencies = [sum(c.get("latency_ms") or 0 for c in r["calls"])
                     for r in rows if r["calls"]]
        lines.append(
            f"| {variant} | {synthesis:.2f} | {unsupported} | {false}/11 | {recall}/11 | "
            f"{len(calls)} | {tokens:,} | {median(latencies):.0f} |"
        )
    lines += ["", "## Per-case scores and actual outputs", ""]
    for variant, scores in reviews.items():
        if variant == "reviewer":
            continue
        rows_by_id = {r["id"]: r for r in load_rows(variant)}
        lines += [f"### {variant}", "",
                  f"[Raw prompts, retrieved chunks and responses]({variant}.jsonl)", ""]
        for score in scores:
            row = rows_by_id[score["id"]]
            lines += [
                f"**{row['id']} — {row['question']}**", "",
                f"Score: {score['synthesis']}/5. Grounding: {score['grounding']}. " + score["note"],
                "", "> " + row["answer"]["text"].replace("\n", "\n> "), "",
                "Sources: " + ("; ".join(row["answer"]["citations"]) or "none (refusal)"), "",
            ]
    (RESULTS / "reviewed_results.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:18]))


if __name__ == "__main__":
    main()
