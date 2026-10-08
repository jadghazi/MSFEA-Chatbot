"""One opt-in provider diagnostic; print only safe quota identifiers, never raw errors."""
import json
from datetime import datetime, timezone
from typing import Any
from msfea_bot.llm import get_llm_provider, LLMError

rows = [json.loads(line) for line in open("eval/results/student_quality_completion_answers_final_20261007.jsonl", encoding="utf-8")]
prompt = next(row["prompt"] for row in rows if row["id"] == "Q19")
result: dict[str, Any] = {"utc": datetime.now(timezone.utc).isoformat(), "quota": [], "retry_delay": []}
try:
    get_llm_provider().generate(prompt)
    result["status"] = "available"
except LLMError as exc:
    result["status"] = type(exc).__name__
    cause = exc.__cause__
    details = getattr(cause, "details", None)
    response = getattr(cause, "response_json", None)
    if isinstance(response, dict):
        details = response.get("error", {}).get("details", details)
    if isinstance(details, dict):
        details = details.get("error", {}).get("details", [])
    for item in details if isinstance(details, list) else []:
        if not isinstance(item, dict):
            continue
        for violation in item.get("violations", []):
            result["quota"].append({key: violation[key] for key in
                ("quotaMetric", "quotaId", "quotaValue") if key in violation})
        if "retryDelay" in item:
            result["retry_delay"].append(item["retryDelay"])
print(json.dumps(result))
