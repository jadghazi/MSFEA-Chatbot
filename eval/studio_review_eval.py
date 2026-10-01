"""Manual, opt-in live staff review evaluation against frozen synthetic policies.

Use only a disposable dashboard: this submits private review jobs, never publishes.
python -m eval.studio_review_eval --url http://127.0.0.1:8020 --token-env STUDIO_TEST_TOKEN
"""

from __future__ import annotations

import argparse
import json
import os
import time
from http.client import RemoteDisconnected
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from uuid import uuid4


def request(url: str, token: str, path: str, body: dict[str, Any] | None = None) -> Any:
    payload = json.dumps(body).encode() if body is not None else None
    req = Request(url.rstrip("/") + path, data=payload, headers={
        "Authorization": "Bearer " + token, "Content-Type": "application/json",
    })
    with urlopen(req, timeout=30) as response:
        return json.load(response)


def evaluate(
    url: str, token: str, output: Path, limit: int | None = None, resume: bool = False,
) -> list[dict[str, Any]]:
    end = time.monotonic() + 120
    while True:
        try:
            request(url, token, "/ready")
            break
        except (HTTPError, URLError, RemoteDisconnected, TimeoutError):
            if time.monotonic() >= end:
                raise RuntimeError("The disposable dashboard did not become ready.") from None
            time.sleep(2)
    cases = [json.loads(line) for line in Path(__file__).with_name("studio_review_set.jsonl").read_text().splitlines()]
    results: list[dict[str, Any]] = (
        [json.loads(line) for line in output.read_text().splitlines()]
        if resume and output.exists() else []
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    for case in cases[:limit]:
        previous = next((item for item in results if item["id"] == case["id"]), None)
        if previous and previous["passed"]:
            continue
        intake = {key: case[key] for key in ("guidance", "question", "department", "programs")}
        job = request(url, token, "/admin/api/studio/reviews", {
            "intake": intake, "request_key": uuid4().hex,
        })
        end = time.monotonic() + 360
        while True:
            review = request(url, token, "/admin/api/studio/reviews/" + job["id"])
            if review["status"] in {"completed", "failed"} or time.monotonic() >= end:
                break
            time.sleep(2)
        report = review.get("report") or {}
        passed = (
            review["status"] == "completed"
            and report.get("classification") in case["expected"]
            and report.get("blocked") == case["blocked"]
            and (case["decision"] is None or report.get("requires_decision") == case["decision"])
            and report.get("draft", {}).get("answer") == case["guidance"]
        )
        if previous:
            results.remove(previous)
        results.append({
            "id": case["id"], "passed": passed, "expected": case, "review": review,
            "previous_attempts": [previous] if previous else [],
        })
        output.write_text("\n".join(json.dumps(item) for item in results) + "\n")
        print(case["id"], "PASS" if passed else "FAIL",
              report.get("classification") or review.get("error_code"), flush=True)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--token-env", default="STUDIO_TEST_TOKEN")
    parser.add_argument("--output", type=Path, default=Path("tmp/studio-live-results.jsonl"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    token = os.environ.get(args.token_env)
    if not token:
        parser.error("Set the test administrator token in the named environment variable.")
    results = evaluate(args.url, token, args.output, args.limit, args.resume)
    print(f"Staff review cases: {sum(item['passed'] for item in results)}/{len(results)}")
    raise SystemExit(any(not item["passed"] for item in results))


if __name__ == "__main__":
    main()
