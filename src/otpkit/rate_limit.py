"""Rate-limiting primitives for OTP verification."""

from __future__ import annotations

import time
from threading import RLock


class RateLimiter:
    """A lightweight in-memory rate limiter for OTP activity."""

    def __init__(self, max_attempts: int = 5) -> None:
        if max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        self.max_attempts = max_attempts
        self._lock = RLock()
        self._attempts: dict[str, int] = {}
        self._window_start: dict[str, float] = {}

    def record_attempt(self, key: str) -> int:
        now = time.time()
        with self._lock:
            if key not in self._attempts:
                self._attempts[key] = 0
                self._window_start[key] = now
            if now - self._window_start.get(key, now) > 60:
                self._attempts[key] = 0
                self._window_start[key] = now
            self._attempts[key] += 1
            return self._attempts[key]

    def attempts_remaining(self, key: str) -> int:
        with self._lock:
            attempts = self._attempts.get(key, 0)
            return max(self.max_attempts - attempts, 0)

    def should_block(self, key: str) -> bool:
        return self.attempts_remaining(key) <= 0

    def reset(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)
            self._window_start.pop(key, None)
