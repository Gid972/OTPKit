"""OTPKit public package API."""

from .exceptions import (
    InvalidConfigurationError,
    InvalidOTPError,
    OTPAlreadyUsedError,
    OTPAttemptLimitError,
    OTPError,
    OTPExpiredError,
    OTPCooldownError,
)
from .generator import generate_secret
from .hotp import HOTP
from .otp import OTP
from .totp import TOTP

__version__ = "0.1.0"

__all__ = [
    "OTP",
    "TOTP",
    "HOTP",
    "generate_secret",
    "OTPError",
    "InvalidOTPError",
    "OTPExpiredError",
    "OTPAlreadyUsedError",
    "OTPAttemptLimitError",
    "OTPCooldownError",
    "InvalidConfigurationError",
    "__version__",
]
