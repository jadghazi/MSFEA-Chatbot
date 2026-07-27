"""Request-safety helpers (CLAUDE.md §5.8): input sanitization + rate limiting."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

_ALLOWED_CONTROL = {"\n", "\t"}


def sanitize(text: str) -> str:
    """Strip null bytes and control characters (keeping newlines/tabs), then trim.

    Length is capped separately by the request model. This does not attempt to
    defend against prompt injection — that is handled in the grounded system
    prompt (the model is told to ignore instructions inside the question).
    """
    text = text.replace("\x00", "")
    cleaned = "".join(ch for ch in text if ch >= " " or ch in _ALLOWED_CONTROL)
    return cleaned.strip()


class RateLimiter:
    """In-memory sliding-window rate limiter, keyed by client.

    Thread-safe (sync FastAPI endpoints run in a threadpool). NOTE: in-memory, so
    it is per-process — fine for a single instance / pilot. A multi-instance
    deployment needs a shared store (e.g. Redis). Documented in ADR-0008.
    """

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        self._last_sweep = time.monotonic()

    def _sweep(self, cutoff: float) -> None:
        """Drop keys whose most recent hit has expired, so the map can't grow
        unbounded under a flood of distinct client IPs (public-endpoint hardening).
        Caller must hold the lock."""
        stale = [key for key, hits in self._hits.items() if not hits or hits[-1] < cutoff]
        for key in stale:
            del self._hits[key]

    def allow(self, key: str) -> bool:
        """Record a request for `key`; return False if it exceeds the limit."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            if now - self._last_sweep > self.window_seconds:
                self._sweep(cutoff)
                self._last_sweep = now
            hits = self._hits[key]
            while hits and hits[0] < cutoff:
                hits.popleft()
            if len(hits) >= self.max_requests:
                return False
            hits.append(now)
            return True
