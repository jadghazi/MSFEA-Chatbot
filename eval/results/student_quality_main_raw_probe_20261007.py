"""Retain raw provider replies for a bounded, identical-prompt diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path

from msfea_bot.config import settings
from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import ConversationMessage
from msfea_bot.llm import LLMError, LLMRateLimitError, get_llm_provider
from msfea_bot.retrieval.store import RetrievedChunk


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--ids", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    selected = set(args.ids.split(","))
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines()]
    provider = get_llm_provider()
    with args.output.open("x", encoding="utf-8") as stream:
        for row in rows:
            if row["id"] not in selected:
                continue
            if row["model"] != settings.llm_model or not row["prompt"]:
                raise ValueError("The diagnostic must replay the configured model's actual provider prompt")
            history = [ConversationMessage(**message) for message in row.get("history", [])]
            supplied = pipeline._answer_context(row["question"],
                [RetrievedChunk(**chunk) for chunk in row["chunks"]], history)
            if pipeline.build_prompt(row["question"], supplied, row.get("department"), history) != row["prompt"]:
                raise ValueError("The runtime changed; retain the old attempt without replaying it")
            record = {**row, "diagnostic_only": True,
                      "replay_input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest()}
            try:
                result = provider.generate(row["prompt"])
                record["raw_generation"] = asdict(result)
                record["parsed_replay_answer"] = asdict(pipeline.parse_answer(
                    result.text, supplied, row.get("department")))
            except LLMError as exc:
                record["provider_error"] = type(exc).__name__
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                stream.flush()
                if isinstance(exc, LLMRateLimitError):
                    return
                time.sleep(12)
                continue
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            print(row["id"], flush=True)
            time.sleep(12)


if __name__ == "__main__":
    main()
