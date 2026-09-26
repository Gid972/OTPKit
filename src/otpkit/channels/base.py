"""Delivery channel abstraction for OTP messages."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Channel(ABC):
    """Abstract base class for delivery abstractions."""

    @abstractmethod
    def send(self, *, destination: str, otp: str, purpose: str | None = None) -> None:
        """Send an OTP to a destination."""
