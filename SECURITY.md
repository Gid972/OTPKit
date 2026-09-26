# Security

## What OTPKit protects against

- Guessability from predictable random generation by using Python's `secrets` module
- Timing leaks in OTP comparisons by using `hmac.compare_digest()`
- Unsafe plaintext storage through hashed OTP records in the default storage model
- Replay risk in the default single-use model

## What it does not protect against

- Compromise of the application's host or database
- Weak user verification outside the OTP flow
- Misuse of the in-memory backend in multi-process deployments
- Transport security problems if OTPs are sent over insecure channels

## Deployment guidance

- Use HTTPS for all OTP delivery and verification endpoints
- Never log OTP values or secrets
- Use persistent shared storage in production
- Apply rate limiting and account lockouts beyond the default in-memory scope
- Restrict who may trigger OTP issuance and verification

## Why HTTPS matters

Transport security prevents OTPs from being stolen in transit or replaced through man-in-the-middle attacks.

## Why OTPs should not be logged

OTP codes are short-lived secrets and may be replayed by an attacker if they are exposed in logs, traces, or debugging output.

## Production storage

The built-in `MemoryStorage` is intended for local development and single-process applications only. Production services should use persistent or shared storage such as Redis with a safe storage adapter.
