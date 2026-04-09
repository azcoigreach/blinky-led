from __future__ import annotations

from datetime import UTC, datetime

from app.core.market_data import StockQuoteNormalized
from app.services.http import fetch_json


class AlphaVantageApiClient:
    def __init__(self, *, api_key: str, base_url: str = "https://www.alphavantage.co/query") -> None:
        self.api_key = api_key
        self.base_url = base_url

    async def global_quote(self, symbol: str) -> dict:
        payload = await fetch_json(
            self.base_url,
            params={"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": self.api_key},
        )
        return payload.get("Global Quote", {})


class AlphaVantageStockProvider:
    def __init__(self, *, api_key: str, source: str = "alphavantage", base_url: str = "https://www.alphavantage.co/query") -> None:
        if not api_key:
            raise RuntimeError("alphavantage provider requires API key")
        self.source = source
        self.client = AlphaVantageApiClient(api_key=api_key, base_url=base_url)

    async def fetch_quote(self, symbol: str, *, label: str | None = None) -> StockQuoteNormalized:
        payload = await self.client.global_quote(symbol)
        if not payload:
            raise RuntimeError(f"alphavantage quote missing for {symbol}")

        price = float(payload.get("05. price", 0.0))
        absolute_change = float(payload.get("09. change", 0.0))
        percent_raw = str(payload.get("10. change percent", "0")).strip().replace("%", "")
        percent_change = float(percent_raw or 0.0)
        previous_close = float(payload.get("08. previous close", 0.0))

        ts = payload.get("07. latest trading day")
        if ts:
            timestamp = datetime.fromisoformat(str(ts)).replace(tzinfo=UTC)
            stale = False
        else:
            timestamp = datetime.now(UTC)
            stale = True

        return StockQuoteNormalized(
            symbol=symbol,
            label=label or symbol,
            price=price,
            absolute_change=absolute_change,
            percent_change=percent_change,
            previous_close=previous_close,
            day_high=float(payload.get("03. high", 0.0)) or None,
            day_low=float(payload.get("04. low", 0.0)) or None,
            market_state="regular",
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
