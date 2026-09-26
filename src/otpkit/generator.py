"""Secure secret generation for OTP algorithms."""

from __future__ import annotations

import base64
import secrets


def generate_secret(length: int = 32) -> str:
    """Generate a secure random secret suitable for TOTP/HOTP.

    The output is encoded as base32 for interoperability with authenticator apps.
    """
    if length <= 0:
        raise ValueError("Secret length must be positive.")
    raw = secrets.token_bytes(length)
    return base64.b32encode(raw).decode("ascii").rstrip("=")
