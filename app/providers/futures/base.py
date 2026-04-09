from __future__ import annotations

from typing import Protocol

from app.core.market_data import FuturesQuoteNormalized


class FuturesQuoteProvider(Protocol):
    async def fetch_quote(self, contract: str, *, label: str | None = None) -> FuturesQuoteNormalized:
        ...

    async def fetch_quotes(
        self,
        contracts: list[str],
        *,
        labels: dict[str, str] | None = None,
        aliases: dict[str, str] | None = None,
    ) -> list[FuturesQuoteNormalized]:
        ...
