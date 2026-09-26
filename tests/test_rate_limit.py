from otpkit.rate_limit import RateLimiter


def test_rate_limiter_tracks_attempts_and_reset():
    limiter = RateLimiter(max_attempts=3)
    assert limiter.attempts_remaining("alice") == 3
    assert limiter.record_attempt("alice") == 1
    assert limiter.record_attempt("alice") == 2
    assert limiter.attempts_remaining("alice") == 1
    limiter.reset("alice")
    assert limiter.attempts_remaining("alice") == 3
