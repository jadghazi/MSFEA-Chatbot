"""Tests for input sanitization and the rate limiter (CLAUDE.md §5.8)."""

import time

from msfea_bot.api.security import RateLimiter, sanitize


def test_sanitize_strips_control_chars_but_keeps_text() -> None:
    assert sanitize("hello\x00\x07 world") == "hello world"
    assert sanitize("  padded  ") == "padded"
    assert sanitize("line1\nline2\tend") == "line1\nline2\tend"


def test_sanitize_empty_after_cleanup() -> None:
    assert sanitize("\x00\x01\x02") == ""


def test_rate_limiter_blocks_over_limit() -> None:
    limiter = RateLimiter(max_requests=3, window_seconds=60)
    assert [limiter.allow("ip1") for _ in range(4)] == [True, True, True, False]


def test_rate_limiter_is_per_key() -> None:
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    assert limiter.allow("a") is True
    assert limiter.allow("a") is False
    assert limiter.allow("b") is True  # different client, own budget


def test_rate_limiter_window_expiry() -> None:
    limiter = RateLimiter(max_requests=1, window_seconds=0.05)
    assert limiter.allow("a") is True
    assert limiter.allow("a") is False  # blocked within the window
    time.sleep(0.06)
    assert limiter.allow("a") is True  # window elapsed, allowed again


def test_rate_limiter_evicts_stale_keys() -> None:
    # Keys from clients that go quiet must not accumulate forever (memory bound).
    limiter = RateLimiter(max_requests=5, window_seconds=0.05)
    for i in range(50):
        limiter.allow(f"ip-{i}")
    assert len(limiter._hits) == 50
    time.sleep(0.06)  # let every key's window expire
    limiter.allow("fresh")  # triggers a sweep of the now-stale keys
    assert "fresh" in limiter._hits
    assert len(limiter._hits) == 1  # the 50 stale keys were evicted
