from __future__ import annotations

from app.core.models import Severity
from app.widgets.base import Widget


class StocksWidget(Widget):
    async def fetch_primary(self):
        symbol = self.config.get("symbol", "SPY")
        price = float(self.config.get("fixture_price", 500.0))
        delta = float(self.config.get("fixture_delta", 0.0))
        sev = Severity.warning if delta < -1 else Severity.ok
        trend = "down" if delta < 0 else "up" if delta > 0 else "flat"
        return self.normalized(
            "Stocks",
            f"{symbol} {price:.2f}",
            delta=f"{delta:+.2f}%",
            trend=trend,
            severity=sev,
            source_label="fixture",
            status_summary="stock fixture loaded",
            extra={"symbol": symbol, "price": price, "delta_percent": delta},
        )
