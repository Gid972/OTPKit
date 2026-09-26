"""Core value models used by OTPKit."""

from __future__ import annotations

from dataclasses import dataclass, field
import time


@dataclass
class OTPRecord:
    """Represents a single generated OTP and its metadata."""

    code_hash: str
    purpose: str | None = None
    user_id: str | None = None
    destination: str | None = None
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 300)
    invalidated: bool = False
    used: bool = False
    attempts: int = 0
    max_attempts: int = 5
    signed: bool = False

    def is_expired(self, now: float | None = None) -> bool:
        if now is None:
            now = time.time()
        return now >= self.expires_at

    def to_dict(self) -> dict[str, object]:
        return {
            "code_hash": self.code_hash,
            "purpose": self.purpose,
            "user_id": self.user_id,
            "destination": self.destination,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "invalidated": self.invalidated,
            "used": self.used,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "signed": self.signed,
        }
