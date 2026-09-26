"""Custom OTPKit exceptions."""


class OTPError(Exception):
    """Base exception for OTP-related errors."""


class InvalidOTPError(OTPError):
    """Raised when a supplied OTP value is invalid or mismatched."""


class OTPExpiredError(OTPError):
    """Raised when a verification is attempted after the OTP has expired."""


class OTPAlreadyUsedError(OTPError):
    """Raised when a single-use OTP is re-used."""


class OTPAttemptLimitError(OTPError):
    """Raised when an OTP has reached the configured failure limit."""


class OTPCooldownError(OTPError):
    """Raised when resend or verification is attempted too quickly."""


class InvalidConfigurationError(OTPError):
    """Raised when configuration or runtime parameters are invalid."""
