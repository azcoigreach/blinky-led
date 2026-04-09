from __future__ import annotations

from collections.abc import Awaitable, Callable

from app.core.market_data import MarketOverviewQuote
from app.core.market_data import StockQuoteNormalized
from app.providers.stocks.base import StockQuoteProvider


class ProxyEtfMarketProvider:
    def __init__(
        self,
        *,
        stock_provider: StockQuoteProvider,
        source: str = "proxy-etf",
        quote_fetcher: Callable[[list[str], dict[str, str] | None], Awaitable[list[StockQuoteNormalized]]] | None = None,
    ) -> None:
        self.stock_provider = stock_provider
        self.source = source
        self.quote_fetcher = quote_fetcher

    async def fetch_overview(self, symbols: list[str], *, labels: dict[str, str] | None = None) -> list[MarketOverviewQuote]:
        if self.quote_fetcher is not None:
            stock_quotes = await self.quote_fetcher(symbols, labels)
        else:
            stock_quotes = await self.stock_provider.fetch_quotes(symbols, labels=labels)
        return [
            MarketOverviewQuote(
                symbol=quote.symbol,
                label=quote.label,
                price=quote.price,
                absolute_change=quote.absolute_change,
                percent_change=quote.percent_change,
                market_state=quote.market_state,
                timestamp=quote.timestamp,
                source=self.source,
                stale=quote.stale,
            )
            for quote in stock_quotes
        ]
