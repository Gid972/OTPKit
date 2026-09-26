"""Security helpers for OTPKit."""

from __future__ import annotations

import hashlib
import hmac


def hash_value(value: str) -> str:
    """Return a SHA-256 digest for comparison or storage."""
    if not isinstance(value, str):
        value = str(value)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compare_values(left: str, right: str) -> bool:
    """Perform a constant-time comparison using hmac.compare_digest."""
    return hmac.compare_digest(left, right)
