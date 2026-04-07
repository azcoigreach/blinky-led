from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from app.core.cache import TTLCache
from app.core.models import Freshness, WidgetData, WidgetStatus
from app.widgets.base import Widget

logger = logging.getLogger(__name__)


class WidgetScheduler:
    def __init__(self, widgets: dict[str, Widget], cache: TTLCache[WidgetData], status: dict[str, WidgetStatus]) -> None:
        self.widgets = widgets
        self.cache = cache
        self.status = status
        self._tasks: list[asyncio.Task[None]] = []
        self._data: dict[str, WidgetData] = {}
        self._running = False

    @property
    def data(self) -> dict[str, WidgetData]:
        return self._data

    async def start(self) -> None:
        self._running = True
        for widget in self.widgets.values():
            self._tasks.append(asyncio.create_task(self._run_widget(widget)))

    async def stop(self) -> None:
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def _run_widget(self, widget: Widget) -> None:
        wid = widget.widget_id
        self.status.setdefault(wid, WidgetStatus(widget_id=wid))
        while self._running:
            cached = self.cache.get(wid)
            if cached:
                self._data[wid] = cached
                await asyncio.sleep(max(1, widget.refresh_seconds // 2))
                continue
            try:
                data = await widget.fetch()
                data.timestamp = datetime.now(UTC)
                self._data[wid] = data
                self.cache.set(wid, data, widget.ttl_seconds)
                self.status[wid] = WidgetStatus(
                    widget_id=wid,
                    healthy=True,
                    last_refresh=datetime.now(UTC),
                    retries=0,
                    source_health="ok",
                )
                logger.info("widget refresh success: %s", wid)
            except Exception as exc:  # noqa: BLE001
                previous = self._data.get(wid)
                if previous:
                    previous.freshness = Freshness.stale
                    self._data[wid] = previous
                curr = self.status.get(wid, WidgetStatus(widget_id=wid))
                self.status[wid] = WidgetStatus(
                    widget_id=wid,
                    healthy=False,
                    last_refresh=curr.last_refresh,
                    retries=curr.retries + 1,
                    last_error=str(exc),
                    source_health="degraded",
                )
                logger.exception("widget refresh failed: %s", wid)
            await asyncio.sleep(widget.refresh_seconds)
