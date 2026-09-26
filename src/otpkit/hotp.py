"""HMAC-based one-time passwords."""

from __future__ import annotations

import base64
import hashlib
import hmac
import struct


class HOTP:
    """RFC 4226-compatible HOTP implementation."""

    def __init__(self, secret: str, digits: int = 6, algorithm: str = "SHA1") -> None:
        if not secret:
            raise ValueError("Secret must not be empty.")
        if digits < 4 or digits > 10:
            raise ValueError("Digits must be between 4 and 10.")
        self.secret = secret
        self.digits = digits
        self.algorithm = algorithm.upper()

    def _decode_secret(self) -> bytes:
        padded = self.secret.upper() + "=" * ((8 - len(self.secret) % 8) % 8)
        return base64.b32decode(padded, casefold=True)

    def _digest(self, counter: int) -> bytes:
        msg = struct.pack("!Q", counter)
        return hmac.new(self._decode_secret(), msg, getattr(hashlib, self.algorithm.lower())).digest()

    def generate(self, counter: int) -> str:
        if counter < 0:
            raise ValueError("Counter must be non-negative.")
        digest = self._digest(counter)
        offset = digest[-1] & 0x0F
        binary = ((digest[offset] & 0x7F) << 24) | ((digest[offset + 1] & 0xFF) << 16) | ((digest[offset + 2] & 0xFF) << 8) | (digest[offset + 3] & 0xFF)
        value = binary % (10**self.digits)
        return f"{value:0{self.digits}d}"

    def verify(self, code: str, counter: int) -> bool:
        return hmac.compare_digest(code, self.generate(counter))
