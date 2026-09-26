import pytest

from otpkit import (
    OTP,
    InvalidConfigurationError,
    OTPAttemptLimitError,
    OTPExpiredError,
    OTPError,
    OTPCooldownError,
)


def test_generate_default_length_and_basic_verify():
    otp = OTP()
    code = otp.generate()
    assert len(code) == 6
    assert code.isdigit()
    assert otp.verify(code) is True


def test_generate_custom_length_and_purpose_context():
    otp = OTP(length=8)
    code = otp.generate(purpose="login")
    assert len(code) == 8
    assert otp.verify(code, purpose="login") is True
    assert otp.verify(code, purpose="password_reset") is False


def test_reject_invalid_lengths():
    with pytest.raises(InvalidConfigurationError):
        OTP(length=3)

    with pytest.raises(InvalidConfigurationError):
        OTP(length=15)


def test_single_use_behavior():
    otp = OTP(single_use=True)
    code = otp.generate()
    assert otp.verify(code) is True
    assert otp.verify(code) is False


def test_expiration_and_remaining_time():
    otp = OTP(expiration=1)
    code = otp.generate()
    assert otp.is_expired(code) is False
    assert otp.remaining_time(code) > 0
    assert otp.verify(code) is True


def test_invalidations_and_purpose_scope():
    otp = OTP()
    code = otp.generate(purpose="login")
    otp.invalidate(code)
    assert otp.verify(code, purpose="login") is False

    code2 = otp.generate(purpose="login")
    otp.invalidate_all(purpose="login")
    assert otp.verify(code2, purpose="login") is False


def test_attempt_limits_and_remaining_attempts():
    otp = OTP(max_attempts=3)
    code = otp.generate()

    assert otp.verify("000000") is False
    assert otp.attempts_remaining(code) == 2

    assert otp.verify("000000") is False
    assert otp.verify("000000") is False
    assert otp.verify(code) is False


def test_user_context_and_destination_mismatch():
    otp = OTP()
    code = otp.generate(user_id="user_123", purpose="login")
    assert otp.verify(code, user_id="user_123", purpose="login") is True
    assert otp.verify(code, user_id="user_999", purpose="login") is False


def test_resend_and_cooldown():
    otp = OTP(resend_limit=2, resend_cooldown=60)
    first = otp.generate(purpose="login", user_id="u1")

    second = otp.resend(purpose="login", user_id="u1")
    assert second != first
    assert otp.verify(first, purpose="login", user_id="u1") is False

    with pytest.raises(OTPCooldownError):
        otp.resend(purpose="login", user_id="u1")


def test_invalid_configuration_raises_custom_exception():
    with pytest.raises(InvalidConfigurationError):
        OTP(length=0)

    with pytest.raises(InvalidConfigurationError):
        OTP(expiration=-1)

    with pytest.raises(InvalidConfigurationError):
        OTP(max_attempts=0)


def test_exception_types_are_exposed():
    assert issubclass(OTPError, Exception)
    assert issubclass(OTPExpiredError, OTPError)
    assert issubclass(OTPAttemptLimitError, OTPError)
    assert issubclass(OTPCooldownError, OTPError)
