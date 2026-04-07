from __future__ import annotations

from app.core.models import Severity
from app.widgets.base import Widget


class GasWidget(Widget):
    async def fetch(self):
        usd = float(self.config.get("fixture_price", 3.89))
        sev = Severity.warning if usd >= 5.0 else Severity.info
        return self.normalized("Gas", f"${usd:.2f}/gal", severity=sev, source_label="fixture")
