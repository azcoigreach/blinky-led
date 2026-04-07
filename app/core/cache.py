from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass(slots=True)
class CacheEntry(Generic[T]):
    value: T
    expires_at: datetime


class TTLCache(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[str, CacheEntry[T]] = {}

    def set(self, key: str, value: T, ttl_seconds: int) -> None:
        self._items[key] = CacheEntry(value=value, expires_at=datetime.now(UTC) + timedelta(seconds=ttl_seconds))

    def get(self, key: str) -> T | None:
        entry = self._items.get(key)
        if not entry:
            return None
        if entry.expires_at < datetime.now(UTC):
            self._items.pop(key, None)
            return None
        return entry.value

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def clear(self) -> None:
        self._items.clear()
