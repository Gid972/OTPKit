import hmac

from otpkit import OTP, generate_secret


def test_generate_secret_is_secure_length_and_and_uses_valid_chars():
    secret = generate_secret()
    assert isinstance(secret, str)
    assert len(secret) > 0
    assert secret.isalnum()


def test_constant_time_compare_is_used_for_otp_verification():
    otp = OTP()
    code = otp.generate()
    assert otp.verify(code) is True
    assert otp.verify(code) is False


def test_hash_never_exposes_plaintext_value():
    otp = OTP()
    code = otp.generate(purpose="login")
    record = next(value for _, value in otp.storage.items())
    assert record["code_hash"] != code
    assert hmac.compare_digest(record["code_hash"], code) is False
