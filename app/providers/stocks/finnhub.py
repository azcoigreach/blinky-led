from __future__ import annotations

from datetime import UTC, datetime

from app.core.market_data import StockQuoteNormalized
from app.services.http import fetch_json


class FinnhubStockApiClient:
    def __init__(self, *, api_key: str, base_url: str = "https://finnhub.io/api/v1") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def quote(self, symbol: str) -> dict:
        return await fetch_json(f"{self.base_url}/quote", params={"symbol": symbol, "token": self.api_key})


class FinnhubStockProvider:
    def __init__(self, *, api_key: str, source: str = "finnhub", base_url: str = "https://finnhub.io/api/v1") -> None:
        if not api_key:
            raise RuntimeError("finnhub provider requires API key")
        self.source = source
        self.client = FinnhubStockApiClient(api_key=api_key, base_url=base_url)

    async def fetch_quote(self, symbol: str, *, label: str | None = None) -> StockQuoteNormalized:
        payload = await self.client.quote(symbol)
        price = float(payload.get("c", 0.0))
        previous_close = float(payload.get("pc", 0.0))
        absolute_change = float(payload.get("d", 0.0))
        percent_change = float(payload.get("dp", 0.0))
        ts = int(payload.get("t", 0) or 0)
        if ts <= 0:
            timestamp = datetime.now(UTC)
            stale = True
        else:
            timestamp = datetime.fromtimestamp(ts, tz=UTC)
            stale = False
        return StockQuoteNormalized(
            symbol=symbol,
            label=label or symbol,
            price=price,
            absolute_change=absolute_change,
            percent_change=percent_change,
            previous_close=previous_close,
            day_high=float(payload.get("h", 0.0)) or None,
            day_low=float(payload.get("l", 0.0)) or None,
            market_state=_market_state_from_timestamp(timestamp),
            timestamp=timestamp,
            source=self.source,
            stale=stale,
        )

    async def fetch_quotes(self, symbols: list[str], *, labels: dict[str, str] | None = None) -> list[StockQuoteNormalized]:
        labels = labels or {}
        results: list[StockQuoteNormalized] = []
        for symbol in symbols:
            results.append(await self.fetch_quote(symbol, label=labels.get(symbol)))
        return results


def _market_state_from_timestamp(timestamp: datetime) -> str:
    hour = timestamp.astimezone(UTC).hour
    if 13 <= hour < 20:
        return "regular"
    if 9 <= hour < 13:
        return "premarket"
    return "after_hours"
