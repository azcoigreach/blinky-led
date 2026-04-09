from __future__ import annotations

from app.core.market_data import MarketOverviewQuote
from app.core.models import Severity
from app.providers.markets import ProxyEtfMarketProvider
from app.providers.stocks import build_stock_provider_pair
from app.services.market_data import MarketDataService, MarketOverviewDataSource, StocksDataSource
from app.widgets.base import Widget


DEFAULT_MARKET_SYMBOLS = ["DIA", "QQQ", "SPY", "IWM"]


class MarketsWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        provider_cfg = self.config.get("stocks_provider", self.config)
        primary, fallback = build_stock_provider_pair(provider_cfg, source_label=self.source_label)
        stock_source = StocksDataSource(primary=primary, fallback=fallback)
        self.provider = ProxyEtfMarketProvider(
            stock_provider=primary,
            source=self.source_label,
            quote_fetcher=lambda symbols, labels: stock_source.fetch(symbols, labels=labels),
        )
        self.data_source = MarketOverviewDataSource(provider=self.provider)
        self.service: MarketDataService[MarketOverviewQuote] = MarketDataService(
            refresh_seconds=int(self.config.get("refresh_seconds", self.refresh_seconds)),
            stale_after_seconds=int(self.config.get("stale_after_seconds", self.ttl_seconds)),
            retry_attempts=int(self.config.get("provider_retry_attempts", 2)),
            retry_backoff_seconds=float(self.config.get("provider_retry_backoff_seconds", 0.25)),
        )

    async def fetch_primary(self):
        symbols = [str(symbol).upper() for symbol in self.config.get("symbols", DEFAULT_MARKET_SYMBOLS) if symbol]
        labels = {str(k).upper(): str(v) for k, v in dict(self.config.get("labels", {})).items()}
        batch = await self.service.get_or_refresh(
            fetcher=lambda: self.data_source.fetch(symbols, labels=labels),
            source=self.source_label,
        )
        items = [_format_item(quote) for quote in batch.items]
        lead = batch.items[0]
        worst = min((quote.percent_change for quote in batch.items), default=0.0)
        severity = Severity.warning if worst < -1.0 else Severity.ok

        return self.normalized(
            "Markets",
            _render_value(items),
            delta=f"{lead.percent_change:+.2f}%",
            trend="down" if lead.percent_change < 0 else "up" if lead.percent_change > 0 else "flat",
            severity=severity,
            source_label=batch.source,
            status_summary=f"{len(batch.items)} market proxy quote(s) loaded",
            extra={
                "layout": str(self.config.get("layout", "compact")),
                "items": items,
                "updated_at": batch.updated_at.isoformat(),
                "service_stale": self.service.is_stale(),
            },
            debug={"symbols": symbols, "provider_error": self.service.last_error, "asset_type": "market_proxy"},
        )


def _format_item(quote: MarketOverviewQuote) -> dict[str, object]:
    trend = "down" if quote.percent_change < 0 else "up" if quote.percent_change > 0 else "flat"
    return {
        "symbol": quote.symbol,
        "label": quote.label,
        "value": f"{quote.price:.2f}",
        "delta": f"{quote.percent_change:+.2f}%",
        "trend": trend,
        "stale": quote.stale,
        "asset_type": quote.asset_type,
    }


def _render_value(items: list[dict[str, object]]) -> str:
    if not items:
        return "n/a"
    return " | ".join(f"{item['label']} {item['delta']}" for item in items[:3])
