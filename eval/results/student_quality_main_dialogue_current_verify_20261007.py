"""Recheck actual main-model conversation chains against current retrieval/prompts."""

import json
from dataclasses import asdict
from pathlib import Path
from unittest.mock import patch
from msfea_bot.generation import answer as pipeline
from msfea_bot.generation.conversation import ConversationMessage, bounded_history, retrieval_plan
from msfea_bot.retrieval.store import indexed_generation, retrieval_depth
from msfea_bot.config import settings
from msfea_bot.llm import GenerationResult

root = Path("eval/results")
assert "test-db" in settings.database_url and settings.database_url.endswith("/msfea_test")
old = {}
for name in [
    "student_quality_main_closing_dialogue_20261007.jsonl",
    "student_quality_main_final_verified_dialogue_20261007.jsonl",
]:
    for line in (root / name).read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        old[row["id"]] = {**row, "generation_reuse_from": name}
generation = indexed_generation()
rows = []
mismatches = []
for case in [
    json.loads(line)
    for line in Path("eval/student_quality_dialogue_set.jsonl").read_text().splitlines()
]:
    history: list[ConversationMessage] = []
    chain_verified = True
    for index, turn in enumerate(case["turns"], 1):
        assert indexed_generation() == generation
        case_id = str(case["id"]) + "." + str(index)
        prior = bounded_history(history)
        original = old[case_id]
        assert [asdict(m) for m in prior] == original["history"]
        assert (
            original["question"] == turn["question"]
            and original["expected_behavior"] == turn["expected_behavior"]
        )
        assert original["model"] == settings.llm_model and not original.get("provider_error")
        question = turn["question"]
        k = retrieval_depth(question, settings.top_k)
        chunks = pipeline.retrieve_context(question, k, case.get("department"), prior)
        prompts: list[str] = []

        class Recorder:
            def generate(self, prompt: str) -> GenerationResult:
                prompts.append(prompt)
                return GenerationResult(text=pipeline.REFUSAL_MARKER)

        with patch.object(pipeline, "retrieve_context", return_value=chunks):
            pipeline.generate_answer(
                question, k=k, department=case.get("department"), history=prior, provider=Recorder()
            )
        prompt = prompts[0] if prompts else None
        exact = prompt == original["prompt"]
        chain_verified = chain_verified and exact
        if not exact:
            mismatches.append(case_id)
        plan = retrieval_plan(question, prior)
        rows.append(
            {
                **original,
                "chunks": [asdict(c) for c in chunks],
                "prompt": prompt,
                "context": prompt.split("\nContext:\n", 1)[1].split("\n\nQuestion:", 1)[0]
                if prompt
                else "",
                "query": plan.query,
                "literal_query": plan.standalone_query,
                "index_generation": generation,
                "current_prompt_exact": exact,
                "current_conversation_chain_verified": chain_verified,
            }
        )
        history.extend(
            [
                ConversationMessage("user", question),
                ConversationMessage("assistant", original["answer"]["text"]),
            ]
        )
with (root / "student_quality_main_current_dialogue_20261007.jsonl").open(
    "x", encoding="utf-8"
) as stream:
    for row in rows:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
summary = {
    "turns": len(rows),
    "exact_prompts": sum(r["current_prompt_exact"] for r in rows),
    "verified_chain_turns": sum(r["current_conversation_chain_verified"] for r in rows),
    "mismatches": mismatches,
    "model": settings.llm_model,
    "fresh_provider_calls": 0,
    "note": "Actual prior replies; exact current prompt reuse, not independent repeats or semantic grading.",
}
(root / "student_quality_main_current_dialogue_manifest_20261007.json").write_text(
    json.dumps(summary, indent=2)
)
print(json.dumps(summary))
