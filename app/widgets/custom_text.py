from __future__ import annotations

from app.core.models import Severity
from app.widgets.base import Widget


class CustomTextWidget(Widget):
    async def fetch(self):
        message = str(self.config.get("message", "BLINKY V3"))
        return self.normalized("Message", message, severity=Severity.ok, source_label="config")
