from __future__ import annotations

from app.core.models import Severity
from app.widgets.base import Widget


class PollWidget(Widget):
    async def fetch_primary(self):
        candidate = self.config.get("candidate", "A")
        value = float(self.config.get("fixture_percent", 49.0))
        severity = Severity.critical if value < 40 else Severity.info
        return self.normalized(
            "Poll",
            f"{candidate}: {value:.1f}%",
            severity=severity,
            source_label="fixture",
            status_summary="poll fixture loaded",
            extra={"candidate": candidate, "percent": value},
        )
