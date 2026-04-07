from __future__ import annotations

from app.core.models import Severity
from app.providers.crypto import build_crypto_provider
from app.widgets.base import Widget


class CryptoWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = build_crypto_provider(self.config, source_label=self.source_label)

    async def fetch_primary(self):
        symbol = self.config.get("symbol", "BTCUSDT")
        quote = await self.provider.fetch_quote(symbol)
        price = quote.price
        change = quote.change_percent
        severity = Severity.warning if change < -5 else Severity.ok
        trend = "down" if change < 0 else "up" if change > 0 else "flat"
        return self.normalized(
            "Crypto",
            f"{symbol[:3]} {price:,.0f}",
            delta=f"{change:+.2f}%",
            trend=trend,
            severity=severity,
            source_label=quote.meta.source_label,
            status_summary="crypto ticker loaded",
            extra={
                "symbol": quote.symbol,
                "last_price": price,
                "change_percent": change,
                "provider_fetched_at": quote.meta.fetched_at.isoformat(),
            },
            debug=quote.meta.debug,
        )
