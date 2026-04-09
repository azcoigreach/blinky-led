from __future__ import annotations

from typing import Protocol

from app.core.market_data import MarketOverviewQuote


class MarketOverviewProvider(Protocol):
    async def fetch_overview(self, symbols: list[str], *, labels: dict[str, str] | None = None) -> list[MarketOverviewQuote]:
        ...
