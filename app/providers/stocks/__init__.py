from __future__ import annotations

import os

from app.providers.stocks.alphavantage import AlphaVantageStockProvider
from app.providers.stocks.base import FixtureStockProvider, StockQuoteProvider
from app.providers.stocks.finnhub import FinnhubStockProvider


def build_stock_provider(provider_name: str, *, source_label: str, config: dict) -> StockQuoteProvider:
    normalized = provider_name.strip().lower()
    if normalized == "finnhub":
        api_key = str(config.get("api_key") or os.getenv("FINNHUB_API_KEY") or "").strip()
        return FinnhubStockProvider(api_key=api_key, source=source_label or "finnhub")
    if normalized == "alphavantage":
        api_key = str(config.get("api_key") or os.getenv("ALPHAVANTAGE_API_KEY") or "").strip()
        return AlphaVantageStockProvider(api_key=api_key, source=source_label or "alphavantage")
    return FixtureStockProvider(
        price=float(config.get("fixture_price", 500.0)),
        percent_change=float(config.get("fixture_percent_change", config.get("fixture_delta", 0.0))),
        source=source_label or "fixture-stock",
    )


def build_stock_provider_pair(config: dict, *, source_label: str) -> tuple[StockQuoteProvider, StockQuoteProvider | None]:
    primary_name = str(config.get("primary", config.get("provider", "fixture")))
    fallback_name = str(config.get("fallback", "")).strip()
    primary = build_stock_provider(primary_name, source_label=source_label, config=config)
    fallback = build_stock_provider(fallback_name, source_label=source_label, config=config) if fallback_name else None
    return primary, fallback


__all__ = [
    "AlphaVantageStockProvider",
    "FinnhubStockProvider",
    "FixtureStockProvider",
    "StockQuoteProvider",
    "build_stock_provider",
    "build_stock_provider_pair",
]
