"""Dated diagnostic: same frozen context, temporary model with medium thinking.

This is not a production configuration change or an accepted answer trace. The
existing curation provider configuration supplies medium thinking; no curation
workflow, publication or database write is invoked. Do not use these traces as
default-thinking prompt-reuse inputs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

from eval import student_quality_audit
from msfea_bot.config import settings
from msfea_bot.llm.gemini import GeminiProvider


def main() -> None:
    results = Path("eval/results")
    stem = results / "student_quality_continue_medium_20261007"
    prior_paths = [results / "student_quality_continue_parent_answers_20261007.jsonl",
                   results / "student_quality_continue_generalization_final_20261007.jsonl"]
    ids = {*(f"P{i:02}" for i in range(1, 9)), "R31"}
    rows = [row for path in prior_paths
            for line in path.read_text(encoding="utf-8").splitlines()
            if (row := json.loads(line))["id"] in ids]
    if len(rows) != len(ids) or {row["id"] for row in rows} != ids:
        raise ValueError("Require the nine frozen conditional-reasoning probes")
    if settings.llm_model != "gemini-3.1-flash-lite":
        raise ValueError("This trial requires the user-authorized temporary model")
    cases = Path(str(stem) + "_cases.jsonl")
    retrieval = Path(str(stem) + "_retrieval.jsonl")
    raw = Path(str(stem) + "_raw.jsonl")
    for path, records in ((cases, [{key: row[key] for key in (
        "id", "category", "question", "department", "expected_behavior")}
                                  for row in rows]), (retrieval, rows)):
        with path.open("x", encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    # All provider calls still go through the implemented llm/ adapter. Its
    # curation purpose selects MEDIUM without altering student-model defaults.
    sys.argv = ["reasoning-trial", "--cases", str(cases), "--replay-retrieval",
                str(retrieval), "--live-ids", "all", "--delay", "12",
                "--output", str(raw)]
    with patch.object(student_quality_audit, "get_llm_provider",
                      return_value=GeminiProvider(purpose="curation_")):
        student_quality_audit.main()
    parameters = {"model": settings.llm_model, "thinking_level": "medium",
                  "temperature": settings.llm_temperature, "seed": settings.llm_seed,
                  "max_output_tokens": settings.llm_max_output_tokens}
    with Path(str(stem) + "_answers.jsonl").open("x", encoding="utf-8") as stream:
        for line in raw.read_text(encoding="utf-8").splitlines():
            stream.write(json.dumps({**json.loads(line), "generation_config": parameters,
                                    "diagnostic_only": True}, ensure_ascii=False) + "\n")
    print(json.dumps(parameters))


if __name__ == "__main__":
    main()
