from __future__ import annotations

from app.core.models import Severity
from app.services.http import fetch_json
from app.widgets.base import Widget


class CryptoWidget(Widget):
    async def fetch_primary(self):
        symbol = self.config.get("symbol", "BTCUSDT")
        payload = await fetch_json(f"https://api.binance.us/api/v3/ticker/24hr?symbol={symbol}")
        price = float(payload.get("lastPrice", 0.0))
        change = float(payload.get("priceChangePercent", 0.0))
        severity = Severity.warning if change < -5 else Severity.ok
        trend = "down" if change < 0 else "up" if change > 0 else "flat"
        return self.normalized(
            "Crypto",
            f"{symbol[:3]} {price:,.0f}",
            delta=f"{change:+.2f}%",
            trend=trend,
            severity=severity,
            source_label="binance",
            status_summary="crypto ticker loaded",
            extra={"symbol": symbol, "last_price": price, "change_percent": change},
        )
