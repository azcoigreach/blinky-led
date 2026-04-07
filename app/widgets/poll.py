from __future__ import annotations

from app.core.models import Severity
from app.providers.polls import build_poll_provider
from app.widgets.base import Widget


class PollWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = build_poll_provider(self.config, source_label=self.source_label)

    async def fetch_primary(self):
        reading = await self.provider.fetch_poll()
        candidate = reading.candidate
        value = reading.percent
        severity = Severity.critical if value < 40 else Severity.info
        return self.normalized(
            "Poll",
            f"{candidate}: {value:.1f}%",
            severity=severity,
            source_label=reading.meta.source_label,
            status_summary="poll reading loaded",
            extra={
                "candidate": candidate,
                "percent": value,
                "provider_fetched_at": reading.meta.fetched_at.isoformat(),
            },
            debug=reading.meta.debug,
        )
