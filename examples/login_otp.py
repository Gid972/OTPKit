from otpkit import OTP
from otpkit.channels.console import ConsoleChannel

otp = OTP(length=6, expiration=300, max_attempts=5)

# User requests login
code = otp.send(destination="user@example.com", channel=ConsoleChannel(), purpose="login", user_id="user_123")
print(f"Generated code: {code}")

# User submits OTP
verified = otp.verify(code, user_id="user_123", purpose="login")
print(f"Verified: {verified}")
