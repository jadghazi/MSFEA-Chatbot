"""Budget admission protects spending independently of student-answer policy."""

from pathlib import Path
from typing import Callable

import pytest

from eval.paid_budget import BudgetedGemini, EvaluationBudgetExceeded
from msfea_bot.config import settings
from msfea_bot.llm import GenerationResult, LLMServiceError
from msfea_bot.llm.gemini import GeminiProvider


class FakeGemini(GeminiProvider):
    def __init__(self, *, failed_first_attempt: bool = False, fail: bool = False) -> None:
        self._before_request: Callable[[], None] | None = None
        self.failed_first_attempt = failed_first_attempt
        self.fail = fail
        self.calls = 0

    def count_input_tokens(self, prompt: str) -> int:
        return 1000

    def generate(self, prompt: str) -> GenerationResult:
        assert self._before_request is not None
        for _ in range(2 if self.failed_first_attempt else 1):
            self._before_request()
            self.calls += 1
        if self.fail:
            raise LLMServiceError("Simulated failure")
        return GenerationResult(text="answer", input_tokens=1000,
                                output_tokens=100, total_tokens=1600)


def test_budget_counts_reasoning_and_replays_prior_spending(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "llm_max_output_tokens", 2000)
    ledger = tmp_path / "ledger.jsonl"
    budget = BudgetedGemini(FakeGemini(), ledger, 0.010, 1, 5)
    with pytest.raises(EvaluationBudgetExceeded):
        budget.generate("question")
    assert budget.provider.calls == 0
    assert not ledger.exists()
    budget.limit = 0.015
    budget.generate("question")
    assert budget.spent == pytest.approx(0.004)  # 600 billed output, not just 100 visible.
    replay = BudgetedGemini(FakeGemini(), ledger, 0.015, 1, 5)
    assert replay.spent == pytest.approx(0.004)
    replay.generate("next question")
    with pytest.raises(EvaluationBudgetExceeded):
        replay.generate("third question")
    assert replay.provider.calls == 1


def test_failed_attempt_and_retry_keep_conservative_reservations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "llm_max_output_tokens", 2000)
    budget = BudgetedGemini(FakeGemini(failed_first_attempt=True),
                           tmp_path / "retry.jsonl", 0.03, 1, 5)
    budget.generate("question")
    assert budget.spent == pytest.approx(0.015)  # Failed attempt 0.011 + success 0.004.
    failing = BudgetedGemini(FakeGemini(fail=True), tmp_path / "failed.jsonl", 0.03, 1, 5)
    with pytest.raises(LLMServiceError):
        failing.generate("question")
    assert failing.spent == pytest.approx(0.011)
