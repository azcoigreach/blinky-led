from __future__ import annotations

from datetime import datetime

from app.widgets.base import Widget


class ClockWidget(Widget):
    async def fetch(self):
        now = datetime.now()
        return self.normalized("Clock", now.strftime("%H:%M:%S"), extra={"date": now.strftime("%Y-%m-%d")})
