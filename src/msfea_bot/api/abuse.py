"""Small, bounded single-worker protections, independent of retrieval and prompts."""

from __future__ import annotations

import hashlib
import re
import threading
import time
from collections import Counter, OrderedDict
from typing import Any

from fastapi import HTTPException
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from msfea_bot.observability.usage import count


def local_reply(question: str, has_history: bool = False) -> str | None:
    """Only classify whole messages; never reject words based on a dictionary."""
    words = re.findall(r"\w+", question.casefold())
    normalized = " ".join(words)
    if not normalized:
        return "Please type a short question about internships or CDC programs."
    # Yes/no can answer a clarification. Preserve that possibility with history.
    acknowledgements = r"(?:(?:ok|okay|thanks|thank you|thankyou|thx|got it|understood)\s*)+"
    if re.fullmatch(acknowledgements, normalized):
        return "You're welcome! Let me know if you have another question."
    if normalized in {"yes", "no", "yep", "nope"} and not has_history:
        return "What would you like to know about internships or CDC programs?"
    if normalized in {"hi", "hello", "hey"}:
        return "Hello! What would you like to know about internships or CDC programs?"
    compact = "".join(words)
    if len(compact) == 1 and not has_history:
        return "Please add a little more detail so I can understand your question."
    repeated = len(compact) >= 8 and len(set(compact)) <= 2
    mostly_repeated = (
        len(compact) >= 16 and Counter(compact).most_common(1)[0][1] / len(compact) >= 0.9
    )
    repeated_pattern = re.fullmatch(r"(.{1,8})\1{5,}", compact)
    repeated_words = len(words) >= 6 and len(set(words)) == 1
    # Only complete keyboard-row runs, not arbitrary unfamiliar words/acronyms.
    keyboard = re.fullmatch(r"(?:(?:qwerty(?:uiop)?|asdf(?:ghjkl)?|zxcv(?:bnm)?))+", compact)
    consonant_run = re.fullmatch(r"[bcdfghjklmnpqrstvwxz]{16,}", compact)
    if (
        repeated
        or mostly_repeated
        or repeated_pattern
        or repeated_words
        or keyboard
        or consonant_run
    ):
        return "I couldn't understand that. Please rephrase it as a short question."
    return None


def fingerprint(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()


def busy() -> HTTPException:
    count("concurrency_hits")
    return HTTPException(
        429, "Please wait for the current answer, then try again.", headers={"Retry-After": "3"}
    )


class RequestGuard:
    """Reject in-flight repeats; replay completed responses for 30 seconds.

    Cache only clients supplying a session ID, scoped to IP + session + complete
    request context. Never hold the lock over inference or wait in a worker thread.
    Anonymous legacy clients still get IP concurrency protection.
    """

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.active: dict[str, int] = {}
        self.sessions: set[str] = set()
        self.inflight: set[str] = set()
        self.cache: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self.version = 0

    def invalidate(self) -> None:
        """New namespace prevents even an older in-flight result being replayed."""
        with self.lock:
            self.version += 1
            self.cache.clear()

    def begin(self, ip: str, session: str | None, key: str) -> Any:
        now = time.monotonic()
        with self.lock:
            while self.cache and next(iter(self.cache.values()))[0] <= now:
                self.cache.popitem(last=False)
            if session and key in self.cache:
                count("duplicates_avoided")
                return self.cache[key][1]
            if key in self.inflight:
                count("duplicates_avoided")
                raise busy()
            if session and session in self.sessions:
                raise busy()
            if self.active.get(ip, 0) >= 4 or sum(self.active.values()) >= 16:
                raise busy()
            self.inflight.add(key)
            self.active[ip] = self.active.get(ip, 0) + 1
            if session:
                self.sessions.add(session)
        return None

    def finish(self, ip: str, session: str | None, key: str, response: Any = None) -> None:
        with self.lock:
            self.inflight.discard(key)
            self.active[ip] -= 1
            if not self.active[ip]:
                del self.active[ip]
            if session:
                self.sessions.discard(session)
                if response is not None:
                    self.cache[key] = (time.monotonic() + 30, response)
                    self.cache.move_to_end(key)
                    while len(self.cache) > 256:
                        self.cache.popitem(last=False)


class BodyLimitMiddleware:
    """Bound bytes before JSON parsing, including chunked/no-length requests."""

    def __init__(self, app: ASGIApp, max_bytes: int = 65_536) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            await self.app(scope, receive, send)
            return
        if scope["path"] == "/chat":
            count("chat_requests")
        headers = dict(scope.get("headers", []))
        try:
            declared_size = int(headers.get(b"content-length", b"0"))
        except ValueError:
            declared_size = 0  # Actual streamed bytes remain bounded below.
        if declared_size > self.max_bytes:
            count("body_size_hits")
            await JSONResponse(
                {"detail": "That request is too long. Please send a shorter question."},
                status_code=413,
            )(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.max_bytes:
                count("body_size_hits")
                await JSONResponse(
                    {"detail": "That request is too long. Please send a shorter question."},
                    status_code=413,
                )(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break

        delivered = False

        async def replay() -> Message:
            nonlocal delivered
            if delivered:
                return await receive()
            delivered = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        await self.app(scope, replay, send)
