"""Narrow regression checks; semantic/source review remains a separate recorded step."""

from __future__ import annotations

import re
from typing import Any


def checks(row: dict[str, Any]) -> dict[str, bool]:
    answer = row["answer"]
    text = answer["text"]
    result = {
        "refusal": answer["refused"] == row["should_refuse"],
        "citations": answer["refused"] or bool(answer["citations"]),
        "disclaimer": bool(answer["disclaimer"]),
        "no_operational_error": answer.get("error_code") is None,
    }
    if row["should_refuse"]:
        return result
    result["no_department_prefix"] = not bool(re.match(r"For ECE students\b", text, re.I))
    if row["id"] in {"f01-six-only", "f02-what-about", "f03-other-two",
                      "f04-paraphrase", "f05-confirm"}:
        result["two_research_weeks"] = bool(
            re.search(r"\b(?:2|two)\b", text, re.I) and re.search(r"\bresearch\b", text, re.I)
        )
        result["no_unstated_ten_week_rule"] = not bool(re.search(r"\b(?:10|ten)\b", text, re.I))
        result["no_unasked_procedures"] = not bool(
            re.search(r"\b(?:reports?|forms?|deadlines?|Moodle)\b", text, re.I)
        )
    if row["id"] in {"f01-six-only", "f04-paraphrase"}:
        result["direct_no"] = bool(re.match(r"No\b", text, re.I))
    if row["id"] == "f06-summer":
        result["summer_exception"] = bool(
            re.match(r"No\b", text, re.I) and re.search(r"\b(?:10|ten)\b", text, re.I)
        )
    if row["id"] == "f08-mech-no-six-plus-two":
        result["direct_no"] = bool(re.match(r"No\b", text, re.I))
        result["mech_scope_rejection"] = bool(
            re.search(
                r"\b(?:not|isn't|is not)\b.*\b(?:MECH|Mechanical|documented|option)\b",
                text,
                re.I,
            )
        )
        result["no_unrelated_split_rule"] = not bool(
            re.search(r"\b(?:4|four)[- ]week\b", text, re.I)
        )
        result["no_research_form"] = not bool(re.search(r"\b(?:form|Moodle)\b", text, re.I))
    if row["id"] == "f09-ece-six-plus-two":
        result["direct_yes"] = bool(re.match(r"Yes\b", text, re.I))
        result["two_research_weeks"] = bool(
            re.search(r"\b(?:2|two)\b", text, re.I)
            and re.search(r"\bresearch\b", text, re.I)
        )
        result["approval_condition"] = bool(re.search(r"\bapprov", text, re.I))
        result["no_unasked_procedures"] = not bool(
            re.search(r"\b(?:reports?|forms?|deadlines?|Moodle)\b", text, re.I)
        )
    return result
