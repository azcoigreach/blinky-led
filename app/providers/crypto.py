from __future__ import annotations

from typing import Protocol

from app.providers.base import CryptoQuote, ProviderResultMeta
from app.services.http import fetch_json


class CryptoProvider(Protocol):
    async def fetch_quote(self, symbol: str) -> CryptoQuote:
        ...


class FixtureCryptoProvider:
    def __init__(self, *, price: float, change_percent: float, source_label: str = "fixture-crypto") -> None:
        self.price = price
        self.change_percent = change_percent
        self.source_label = source_label

    async def fetch_quote(self, symbol: str) -> CryptoQuote:
        return CryptoQuote(
            symbol=symbol,
            price=self.price,
            change_percent=self.change_percent,
            meta=ProviderResultMeta(source_label=self.source_label),
        )


class BinanceProvider:
    def __init__(self, *, base_url: str = "https://api.binance.us", source_label: str = "binance") -> None:
        self.base_url = base_url.rstrip("/")
        self.source_label = source_label

    async def fetch_quote(self, symbol: str) -> CryptoQuote:
        payload = await fetch_json(f"{self.base_url}/api/v3/ticker/24hr", params={"symbol": symbol})
        return CryptoQuote(
            symbol=symbol,
            price=float(payload.get("lastPrice", 0.0)),
            change_percent=float(payload.get("priceChangePercent", 0.0)),
            meta=ProviderResultMeta(source_label=self.source_label),
        )


class CoinGeckoProvider:
    def __init__(self, *, source_label: str = "coingecko") -> None:
        self.source_label = source_label

    async def fetch_quote(self, symbol: str) -> CryptoQuote:
        coin_id = symbol.lower().replace("usdt", "")
        payload = await fetch_json(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
        )
        if coin_id not in payload:
            raise RuntimeError(f"coingecko did not return quote for {coin_id}")
        quote = payload[coin_id]
        return CryptoQuote(
            symbol=symbol,
            price=float(quote.get("usd", 0.0)),
            change_percent=float(quote.get("usd_24h_change", 0.0)),
            meta=ProviderResultMeta(source_label=self.source_label, debug={"coin_id": coin_id}),
        )


def build_crypto_provider(config: dict, *, source_label: str) -> CryptoProvider:
    provider_name = str(config.get("provider", "binance")).lower()
    if provider_name == "coingecko":
        return CoinGeckoProvider(source_label=source_label or "coingecko")
    if provider_name == "fixture":
        return FixtureCryptoProvider(
            price=float(config.get("fixture_price", 68000.0)),
            change_percent=float(config.get("fixture_change_percent", 0.0)),
            source_label=source_label or "fixture-crypto",
        )
    return BinanceProvider(source_label=source_label or "binance")
