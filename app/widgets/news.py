from __future__ import annotations

from app.providers.news import build_news_provider
from app.widgets.base import Widget


class NewsWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = build_news_provider(self.config, source_label=self.source_label)

    async def fetch_primary(self):
        snapshot = await self.provider.fetch_news()
        top_items = snapshot.items[:3]
        joined = " | ".join(item.title for item in top_items)
        return self.normalized(
            "News",
            joined[:120],
            source_label=snapshot.meta.source_label,
            status_summary="news headlines prepared",
            extra={
                "headlines": [item.title for item in top_items],
                "headline_count": len(snapshot.items),
                "provider_fetched_at": snapshot.meta.fetched_at.isoformat(),
            },
            debug=snapshot.meta.debug,
        )
