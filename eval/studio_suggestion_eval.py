"""Opt-in source-coverage checks on a disposable Studio; never creates KB entries."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError
from uuid import uuid4

from eval.studio_review_eval import request
from msfea_bot.curation.assistance import SUGGESTION_PROMPT_VERSION


def wait(url: str, token: str, path: str) -> dict[str, Any]:
    deadline = time.monotonic() + 360
    while True:
        job: dict[str, Any] = request(url, token, path)
        if job['status'] in {'completed', 'failed'} or time.monotonic() >= deadline:
            return job
        time.sleep(2)


def evaluate(url: str, token: str, output: Path, resume: bool = False) -> list[dict[str, Any]]:
    if output.exists() and not resume:
        raise FileExistsError('Use --resume to retain earlier attempts or choose a new output file.')
    results: list[dict[str, Any]] = [json.loads(line) for line in output.read_text().splitlines()] if output.exists() else []
    cases = [json.loads(line) for line in Path(__file__).with_name('studio_suggestion_set.jsonl').read_text().splitlines()]
    output.parent.mkdir(parents=True, exist_ok=True)
    for case in cases:
        previous = next((item for item in results if item['id'] == case['id']), None)
        if previous and previous['passed'] and previous.get('suggestion',{}).get('prompt_version') == SUGGESTION_PROMPT_VERSION:
            continue
        record: dict[str, Any] = {'id': case['id'], 'passed': False, 'previous_attempts': [previous] if previous else []}
        review = previous.get('review') if previous else None
        if not review or review['status'] != 'completed':
            intake = {key: case[key] for key in ('guidance', 'question', 'department', 'programs')}
            queued = request(url, token, '/admin/api/studio/reviews', {'intake': intake, 'request_key': uuid4().hex})
            review = wait(url, token, '/admin/api/studio/reviews/' + queued['id'])
        record['review'] = review
        if review['status'] == 'completed':
            try:
                queued = request(url, token, '/admin/api/studio/suggestions', {'review_id': review['id'], 'request_key': uuid4().hex})
            except HTTPError as exc:
                detail = json.load(exc).get('detail', '')
                record.update(error_code=exc.code, detail=detail,
                              passed=False)
            else:
                suggestion = wait(url, token, '/admin/api/studio/suggestions/' + queued['id'])
                report = suggestion.get('report') or {}
                proposed = report.get('suggested_answer', '').lower()
                before = sum(term.lower() in case['guidance'].lower() for term in case['required_terms'])
                after = sum(term.lower() in proposed for term in case['required_terms'])
                changes = report.get('claim_changes') or []
                declared = bool(changes) and all(
                    change['before'] in case['guidance'] and change['after'] in report.get('suggested_answer','')
                    and bool(change.get('sources')) and all(source['id'].startswith('source:') for source in change['sources'])
                    for change in changes
                )
                record.update(suggestion=suggestion, before_supported_terms=before, after_supported_terms=after,
                              corrections_explained=declared,
                              required_terms=len(case['required_terms']),
                              passed=suggestion['status'] == 'completed' and after == len(case['required_terms'])
                              and bool(report.get('missing_details')) == case['must_ask']
                              and (not case.get('must_explain_correction') or declared)
                              and not any(term.lower() in proposed for term in case.get('forbidden_terms',[])))
        if previous:
            results.remove(previous)
        results.append(record)
        output.write_text(''.join(json.dumps(item, ensure_ascii=False) + '\n' for item in results))
        print(json.dumps({key: record.get(key) for key in ('id', 'passed', 'before_supported_terms', 'after_supported_terms', 'corrections_explained', 'error_code')}), flush=True)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True, help='Disposable dashboard URL; do not run synthetic cases on Oracle.')
    parser.add_argument('--token-env', default='STUDIO_TEST_TOKEN')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--resume', action='store_true', help='Explicit retry retaining failures; reuse completed parent reviews.')
    args = parser.parse_args()
    results = evaluate(args.url, os.environ[args.token_env], args.output, args.resume)
    print(json.dumps({'passed': sum(bool(item['passed']) for item in results), 'cases': len(results)}))
    raise SystemExit(any(not item['passed'] for item in results))


if __name__ == '__main__':
    main()
