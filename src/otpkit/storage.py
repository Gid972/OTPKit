"""Storage abstraction and in-memory storage backend."""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from threading import RLock
from typing import Any


class Storage(ABC):
    """Interface for OTP persistence backends."""

    @abstractmethod
    def save(self, key: str, value: Any) -> None:
        """Persist a value under the given key."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Return the stored value, or None if not found."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a value from the storage backend."""

    @abstractmethod
    def update(self, key: str, value: Any) -> None:
        """Update an existing item in the backend."""

    @abstractmethod
    def items(self) -> list[tuple[str, Any]]:
        """Return all stored items for iteration."""


class MemoryStorage(Storage):
    """Simple in-memory implementation for development and single-process use."""

    def __init__(self) -> None:
        self._values: dict[str, Any] = {}
        self._lock = RLock()

    def save(self, key: str, value: Any) -> None:
        with self._lock:
            self._values[key] = deepcopy(value)

    def get(self, key: str) -> Any:
        with self._lock:
            value = self._values.get(key)
            return deepcopy(value) if value is not None else None

    def delete(self, key: str) -> None:
        with self._lock:
            self._values.pop(key, None)

    def update(self, key: str, value: Any) -> None:
        with self._lock:
            self._values[key] = deepcopy(value)

    def items(self) -> list[tuple[str, Any]]:
        with self._lock:
            return [(key, deepcopy(value)) for key, value in self._values.items()]
