# OTPKit

OTPKit is a secure Python library for generating, validating, and managing one-time passwords. It supports numeric OTPs, expiration, single-use enforcement, brute-force protection, TOTP, HOTP, user context, and flexible storage. Built for developers who want a simple API, strong security defaults, and easy integration into login, verification, and authentication workflows.

## Why use OTPKit?

- Generate secure numeric OTPs with Python's `secrets` module
- Verify codes with purpose, user, and destination context
- Enforce expiration, single-use behavior, and failed-attempt limits
- Support TOTP and HOTP standards
- Keep your OTP handling provider-agnostic and clean
- Work with an in-memory storage backend by default for quick setup
- Use a CLI for simple local workflows

---

## Features

- Random OTP generation using cryptographically secure randomness
- OTP verification with purpose and user matching
- Expiration checks and remaining lifetime values
- Invalidating OTPs manually or by purpose
- Single-use OTP support
- Attempt limits to reduce brute-force risk
- Resend cooldowns and resend limits
- TOTP support for authenticator-style codes
- HOTP support using counters
- Secure storage abstraction with in-memory backend
- CLI helper commands
- Clear custom exceptions for invalid configuration and runtime errors

---

## Installation

Install the package with pip:

```bash
pip install otpkit
```

If you are working from a local checkout:

```bash
python -m pip install -e .
```

---

## Quick start

```python
from otpkit import OTP

otp = OTP(length=6, expiration=300, max_attempts=5)

code = otp.generate(user_id="user_123", purpose="login")
print(code)

is_valid = otp.verify(code, user_id="user_123", purpose="login")
print(is_valid)
```

This example creates a 6-digit OTP, associates it with a user and purpose, and verifies it with the same context.

---

## Basic usage examples

### 1. Simple OTP generation

This is the most basic OTP flow. It creates a secure 6-digit code using the default settings.

```python
from otpkit import OTP

otp = OTP()
code = otp.generate()
print(code)
```

### 2. Custom OTP length

You can choose the length when creating the `OTP` instance or when generating a code. The default is 6 digits, but you can make it longer if needed.

```python
from otpkit import OTP

otp = OTP(length=8)
code = otp.generate()
print(code)
```

### 3. Verify with purpose matching

OTP codes are tied to a purpose such as `login` or `password_reset`. This keeps one OTP from being reused across unrelated flows.

```python
from otpkit import OTP

otp = OTP()
code = otp.generate(purpose="login")

print(otp.verify(code, purpose="login"))      # True
print(otp.verify(code, purpose="password_reset"))  # False
```

### 4. Single-use OTPs

By default, OTPs are single-use. Once a valid OTP is checked, it cannot be reused again unless you configure `single_use=False`.

```python
from otpkit import OTP

otp = OTP(single_use=True)
code = otp.generate()

print(otp.verify(code))  # True
print(otp.verify(code))  # False
```

### 5. Expiration and remaining time

Every OTP has a lifetime. You can configure how long it remains valid, and then check how much time is left before the token expires.

```python
from otpkit import OTP

otp = OTP(expiration=60)
code = otp.generate()

print(otp.remaining_time(code))
print(otp.is_expired(code))
```

### 6. Manual invalidation

If you need to revoke a code before it expires, you can invalidate it manually.

```python
from otpkit import OTP

otp = OTP()
code = otp.generate(purpose="login")

otp.invalidate(code, purpose="login")
print(otp.verify(code, purpose="login"))
```

### 7. Invalidating all OTPs for a purpose

This is useful when you want to revoke every active code associated with a certain action, such as a login flow.

```python
from otpkit import OTP

otp = OTP()
code = otp.generate(purpose="login")

otp.invalidate_all(purpose="login")
print(otp.verify(code, purpose="login"))
```

### 8. Attempt limits

You can limit the number of failed verification attempts before an OTP becomes unusable. This helps guard against brute-force guessing.

```python
from otpkit import OTP

otp = OTP(max_attempts=3)
code = otp.generate()

for _ in range(3):
    otp.verify("000000")

print(otp.attempts_remaining(code))
```

---

## User and destination context

You can attach OTPs to a user ID or a destination such as an email address, phone number, username, or internal account ID.

```python
from otpkit import OTP

otp = OTP()
code = otp.generate(user_id="user_123", purpose="login")

print(otp.verify(code, user_id="user_123", purpose="login"))
print(otp.verify(code, user_id="user_456", purpose="login"))
```

This prevents one user from verifying another user's OTP.

---

## Expiration, invalidation, and resend handling

### Expiration

This shows how long a generated code stays valid. The timer is measured in seconds, and a code should stop verifying once the expiration window has been reached.

```python
from otpkit import OTP

otp = OTP(expiration=300)
code = otp.generate()

print(otp.remaining_time(code))
print(otp.is_expired(code))
```

### Resend support

Resending creates a new OTP while invalidating the older OTP for the same purpose/user context. This avoids multiple active codes for the same login attempt.

```python
from otpkit import OTP

otp = OTP(resend_cooldown=60, resend_limit=3)

first = otp.generate(purpose="login", user_id="user_123")
second = otp.resend(purpose="login", user_id="user_123")

print(first)
print(second)
```

