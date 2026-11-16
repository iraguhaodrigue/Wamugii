"""Small in-memory sliding-window rate limiting for public endpoints.

Per process: with several workers each keeps its own count, so the real limit
is roughly `limit x workers`. That is fine for what this protects against --
credential stuffing, sign-up floods, password-reset mail bombing and bots
using the domain search as a free bulk-lookup service. It is deliberately not
a distributed limiter; moving to one would mean Redis, which this deployment
does not run.

Every limiter registers itself on construction so `reset_all()` can clear the
whole set between tests, and `settings.RATE_LIMIT_ENABLED` can switch the
checks off entirely.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.core.config import settings

# One message for every limit, so a caller can never tell from the text which
# limit it tripped -- in particular, the per-email login limit must not read
# differently from the per-IP one.
TOO_MANY_ATTEMPTS = "Too many attempts, try again in a few minutes."

_registry: list["SlidingWindowLimiter"] = []
_registry_lock = threading.Lock()


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: float):
        self.limit, self.window = limit, window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()
        with _registry_lock:
            _registry.append(self)

    def _prune(self, key: str, now: float) -> deque:
        """Drop hits that have aged out. Caller holds the lock."""
        q = self._hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        return q

    def _forget_idle(self) -> None:
        """Keep the key table from growing without bound. Caller holds the lock."""
        if len(self._hits) > 10_000:
            for k in [k for k, v in self._hits.items() if not v][:5_000]:
                self._hits.pop(k, None)

    def allow(self, key: str) -> bool:
        """Record a hit and say whether it was within the limit."""
        if not settings.RATE_LIMIT_ENABLED:
            return True
        now = time.monotonic()
        with self._lock:
            q = self._prune(key, now)
            if len(q) >= self.limit:
                return False
            q.append(now)
            self._forget_idle()
            return True

    def exceeded(self, key: str) -> bool:
        """
        Whether the key is already over the limit, without recording a hit.

        Used with `record()` where only *some* outcomes should count -- the
        per-email login limit counts failures only, so that someone who keeps
        signing in correctly is never locked out.
        """
        if not settings.RATE_LIMIT_ENABLED:
            return False
        now = time.monotonic()
        with self._lock:
            return len(self._prune(key, now)) >= self.limit

    def record(self, key: str) -> None:
        """Count a hit against the key regardless of the limit."""
        if not settings.RATE_LIMIT_ENABLED:
            return
        now = time.monotonic()
        with self._lock:
            self._prune(key, now).append(now)
            self._forget_idle()

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def reset_all() -> None:
    """Clear every limiter in the process. The test suite calls this per test."""
    with _registry_lock:
        limiters = list(_registry)
    for limiter in limiters:
        limiter.reset()


def visitor_key(request: Request) -> str:
    """
    The visitor's address, for rate limiting.

    Behind nginx every request arrives from 127.0.0.1, so prefer the address
    nginx appends: the LAST entry of X-Forwarded-For. Earlier entries can be
    typed by the visitor, so trusting the first would let anyone pick their own
    rate-limit bucket and bypass the limit entirely. Then X-Real-IP, then the
    socket address.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip() or "unknown"
    return request.headers.get("x-real-ip") or (
        request.client.host if request.client else "unknown"
    )


def enforce(limiter: SlidingWindowLimiter, key: str, detail: str = TOO_MANY_ATTEMPTS) -> None:
    """Raise 429 if `key` is over `limiter`'s limit, otherwise record the hit."""
    if not limiter.allow(key):
        raise HTTPException(status_code=429, detail=detail)
