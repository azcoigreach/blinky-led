from __future__ import annotations

from app.core.models import Severity
from app.providers.markets import build_market_provider
from app.widgets.base import Widget


class StocksWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = build_market_provider(self.config, source_label=self.source_label)

    async def fetch_primary(self):
        symbol = self.config.get("symbol", "SPY")
        market_type = str(self.config.get("market_type", "stock"))
        quote = await self.provider.fetch_quote(symbol, market_type=market_type)
        price = quote.price
        delta = quote.change_percent
        sev = Severity.warning if delta < -1 else Severity.ok
        trend = "down" if delta < 0 else "up" if delta > 0 else "flat"
        return self.normalized(
            "Stocks",
            f"{symbol} {price:.2f}",
            delta=f"{delta:+.2f}%",
            trend=trend,
            severity=sev,
            source_label=quote.meta.source_label,
            status_summary=f"{market_type} quote loaded",
            extra={
                "symbol": quote.symbol,
                "price": price,
                "delta_percent": delta,
                "market_type": quote.market_type,
                "provider_fetched_at": quote.meta.fetched_at.isoformat(),
            },
            debug=quote.meta.debug,
        )
