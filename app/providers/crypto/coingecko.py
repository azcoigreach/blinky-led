from __future__ import annotations

from app.core.market_data import CryptoQuoteNormalized, utc_now
from app.services.http import fetch_json


def default_symbol_aliases() -> dict[str, str]:
    return {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "DOGE": "dogecoin",
    }


class CoinGeckoCryptoProvider:
    def __init__(self, *, source: str = "coingecko", base_url: str = "https://api.coingecko.com/api/v3") -> None:
        self.source = source
        self.base_url = base_url.rstrip("/")

    async def fetch_quotes(self, symbols: list[str], *, alias_map: dict[str, str] | None = None) -> list[CryptoQuoteNormalized]:
        alias_map = {**default_symbol_aliases(), **(alias_map or {})}
        ids = [alias_map.get(symbol.upper(), symbol.lower()) for symbol in symbols]
        payload = await fetch_json(
            f"{self.base_url}/simple/price",
            params={
                "ids": ",".join(ids),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_last_updated_at": "true",
            },
        )

        quotes: list[CryptoQuoteNormalized] = []
        now = utc_now()
        for symbol in symbols:
            coin_id = alias_map.get(symbol.upper(), symbol.lower())
            quote = payload.get(coin_id)
            if quote is None:
                raise RuntimeError(f"coingecko did not return quote for {symbol} ({coin_id})")
            price = float(quote.get("usd", 0.0))
            change_24h = float(quote.get("usd_24h_change", 0.0))
            absolute_change = (price * change_24h / 100.0) if price else None
            quotes.append(
                CryptoQuoteNormalized(
                    symbol=symbol.upper(),
                    label=symbol.upper(),
                    price=price,
                    absolute_change=absolute_change,
                    percent_change_24h=change_24h,
                    timestamp=now,
                    source=self.source,
                    stale=False,
                )
            )
        return quotes
