"""Each test starts with empty process-local API guards, at production limits."""

import pytest

import msfea_bot.api.app as api
from msfea_bot.api.abuse import RequestGuard
from msfea_bot.api.security import RateLimiter


@pytest.fixture(autouse=True)
def fresh_api_guards(monkeypatch: pytest.MonkeyPatch) -> None:
    # Preserve limits: only remove traffic from earlier tests. A fast CI runner
    # otherwise carries its burst window into unrelated endpoint tests.
    for name, value in vars(api).items():
        if isinstance(value, RateLimiter):
            monkeypatch.setattr(api, name, RateLimiter(value.max_requests, value.window_seconds))
    monkeypatch.setattr(api, "_guard", RequestGuard())
