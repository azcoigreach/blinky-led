from __future__ import annotations

from typing import Protocol

from app.core.market_data import CryptoQuoteNormalized


class CryptoQuoteProvider(Protocol):
    async def fetch_quotes(self, symbols: list[str], *, alias_map: dict[str, str] | None = None) -> list[CryptoQuoteNormalized]:
        ...


class FixtureCryptoProvider:
    def __init__(self, *, price: float, percent_change_24h: float, source: str = "fixture-crypto") -> None:
        self.price = price
        self.percent_change_24h = percent_change_24h
        self.source = source

    async def fetch_quotes(self, symbols: list[str], *, alias_map: dict[str, str] | None = None) -> list[CryptoQuoteNormalized]:
        from app.core.market_data import utc_now

        now = utc_now()
        return [
            CryptoQuoteNormalized(
                symbol=symbol,
                label=symbol,
                price=self.price,
                absolute_change=None,
                percent_change_24h=self.percent_change_24h,
                timestamp=now,
                source=self.source,
                stale=False,
            )
            for symbol in symbols
        ]
