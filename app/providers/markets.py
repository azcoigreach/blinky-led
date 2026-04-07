from __future__ import annotations

from typing import Protocol

from app.providers.base import MarketQuote, ProviderResultMeta
from app.services.http import fetch_json


class MarketProvider(Protocol):
    async def fetch_quote(self, symbol: str, *, market_type: str) -> MarketQuote:
        ...


class FixtureMarketProvider:
    def __init__(self, *, price: float, change_percent: float, source_label: str = "fixture-market") -> None:
        self.price = price
        self.change_percent = change_percent
        self.source_label = source_label

    async def fetch_quote(self, symbol: str, *, market_type: str) -> MarketQuote:
        return MarketQuote(
            symbol=symbol,
            price=self.price,
            change_percent=self.change_percent,
            market_type=market_type,
            meta=ProviderResultMeta(source_label=self.source_label),
        )


class MarketDataProvider:
    """Adapter-ready HTTP provider. The endpoint shape is intentionally configurable."""

    def __init__(self, *, endpoint: str, source_label: str = "market-api") -> None:
        self.endpoint = endpoint
        self.source_label = source_label

    async def fetch_quote(self, symbol: str, *, market_type: str) -> MarketQuote:
        payload = await fetch_json(self.endpoint, params={"symbol": symbol, "market_type": market_type})
        return MarketQuote(
            symbol=symbol,
            price=float(payload.get("price", 0.0)),
            change_percent=float(payload.get("change_percent", 0.0)),
            market_type=str(payload.get("market_type", market_type)),
            meta=ProviderResultMeta(source_label=self.source_label, debug={"endpoint": self.endpoint}),
        )


def build_market_provider(config: dict, *, source_label: str) -> MarketProvider:
    provider_name = str(config.get("provider", "fixture")).lower()
    if provider_name == "marketdata":
        endpoint = str(config.get("endpoint", "")).strip()
        if not endpoint:
            raise RuntimeError("marketdata provider requires config.endpoint")
        return MarketDataProvider(endpoint=endpoint, source_label=source_label or "market-api")
    return FixtureMarketProvider(
        price=float(config.get("fixture_price", 500.0)),
        change_percent=float(config.get("fixture_delta", 0.0)),
        source_label=source_label or "fixture-market",
    )
