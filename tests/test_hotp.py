from otpkit import HOTP


def test_hotp_generate_and_verify():
    hotp = HOTP("JBSWY3DPEHPK3PXP", digits=8)
    code = hotp.generate(counter=7)
    assert len(code) == 8
    assert hotp.verify(code, counter=7) is True
    assert hotp.verify(code, counter=8) is False
