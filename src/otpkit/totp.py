"""Time-based one-time passwords."""

from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import time
from urllib.parse import quote


class TOTP:
    """RFC 6238-compatible TOTP implementation."""

    def __init__(self, secret: str, digits: int = 6, interval: int = 30, algorithm: str = "SHA1") -> None:
        if not secret:
            raise ValueError("Secret must not be empty.")
        if digits < 4 or digits > 10:
            raise ValueError("Digits must be between 4 and 10.")
        if interval <= 0:
            raise ValueError("Interval must be positive.")
        self.secret = secret
        self.digits = digits
        self.interval = interval
        self.algorithm = algorithm.upper()

    def _decode_secret(self) -> bytes:
        padded = self.secret.upper() + "=" * ((8 - len(self.secret) % 8) % 8)
        return base64.b32decode(padded, casefold=True)

    def _digest(self, counter: int) -> bytes:
        msg = struct.pack("!Q", counter)
        digest = hmac.new(self._decode_secret(), msg, getattr(hashlib, self.algorithm.lower())).digest()
        return digest

    def _truncate(self, digest: bytes) -> int:
        offset = digest[-1] & 0x0F
        binary = ((digest[offset] & 0x7F) << 24) | ((digest[offset + 1] & 0xFF) << 16) | ((digest[offset + 2] & 0xFF) << 8) | (digest[offset + 3] & 0xFF)
        return binary % (10**self.digits)

    def generate(self, timestamp: float | None = None) -> str:
        if timestamp is None:
            timestamp = time.time()
        counter = int(timestamp // self.interval)
        value = self._truncate(self._digest(counter))
        return f"{value:0{self.digits}d}"

    def verify(self, code: str, timestamp: float | None = None, window: int = 1) -> bool:
        if timestamp is None:
            timestamp = time.time()
        current = int(timestamp // self.interval)
        for offset in range(-window, window + 1):
            candidate = self.generate(timestamp=(current + offset) * self.interval)
            if hmac.compare_digest(code, candidate):
                return True
        return False

    def provisioning_uri(self, account: str, issuer: str) -> str:
        label = quote(issuer) + ":" + quote(account)
        params = {
            "secret": self.secret,
            "issuer": issuer,
            "algorithm": self.algorithm,
            "digits": str(self.digits),
            "period": str(self.interval),
        }
        query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        return f"otpauth://totp/{label}?{query}"
