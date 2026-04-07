from __future__ import annotations

from app.core.models import Severity
from app.providers.gas import build_gas_provider
from app.widgets.base import Widget


class GasWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = build_gas_provider(self.config, source_label=self.source_label)

    async def fetch_primary(self):
        price = await self.provider.fetch_gas_price()
        usd = price.usd_per_gallon
        sev = Severity.warning if usd >= 5.0 else Severity.info
        return self.normalized(
            "Gas",
            f"${usd:.2f}/gal",
            severity=sev,
            source_label=price.meta.source_label,
            status_summary="gas price loaded",
            extra={
                "usd_per_gallon": usd,
                "region": price.region,
                "provider_fetched_at": price.meta.fetched_at.isoformat(),
            },
            debug=price.meta.debug,
        )
