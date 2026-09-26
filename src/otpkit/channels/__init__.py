"""Delivery channel abstractions for OTPKit."""

from .base import Channel
from .console import ConsoleChannel

__all__ = ["Channel", "ConsoleChannel"]
