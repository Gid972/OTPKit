from otpkit import TOTP, generate_secret

secret = generate_secret()
totp = TOTP(secret)
code = totp.generate()
print(code)
print(totp.verify(code))
print(totp.provisioning_uri(account="user@example.com", issuer="MyApp"))
