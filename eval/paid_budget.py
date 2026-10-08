"""Single-worker evaluation spending guard; not a billing-account balance reader."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from msfea_bot.config import settings
from msfea_bot.llm import GenerationResult, LLMProvider, get_llm_provider
from msfea_bot.llm.gemini import GeminiProvider


class EvaluationBudgetExceeded(RuntimeError):
    """No inference request was admitted beyond the evaluation's cost ceiling."""


class BudgetedGemini:
    """Reserve counted input plus maximum output before each SDK attempt.

    Failed attempts retain their worst-case reservation. Successful attempts
    settle using total-minus-input tokens, including reasoning. Ledger replay
    makes successive runs share one ceiling. Only one writer may use the ledger.
    """

    def __init__(self, provider: GeminiProvider, ledger: Path, limit: float,
                 input_price: float, output_price: float) -> None:
        if min(limit, input_price, output_price) <= 0:
            raise ValueError("Budget and per-million token prices must be positive")
        self.provider = provider
        self.ledger = ledger
        self.limit = limit
        self.input_price = input_price
        self.output_price = output_price
        self.spent = 0.0
        self.reservation = 0.0
        if ledger.exists():
            for line in ledger.read_text(encoding="utf-8").splitlines():
                event = json.loads(line)
                self.spent += float(event["usd_delta"])
        ledger.parent.mkdir(parents=True, exist_ok=True)
        if provider._before_request is not None:
            raise ValueError("Budget guard requires its own per-attempt admission hook")
        provider._before_request = self._reserve

    def _record(self, event: str, delta: float, **details: Any) -> None:
        self.spent += delta
        with self.ledger.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"event": event, "usd_delta": delta,
                "estimated_spent_upper_bound_usd": self.spent,
                "model": settings.llm_model, **details}) + "\n")

    def _reserve(self) -> None:
        if self.spent + self.reservation > self.limit:
            raise EvaluationBudgetExceeded("Evaluation cost ceiling reached before generation")
        self._record("reserve", self.reservation)

    def generate(self, prompt: str) -> GenerationResult:
        tokens = self.provider.count_input_tokens(prompt)
        self.reservation = (tokens * self.input_price
                            + settings.llm_max_output_tokens * self.output_price) / 1_000_000
        result = self.provider.generate(prompt)
        if result.input_tokens is not None and result.total_tokens is not None:
            output = max(result.output_tokens or 0, result.total_tokens - result.input_tokens)
            actual = (result.input_tokens * self.input_price + output * self.output_price) / 1_000_000
            self._record("settle", actual - self.reservation,
                         input_tokens=result.input_tokens, billed_output_tokens=output)
        # Missing usage retains the entire reservation instead of guessing cost.
        return result


def add_budget_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--budget-ledger", type=Path)
    parser.add_argument("--budget-usd", type=float)
    parser.add_argument("--input-usd-per-million", type=float)
    parser.add_argument("--output-usd-per-million", type=float)


def evaluation_provider(args: argparse.Namespace) -> LLMProvider:
    provider = get_llm_provider()
    if args.budget_ledger is None:
        return provider
    if not isinstance(provider, GeminiProvider):
        raise ValueError("Paid evaluation admission currently supports Gemini")
    if any(value is None for value in (args.budget_usd, args.input_usd_per_million,
                                       args.output_usd_per_million)):
        raise ValueError("Supply the evaluation ceiling and verified model prices")
    return BudgetedGemini(provider, args.budget_ledger, args.budget_usd,
                          args.input_usd_per_million, args.output_usd_per_million)


def student_profile() -> dict[str, Any]:
    """Record settings independently of prompt text for safe evaluation reuse."""
    sampling = settings.llm_gemini_use_sampling_params
    return {"max_output_tokens": settings.llm_max_output_tokens,
            "temperature": settings.llm_temperature if sampling else None,
            "seed": settings.llm_seed if sampling else None,
            "thinking_level": settings.llm_gemini_thinking_level}
