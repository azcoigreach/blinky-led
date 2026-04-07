from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from app.core.models import Freshness, Severity, WidgetData


class Widget(ABC):
    widget_id: str

    def __init__(self, widget_id: str, refresh_seconds: int = 60, ttl_seconds: int = 180, config: dict | None = None) -> None:
        self.widget_id = widget_id
        self.refresh_seconds = refresh_seconds
        self.ttl_seconds = ttl_seconds
        self.config = config or {}

    @abstractmethod
    async def fetch(self) -> WidgetData:
        raise NotImplementedError

    def normalized(self, title: str, value: str, **kwargs: object) -> WidgetData:
        return WidgetData(
            widget_id=self.widget_id,
            title=title,
            value=value,
            delta=kwargs.get("delta"),
            trend=kwargs.get("trend"),
            severity=kwargs.get("severity", Severity.info),
            timestamp=datetime.now(UTC),
            freshness=kwargs.get("freshness", Freshness.fresh),
            source_label=str(kwargs.get("source_label", "local")),
            extra=kwargs.get("extra", {}),
        )
