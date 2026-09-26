from otpkit import TOTP, generate_secret


def test_totp_generates_and_verifies_current_code():
    secret = generate_secret()
    totp = TOTP(secret)
    code = totp.generate()
    assert len(code) == 6
    assert totp.verify(code) is True


def test_totp_provisioning_uri_contains_otpauth():
    totp = TOTP("JBSWY3DPEHPK3PXP")
    uri = totp.provisioning_uri(account="user@example.com", issuer="MyApp")
    assert uri.startswith("otpauth://totp/")
    assert "MyApp" in uri
    assert "user%40example.com" in uri
