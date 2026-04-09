from __future__ import annotations

from app.core.market_data import CryptoQuoteNormalized
from app.core.models import Severity
from app.providers.crypto import build_crypto_provider
from app.services.market_data import CryptoDataSource, MarketDataService
from app.widgets.base import Widget


class CryptoWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = build_crypto_provider(self.config, source_label=self.source_label)
        self.data_source = CryptoDataSource(provider=self.provider)
        self.service: MarketDataService[CryptoQuoteNormalized] = MarketDataService(
            refresh_seconds=int(self.config.get("refresh_seconds", self.refresh_seconds)),
            stale_after_seconds=int(self.config.get("stale_after_seconds", self.ttl_seconds)),
            retry_attempts=int(self.config.get("provider_retry_attempts", 2)),
            retry_backoff_seconds=float(self.config.get("provider_retry_backoff_seconds", 0.25)),
        )

    async def fetch_primary(self):
        symbols = [str(symbol).upper() for symbol in self.config.get("symbols", [self.config.get("symbol", "BTC")]) if symbol]
        if not symbols:
            return self.normalized(
                "Crypto",
                "disabled",
                severity=Severity.info,
                status_summary="crypto widget disabled by empty symbols",
                extra={"items": []},
                source_label=self.source_label,
            )

        alias_map = {str(k).upper(): str(v) for k, v in dict(self.config.get("aliases", {})).items()}
        batch = await self.service.get_or_refresh(
            fetcher=lambda: self.data_source.fetch(symbols, alias_map=alias_map),
            source=self.source_label,
        )
        items = [_format_item(quote) for quote in batch.items]
        lead = batch.items[0]
        change = lead.percent_change_24h
        severity = Severity.warning if min((quote.percent_change_24h for quote in batch.items), default=0.0) < -4 else Severity.ok
        trend = "down" if change < 0 else "up" if change > 0 else "flat"
        display_mode = str(self.config.get("display_mode", "full")).lower()

        return self.normalized(
            "Crypto",
            _render_value(items, display_mode=display_mode),
            delta=f"{change:+.2f}%",
            trend=trend,
            severity=severity,
            source_label=batch.source,
            status_summary=f"{len(batch.items)} crypto quote(s) loaded",
            extra={
                "layout": str(self.config.get("layout", "list")),
                "display_mode": display_mode,
                "items": items,
                "updated_at": batch.updated_at.isoformat(),
                "service_stale": self.service.is_stale(),
            },
            debug={"symbols": symbols, "provider_error": self.service.last_error},
        )


def _format_item(quote: CryptoQuoteNormalized) -> dict[str, object]:
    trend = "down" if quote.percent_change_24h < 0 else "up" if quote.percent_change_24h > 0 else "flat"
    return {
        "symbol": quote.symbol,
        "label": quote.label,
        "value": f"{quote.price:,.0f}",
        "delta": f"{quote.percent_change_24h:+.2f}%",
        "trend": trend,
        "stale": quote.stale,
        "asset_type": quote.asset_type,
        "source": quote.source,
    }


def _render_value(items: list[dict[str, object]], *, display_mode: str) -> str:
    if not items:
        return "n/a"
    if display_mode == "percent_only":
        return " ".join(f"{item['label']} {item['delta']}" for item in items[:2])
    return " | ".join(f"{item['label']} {item['value']} {item['delta']}" for item in items[:2])
