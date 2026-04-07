from __future__ import annotations

from app.core.models import Severity
from app.services.http import fetch_json
from app.widgets.base import Widget


class WeatherWidget(Widget):
    async def fetch(self):
        city = self.config.get("city", "London")
        fixture = self.config.get("fixture_temp")
        if fixture is not None:
            temp = float(fixture)
        else:
            payload = await fetch_json(f"https://wttr.in/{city}?format=j1")
            temp = float(payload["current_condition"][0]["temp_C"])
        sev = Severity.warning if temp >= 35 else Severity.ok
        return self.normalized("Weather", f"{city[:8]} {temp:.0f}C", severity=sev, source_label="wttr.in")
