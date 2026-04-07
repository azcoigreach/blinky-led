from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    ok = "ok"
    info = "info"
    warning = "warning"
    critical = "critical"


class Freshness(str, Enum):
    fresh = "fresh"
    stale = "stale"
    error = "error"


class WidgetStatus(BaseModel):
    widget_id: str
    healthy: bool = True
    last_refresh: datetime | None = None
    last_error: str | None = None
    retries: int = 0
    source_health: str = "unknown"


class WidgetData(BaseModel):
    widget_id: str
    title: str
    value: str
    delta: str | None = None
    trend: str | None = None
    severity: Severity = Severity.info
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    freshness: Freshness = Freshness.fresh
    source_label: str = "local"
    extra: dict[str, Any] = Field(default_factory=dict)


class LayoutRegion(BaseModel):
    name: str
    x: int
    y: int
    width: int
    height: int


class PageDefinition(BaseModel):
    page_id: str
    name: str
    layout: str
    widgets: list[str] = Field(default_factory=list)
    pinned: bool = False
    duration_seconds: int = 8
    ticker_widget: str | None = None


class RenderFrame(BaseModel):
    width: int
    height: int
    page_id: str
    rendered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    annotations: dict[str, Any] = Field(default_factory=dict)


class AppState(BaseModel):
    mode: str = "simulator"
    running: bool = False
    current_page_id: str | None = None
    pinned_page_id: str | None = None
    brightness: int = 60
    override_message: str | None = None
    widget_data: dict[str, WidgetData] = Field(default_factory=dict)
    widget_status: dict[str, WidgetStatus] = Field(default_factory=dict)
    rotation_index: int = 0
