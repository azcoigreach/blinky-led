from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from app.core.market_data import StockQuoteNormalized


class StockQuoteProvider(Protocol):
    async def fetch_quote(self, symbol: str, *, label: str | None = None) -> StockQuoteNormalized:
        ...

    async def fetch_quotes(self, symbols: list[str], *, labels: dict[str, str] | None = None) -> list[StockQuoteNormalized]:
        ...


class FixtureStockProvider:
    def __init__(self, *, price: float, percent_change: float, source: str = "fixture-stock") -> None:
        self.price = price
        self.percent_change = percent_change
        self.source = source

    async def fetch_quote(self, symbol: str, *, label: str | None = None) -> StockQuoteNormalized:
        previous_close = self.price / (1 + (self.percent_change / 100)) if self.percent_change else self.price
        absolute_change = self.price - previous_close
        return StockQuoteNormalized(
            symbol=symbol,
            label=label or symbol,
            price=self.price,
            absolute_change=absolute_change,
            percent_change=self.percent_change,
            previous_close=previous_close,
            day_high=None,
            day_low=None,
            market_state="regular",
            timestamp=datetime.now(UTC),
            source=self.source,
            stale=False,
        )

    async def fetch_quotes(self, symbols: list[str], *, labels: dict[str, str] | None = None) -> list[StockQuoteNormalized]:
        labels = labels or {}
        return [await self.fetch_quote(symbol, label=labels.get(symbol)) for symbol in symbols]