Resending invalidates the previous active OTP for the same context and respects cooldown and limit rules.

---

## TOTP support

TOTP stands for Time-based One-Time Password. It follows the common RFC 6238 pattern used by authenticator apps.

```python
from otpkit import TOTP, generate_secret

secret = generate_secret()
totp = TOTP(secret)

code = totp.generate()
print(code)
print(totp.verify(code))
```

### TOTP provisioning URI

```python
from otpkit import TOTP

totp = TOTP("JBSWY3DPEHPK3PXP")
uri = totp.provisioning_uri(account="user@example.com", issuer="MyApp")
print(uri)
```

This generates an `otpauth://` URL suitable for apps such as authenticator clients.

---

## HOTP support

HOTP uses a counter-based algorithm and is useful when you want a password to be tied to a specific counter or event.

```python
from otpkit import HOTP

hotp = HOTP("JBSWY3DPEHPK3PXP", digits=8)

code = hotp.generate(counter=1)
print(code)
print(hotp.verify(code, counter=1))
```

---

## Secret generation

```python
from otpkit import generate_secret

secret = generate_secret()
print(secret)
```

This creates a secure secret using Python's `secrets` module.

---

## Storage backends

The library uses a storage abstraction so you can replace the default in-memory storage with your own backend later.

```python
from otpkit import OTP
from otpkit.storage import MemoryStorage

store = MemoryStorage()
otp = OTP(storage=store)

code = otp.generate(purpose="login")
print(code)
```

The default `MemoryStorage` is intended for development and single-process use. For production workloads, you should use a persistent or shared storage backend.

---

## Delivery channels

OTPKit does not hard-code SMS or email providers. You can send OTPs through a custom channel object or a callback function.

### Console channel example

The console channel is meant for local development and testing. It prints the OTP to the terminal so you can quickly test the flow without sending real messages.

```python
from otpkit import OTP
from otpkit.channels.console import ConsoleChannel

otp = OTP()
code = otp.send(destination="user@example.com", channel=ConsoleChannel(), purpose="login")
print(code)
```

### Custom sender callback

If you already have your own delivery mechanism, you can pass a custom sender function. This keeps OTPKit independent from specific email or SMS providers.

```python
from otpkit import OTP


def my_sender(*, destination, purpose=None, user_id=None):
    print(f"Sending OTP to {destination} for {purpose}")
    return "123456"

otp = OTP(sender=my_sender)
code = otp.send(destination="user@example.com", purpose="login")
print(code)
```

> This is intentionally decoupled from external email/SMS services so the core library stays provider-neutral.

---

## Command line interface

You can use the built-in CLI for quick work in terminals:

```bash
otpkit generate
otpkit generate --length 8
otpkit verify 482917
otpkit secret
otpkit version
```

Example:

```bash
$ otpkit generate
OTP: 482917
```

---

## Exception types

OTPKit includes clear custom exceptions so invalid configuration and verification errors are easier to handle:

```python
from otpkit import OTP, InvalidConfigurationError

try:
    OTP(length=3)
except InvalidConfigurationError:
    print("Bad OTP length")
```

Common exceptions include:

- `OTPError`
- `InvalidOTPError`
- `OTPExpiredError`
- `OTPAlreadyUsedError`
- `OTPAttemptLimitError`
- `OTPCooldownError`
- `InvalidConfigurationError`

---

## Security model

OTPKit is designed with security in mind:

- OTP values are generated with Python's `secrets` module
- OTP comparisons use `hmac.compare_digest()`
- codes are stored as hashes instead of raw plaintext values
- single-use and attempt-limit logic reduces reuse and brute-force risk
- code generation is provider-agnostic and does not invent custom crypto

### Important security notes

- Never log OTP values or secrets
- Never send real OTPs over insecure channels
- Use HTTPS in any web deployment
- Use persistent storage for multi-process production systems
- The default `MemoryStorage` is only for development and single-process use

---

## API summary

```python
from otpkit import OTP, TOTP, HOTP, generate_secret
```

### `OTP`

This is the main class for random numeric OTPs. It handles generation, verification, expiration, reuse prevention, purpose scoping, user association, invalidation, and resend logic.

### `TOTP`

This class is used for time-based OTPs and is compatible with common authenticator apps that follow the RFC 6238 standard.

### `HOTP`

This class is used for counter-based OTPs and follows the RFC 4226 standard.

### `generate_secret`

This helper generates a secure secret value for use in TOTP or HOTP implementations. It uses a cryptographically secure source instead of Python's random module.

---

## Development

To install dependencies for development:

```bash
python -m pip install -e .[dev]
```

To run the test suite:

```bash
pytest
```

---

## License

This project is licensed under the MIT License.

---

## Summary

OTPKit gives you a clean, secure, and beginner-friendly way to integrate one-time passwords into Python applications without forcing a specific provider or infrastructure model.

It is suitable for:

- login verification
- password reset flows
- email verification
- MFA setup
- transaction confirmation
- TOTP authenticator use cases
