from __future__ import annotations

from app.services.headlines import dedupe_headlines
from app.widgets.base import Widget


class NewsWidget(Widget):
    async def fetch_primary(self):
        headlines = self.config.get(
            "fixture_headlines",
            [
                "Markets mixed ahead of CPI",
                "Energy prices edge lower",
                "Markets mixed ahead of CPI",
            ],
        )
        unique = dedupe_headlines([str(x) for x in headlines])
        return self.normalized(
            "News",
            " | ".join(unique[:3])[:120],
            source_label="fixture",
            status_summary="news headlines prepared",
            extra={"headlines": unique[:3], "headline_count": len(unique)},
        )
