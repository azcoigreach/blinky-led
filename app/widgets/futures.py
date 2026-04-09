from __future__ import annotations

from app.core.market_data import FuturesQuoteNormalized
from app.core.models import Severity
from app.providers.futures import YahooFuturesProvider, default_contract_aliases
from app.services.market_data import FuturesDataSource, MarketDataService
from app.widgets.base import Widget


class FuturesWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_enabled = bool(self.config.get("enabled", True))
        provider_name = str(self.config.get("provider", "yahoo")).strip().lower()
        if provider_name != "yahoo":
            raise RuntimeError(f"unsupported futures provider: {provider_name}")
        aliases = {**default_contract_aliases(), **dict(self.config.get("aliases", {}))}
        self.provider = YahooFuturesProvider(source=self.source_label, aliases=aliases)
        self.data_source = FuturesDataSource(provider=self.provider)
        self.service: MarketDataService[FuturesQuoteNormalized] = MarketDataService(
            refresh_seconds=int(self.config.get("refresh_seconds", self.refresh_seconds)),
            stale_after_seconds=int(self.config.get("stale_after_seconds", self.ttl_seconds)),
            retry_attempts=int(self.config.get("provider_retry_attempts", 2)),
            retry_backoff_seconds=float(self.config.get("provider_retry_backoff_seconds", 0.25)),
        )

    async def fetch_primary(self):
        if not self.provider_enabled:
            return self.normalized(
                "Futures",
                "disabled",
                severity=Severity.info,
                status_summary="futures provider disabled",
                extra={"items": []},
                source_label=self.source_label,
            )

        contracts = [str(contract).upper() for contract in self.config.get("symbols", ["ES", "NQ", "YM", "CL", "GC"]) if contract]
        labels = {str(k).upper(): str(v) for k, v in dict(self.config.get("labels", {})).items()}
        aliases = {str(k).upper(): str(v) for k, v in dict(self.config.get("aliases", {})).items()}
        batch = await self.service.get_or_refresh(
            fetcher=lambda: self.data_source.fetch(contracts, labels=labels, aliases=aliases),
            source=self.source_label,
        )

        items = [_format_item(quote) for quote in batch.items]
        lead = batch.items[0]
        worst = min((quote.percent_change for quote in batch.items), default=0.0)
        severity = Severity.warning if worst < -1.0 else Severity.ok
        return self.normalized(
            "Futures",
            _render_value(items, display_mode=str(self.config.get("display_mode", "percent_only"))),
            delta=f"{lead.percent_change:+.2f}%",
            trend="down" if lead.percent_change < 0 else "up" if lead.percent_change > 0 else "flat",
            severity=severity,
            source_label=batch.source,
            status_summary=f"{len(batch.items)} futures quote(s) loaded",
            extra={
                "layout": str(self.config.get("layout", "compact")),
                "items": items,
                "updated_at": batch.updated_at.isoformat(),
                "service_stale": self.service.is_stale(),
                "limitations": "Yahoo symbol coverage may vary for some contracts.",
            },
            debug={"contracts": contracts, "provider_error": self.service.last_error, "asset_type": "future"},
        )


def _format_item(quote: FuturesQuoteNormalized) -> dict[str, object]:
    trend = "down" if quote.percent_change < 0 else "up" if quote.percent_change > 0 else "flat"
    return {
        "contract": quote.contract,
        "label": quote.label,
        "value": f"{quote.price:.2f}",
        "delta": f"{quote.percent_change:+.2f}%",
        "trend": trend,
        "stale": quote.stale,
        "session": quote.session,
        "asset_type": quote.asset_type,
    }


def _render_value(items: list[dict[str, object]], *, display_mode: str) -> str:
    if not items:
        return "n/a"
    if display_mode.lower() == "full":
        return " | ".join(f"{item['label']} {item['value']} {item['delta']}" for item in items[:2])
    return " | ".join(f"{item['label']} {item['delta']}" for item in items[:3])
