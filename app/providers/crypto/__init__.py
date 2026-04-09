from __future__ import annotations

from datetime import UTC, datetime

from app.providers.base import CryptoQuote, ProviderResultMeta
from app.providers.crypto.base import CryptoQuoteProvider, FixtureCryptoProvider as FixtureCryptoBatchProvider
from app.providers.crypto.coingecko import CoinGeckoCryptoProvider, default_symbol_aliases


def build_crypto_provider(config: dict, *, source_label: str) -> CryptoQuoteProvider:
    provider_name = str(config.get("provider", "coingecko")).strip().lower()
    if provider_name == "fixture":
        return FixtureCryptoProvider(
            price=float(config.get("fixture_price", 68000.0)),
            change_percent=float(config.get("fixture_change_percent", 0.0)),
            source=source_label or "fixture-crypto",
        )
    return CoinGeckoProvider(source=source_label or "coingecko")


class CoinGeckoProvider(CoinGeckoCryptoProvider):
    async def fetch_quote(self, symbol: str) -> CryptoQuote:
        quote = (await self.fetch_quotes([symbol]))[0]
        return CryptoQuote(
            symbol=quote.symbol,
            price=quote.price,
            change_percent=quote.percent_change_24h,
            meta=ProviderResultMeta(source_label=quote.source, fetched_at=datetime.now(UTC)),
        )


class BinanceProvider:
    def __init__(self, *, source_label: str = "binance") -> None:
        self.source_label = source_label
        self._delegate = CoinGeckoProvider(source=source_label)

    async def fetch_quote(self, symbol: str) -> CryptoQuote:
        return await self._delegate.fetch_quote(symbol)


class FixtureCryptoProvider(FixtureCryptoBatchProvider):
    def __init__(self, *, price: float, change_percent: float, source: str = "fixture-crypto") -> None:
        super().__init__(price=price, percent_change_24h=change_percent, source=source)

    async def fetch_quote(self, symbol: str) -> CryptoQuote:
        quote = (await self.fetch_quotes([symbol]))[0]
        return CryptoQuote(
            symbol=quote.symbol,
            price=quote.price,
            change_percent=quote.percent_change_24h,
            meta=ProviderResultMeta(source_label=quote.source, fetched_at=datetime.now(UTC)),
        )


__all__ = [
    "BinanceProvider",
    "CoinGeckoProvider",
    "CoinGeckoCryptoProvider",
    "CryptoQuoteProvider",
    "FixtureCryptoProvider",
    "build_crypto_provider",
    "default_symbol_aliases",
]
