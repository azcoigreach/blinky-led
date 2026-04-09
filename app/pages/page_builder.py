from __future__ import annotations

from app.core.config import DashboardConfig
from app.core.models import PageDefinition


def build_pages(config: DashboardConfig) -> list[PageDefinition]:
    return [
        PageDefinition(
            page_id=page.page_id,
            name=page.name,
            layout=page.layout,
            widgets=page.widgets,
            pinned=page.pinned,
            duration_seconds=page.duration_seconds,
            ticker_widget=page.ticker_widget,
        )
        for page in config.pages
        if page.enabled
    ]
