"""Merge resumable Oracle evaluation shards in frozen case order."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--inputs", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    case_ids = [json.loads(s)["id"] for s in args.cases.read_text(encoding="utf-8").splitlines()]
    records: dict[str, dict[str, Any]] = {}
    for path in args.inputs:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            case_id = str(row["id"])
            if case_id not in case_ids:
                raise ValueError(f"Unknown case {case_id} in {path}")
            if not row.get("error") or case_id not in records or records[case_id].get("error"):
                records[case_id] = row
    missing = [case_id for case_id in case_ids if case_id not in records or
               records[case_id].get("error")]
    if args.require_complete and missing:
        raise SystemExit(f"Incomplete evaluation: {len(missing)} cases: {', '.join(missing)}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(records[case_id], ensure_ascii=False) + "\n"
                for case_id in case_ids if case_id in records), encoding="utf-8"
    )
    print(f"Merged {len(records)}/{len(case_ids)} cases; {len(missing)} missing or provider errors")


if __name__ == "__main__":
    main()
