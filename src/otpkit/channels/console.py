"""A development-only console channel for local testing."""

from __future__ import annotations

from .base import Channel


class ConsoleChannel(Channel):
    """Print messages to the console. This is not production delivery."""

    def send(self, *, destination: str, otp: str, purpose: str | None = None) -> None:
        purpose_text = f" for {purpose}" if purpose else ""
        print(f"[otpkit][dev channel] Sending OTP{purpose_text} to {destination}: {otp}")
