from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Generic, TypeVar

from app.core.market_data import CryptoQuoteNormalized, FuturesQuoteNormalized, MarketOverviewQuote, StockQuoteNormalized
from app.providers.crypto import CryptoQuoteProvider
from app.providers.futures import FuturesQuoteProvider
from app.providers.markets import MarketOverviewProvider
from app.providers.stocks.base import StockQuoteProvider

T = TypeVar("T")


@dataclass(slots=True)
class CachedBatch(Generic[T]):
    items: list[T]
    updated_at: datetime
    source: str


class MarketDataService(Generic[T]):
    def __init__(
        self,
        *,
        refresh_seconds: int,
        stale_after_seconds: int,
        retry_attempts: int = 2,
        retry_backoff_seconds: float = 0.25,
    ) -> None:
        self.refresh_seconds = max(1, refresh_seconds)
        self.stale_after_seconds = max(self.refresh_seconds, stale_after_seconds)
        self.retry_attempts = max(1, retry_attempts)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)

        self._cache: CachedBatch[T] | None = None
        self._last_refresh: datetime | None = None
        self.last_error: str | None = None

    async def get_or_refresh(self, *, fetcher, source: str) -> CachedBatch[T]:
        now = datetime.now(UTC)
        if self._cache and self._last_refresh and (now - self._last_refresh) < timedelta(seconds=self.refresh_seconds):
            return self._cache

        for attempt in range(self.retry_attempts):
            try:
                items = await fetcher()
                self._cache = CachedBatch(items=items, updated_at=datetime.now(UTC), source=source)
                self._last_refresh = datetime.now(UTC)
                self.last_error = None
                return self._cache
            except Exception as exc:  # noqa: BLE001
                self.last_error = str(exc)
                if attempt + 1 < self.retry_attempts:
                    await asyncio.sleep(self.retry_backoff_seconds * (2**attempt))

        if self._cache:
            stale_cache = CachedBatch(items=self._mark_stale(self._cache.items), updated_at=self._cache.updated_at, source=self._cache.source)
            self._cache = stale_cache
            return stale_cache
        raise RuntimeError(self.last_error or "market data fetch failed")

    def _mark_stale(self, items: list[T]) -> list[T]:
        stale_items: list[T] = []
        for item in items:
            setattr(item, "stale", True)
            stale_items.append(item)
        return stale_items

    def is_stale(self) -> bool:
        if not self._cache:
            return True
        age = datetime.now(UTC) - self._cache.updated_at
        return age > timedelta(seconds=self.stale_after_seconds)


class StocksDataSource:
    def __init__(self, *, primary: StockQuoteProvider, fallback: StockQuoteProvider | None = None) -> None:
        self.primary = primary
        self.fallback = fallback

    async def fetch(self, symbols: list[str], *, labels: dict[str, str] | None = None) -> list[StockQuoteNormalized]:
        labels = labels or {}
        try:
            return await self.primary.fetch_quotes(symbols, labels=labels)
        except Exception:
            if not self.fallback:
                raise
            return await self.fallback.fetch_quotes(symbols, labels=labels)


class MarketOverviewDataSource:
    def __init__(self, *, provider: MarketOverviewProvider) -> None:
        self.provider = provider

    async def fetch(self, symbols: list[str], *, labels: dict[str, str] | None = None) -> list[MarketOverviewQuote]:
        return await self.provider.fetch_overview(symbols, labels=labels)


class FuturesDataSource:
    def __init__(self, *, provider: FuturesQuoteProvider) -> None:
        self.provider = provider

    async def fetch(
        self,
        contracts: list[str],
        *,
        labels: dict[str, str] | None = None,
        aliases: dict[str, str] | None = None,
    ) -> list[FuturesQuoteNormalized]:
        return await self.provider.fetch_quotes(contracts, labels=labels, aliases=aliases)


class CryptoDataSource:
    def __init__(self, *, provider: CryptoQuoteProvider) -> None:
        self.provider = provider

    async def fetch(self, symbols: list[str], *, alias_map: dict[str, str] | None = None) -> list[CryptoQuoteNormalized]:
        return await self.provider.fetch_quotes(symbols, alias_map=alias_map)
