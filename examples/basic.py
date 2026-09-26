from otpkit import OTP

otp = OTP(length=6, expiration=300, max_attempts=5)
code = otp.generate(user_id="user_123", purpose="login")
print(code)
print(otp.verify(code, user_id="user_123", purpose="login"))
