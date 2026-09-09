"""Process-local, content-free counters; reset on restart (single-worker pilot)."""

from collections import Counter
from threading import Lock

_counts: Counter[str] = Counter()
_lock = Lock()


def count(name: str, amount: int = 1) -> None:
    with _lock:
        _counts[name] += amount


def snapshot() -> dict[str, int]:
    with _lock:
        return dict(_counts)
