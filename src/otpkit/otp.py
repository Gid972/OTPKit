"""Core OTP implementation."""

from __future__ import annotations

import secrets
import time
from typing import Any, Callable

from .exceptions import (
    InvalidConfigurationError,
    OTPCooldownError,
)
from .models import OTPRecord
from .security import compare_values, hash_value
from .storage import MemoryStorage, Storage


class OTP:
    """A secure OTP generator and verifier with expiration, purpose, and user context."""

    def __init__(
        self,
        length: int = 6,
        expiration: int = 300,
        max_attempts: int = 5,
        single_use: bool = True,
        storage: Storage | None = None,
        resend_cooldown: int = 30,
        resend_limit: int = 3,
        sender: Callable[..., Any] | None = None,
    ) -> None:
        self.length = self._validate_length(length)
        self.expiration = self._validate_positive_int(expiration, "expiration")
        self.max_attempts = self._validate_positive_int(max_attempts, "max_attempts")
        self.single_use = bool(single_use)
        self.storage = storage or MemoryStorage()
        self.resend_cooldown = self._validate_non_negative_int(resend_cooldown, "resend_cooldown")
        self.resend_limit = self._validate_positive_int(resend_limit, "resend_limit")
        self.sender = sender
        self._last_resend: dict[tuple[str | None, str | None], float] = {}
        self._resend_counts: dict[tuple[str | None, str | None], int] = {}

    def generate(
        self,
        length: int | None = None,
        purpose: str | None = None,
        user_id: str | None = None,
        destination: str | None = None,
    ) -> str:
        effective_length = self.length if length is None else self._validate_length(length)
        code = self._generate_code(effective_length)
        record = OTPRecord(
            code_hash=hash_value(code),
            purpose=purpose,
            user_id=user_id,
            destination=destination,
            expires_at=time.time() + self.expiration,
            max_attempts=self.max_attempts,
        )
        self.storage.save(self._record_key(record), record.to_dict())
        return code

    def verify(
        self,
        code: str,
        purpose: str | None = None,
        user_id: str | None = None,
        destination: str | None = None,
    ) -> bool:
        for key, record_data in self.storage.items():
            record = OTPRecord(**record_data)
            if not self._matches_context(record, purpose, user_id, destination):
                continue
            if record.invalidated or record.is_expired():
                continue
            if record.attempts >= record.max_attempts:
                continue
            if not self._compare_code(code, record.code_hash):
                record.attempts += 1
                self.storage.update(key, record.to_dict())
                continue
            if record.used and self.single_use:
                return False
            record.attempts += 1
            if self.single_use:
                record.used = True
            self.storage.update(key, record.to_dict())
            return True
        return False

    def is_expired(
        self,
        code: str,
        purpose: str | None = None,
        user_id: str | None = None,
        destination: str | None = None,
    ) -> bool:
        for record_data in (value for _, value in self.storage.items()):
            record = OTPRecord(**record_data)
            if not self._matches_context(record, purpose, user_id, destination):
                continue
            if self._compare_code(code, record.code_hash):
                return record.is_expired()
        return False

    def remaining_time(
        self,
        code: str,
        purpose: str | None = None,
        user_id: str | None = None,
        destination: str | None = None,
    ) -> float:
        for record_data in (value for _, value in self.storage.items()):
            record = OTPRecord(**record_data)
            if not self._matches_context(record, purpose, user_id, destination):
                continue
            if self._compare_code(code, record.code_hash):
                return max(record.expires_at - time.time(), 0.0)
        return 0.0

    def invalidate(
        self,
        code: str,
        purpose: str | None = None,
        user_id: str | None = None,
        destination: str | None = None,
    ) -> None:
        for key, record_data in self.storage.items():
            record = OTPRecord(**record_data)
            if not self._matches_context(record, purpose, user_id, destination):
                continue
            if self._compare_code(code, record.code_hash):
                record.invalidated = True
                self.storage.update(key, record.to_dict())
                return

    def invalidate_all(
        self,
        purpose: str | None = None,
        user_id: str | None = None,
        destination: str | None = None,
    ) -> None:
        for key, record_data in self.storage.items():
            record = OTPRecord(**record_data)
            if self._matches_context(record, purpose, user_id, destination):
                record.invalidated = True
                self.storage.update(key, record.to_dict())

    def attempts_remaining(
        self,
        code: str,
        purpose: str | None = None,
        user_id: str | None = None,
        destination: str | None = None,
    ) -> int:
        for record_data in (value for _, value in self.storage.items()):
            record = OTPRecord(**record_data)
            if not self._matches_context(record, purpose, user_id, destination):
                continue
            if self._compare_code(code, record.code_hash):
                return max(record.max_attempts - record.attempts, 0)
        return 0

    def resend(
        self,
        purpose: str | None = None,
        user_id: str | None = None,
        destination: str | None = None,
    ) -> str:
        context = (user_id, purpose)
        now = time.time()
        if context in self._last_resend and now - self._last_resend[context] < self.resend_cooldown:
            raise OTPCooldownError("Resend cooldown is active. Please wait before requesting another OTP.")
        if context in self._resend_counts and self._resend_counts[context] >= self.resend_limit:
            raise OTPCooldownError("Resend limit reached.")

        for key, record_data in list(self.storage.items()):
            record = OTPRecord(**record_data)
            if self._matches_context(record, purpose, user_id, destination) and not record.invalidated:
                record.invalidated = True
                self.storage.update(key, record.to_dict())

        code = self.generate(purpose=purpose, user_id=user_id, destination=destination)
        self._last_resend[context] = now
        self._resend_counts[context] = self._resend_counts.get(context, 0) + 1
        return code

    def send(
        self,
        destination: str,
        channel: Any | None = None,
        purpose: str | None = None,
        user_id: str | None = None,
    ) -> str:
        if channel is None:
            if self.sender is None:
                from .channels.console import ConsoleChannel

                channel = ConsoleChannel()
            else:
                return self.sender(destination=destination, purpose=purpose, user_id=user_id)
        code = self.generate(purpose=purpose, user_id=user_id, destination=destination)
        channel.send(destination=destination, otp=code, purpose=purpose)
        return code

    def _generate_code(self, length: int) -> str:
        digits = "0123456789"
        return "".join(secrets.choice(digits) for _ in range(length))

    def _compare_code(self, candidate: str, stored_hash: str) -> bool:
        return compare_values(hash_value(candidate), stored_hash)

    def _matches_context(
        self,
        record: OTPRecord,
        purpose: str | None,
        user_id: str | None,
        destination: str | None,
    ) -> bool:
        return (
            (purpose is None or record.purpose == purpose)
            and (user_id is None or record.user_id == user_id)
            and (destination is None or record.destination == destination)
        )

    def _record_key(self, record: OTPRecord) -> str:
        return f"otp:{record.code_hash}:{record.purpose or 'any'}:{record.user_id or 'any'}:{record.destination or 'any'}"

    @staticmethod
    def _validate_length(length: int) -> int:
        if not isinstance(length, int) or length < 4 or length > 12:
            raise InvalidConfigurationError("OTP length must be an integer between 4 and 12.")
        return length

    @staticmethod
    def _validate_positive_int(value: int, name: str) -> int:
        if not isinstance(value, int) or value <= 0:
            raise InvalidConfigurationError(f"{name} must be a positive integer.")
        return value

    @staticmethod
    def _validate_non_negative_int(value: int, name: str) -> int:
        if not isinstance(value, int) or value < 0:
            raise InvalidConfigurationError(f"{name} must be a non-negative integer.")
        return value
