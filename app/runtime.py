from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from io import BytesIO

from PIL import Image

from app.core.cache import TTLCache
from app.core.config import DashboardConfig
from app.core.models import AppState, PageDefinition, RenderFrame, WidgetData
from app.core.scheduler import WidgetScheduler
from app.pages.page_builder import build_pages
from app.pages.rotation import RotationController
from app.render.layout_engine import LayoutEngine
from app.render.piomatter import PiomatterRenderer
from app.render.renderer import Renderer
from app.render.simulator import SimulatorRenderer
from app.widgets.factory import build_widgets

logger = logging.getLogger(__name__)


class DashboardRuntime:
    def __init__(self, config: DashboardConfig) -> None:
        self.config = config
        self.state = AppState(mode=config.renderer.mode)
        self.widgets = build_widgets(config)
        self.pages: list[PageDefinition] = build_pages(config)
        self.rotation = RotationController(self.pages)
        self.layout = LayoutEngine(config.panel.width, config.panel.height)
        self.cache: TTLCache[WidgetData] = TTLCache()
        self.scheduler = WidgetScheduler(self.widgets, self.cache, self.state.widget_status)
        self.renderer = self._build_renderer()
        self._render_task: asyncio.Task[None] | None = None
        self._running = False
        self._last_frame = RenderFrame(width=config.panel.width, height=config.panel.height, page_id=self.pages[0].page_id)

    def _schedule_brightness(self) -> int:
        now_hour = datetime.now().hour
        schedule = self.config.schedule
        if schedule.day_start_hour <= now_hour < schedule.night_start_hour:
            return schedule.day_brightness
        return schedule.night_brightness

    def _build_renderer(self) -> Renderer:
        if self.config.renderer.mode == "piomatter":
            logger.info("renderer mode: piomatter")
            return PiomatterRenderer(
                width=self.config.panel.width,
                height=self.config.panel.height,
                hardware_mapping=self.config.renderer.hardware_mapping,
                n_addr_lines=self.config.renderer.n_addr_lines,
            )
        if self.config.renderer.mode == "simulator":
            logger.info("renderer mode: simulator")
            return SimulatorRenderer(width=self.config.panel.width, height=self.config.panel.height, output_dir=".simulator")
        raise RuntimeError(f"Unsupported renderer mode: {self.config.renderer.mode}")

    async def start(self) -> None:
        logger.info("starting runtime")
        self._running = True
        self.state.running = True
        await self.scheduler.start()
        self._render_task = asyncio.create_task(self._render_loop())

    async def stop(self) -> None:
        logger.info("stopping runtime")
        self._running = False
        self.state.running = False
        if self._render_task:
            self._render_task.cancel()
            await asyncio.gather(self._render_task, return_exceptions=True)
        await self.scheduler.stop()
        self.renderer.close()

    async def _render_loop(self) -> None:
        while self._running:
            self.state.widget_data = dict(self.scheduler.data)
            self.set_brightness(self._schedule_brightness())
            page = self.rotation.tick(self.state.pinned_page_id)
            self.state.current_page_id = page.page_id
            image = self.layout.render_page(page=page, data_map=self.state.widget_data, override=self.state.override_message)
            self.renderer.draw_frame(image)
            self._last_frame = RenderFrame(
                width=self.renderer.width,
                height=self.renderer.height,
                page_id=page.page_id,
                rendered_at=datetime.now(UTC),
                annotations={"widget_count": len(self.state.widget_data)},
            )
            await asyncio.sleep(0.15)

    def set_override(self, message: str | None) -> None:
        self.state.override_message = message

    def set_pinned_page(self, page_id: str | None) -> None:
        self.state.pinned_page_id = page_id

    def set_brightness(self, brightness: int) -> None:
        self.state.brightness = max(1, min(100, brightness))
        self.renderer.set_brightness(self.state.brightness)

    def preview_png(self) -> bytes:
        image: Image.Image = self.renderer.get_last_image()
        out = BytesIO()
        image.resize((self.config.panel.width * 4, self.config.panel.height * 4), Image.NEAREST).save(out, format="PNG")
        return out.getvalue()

    def status(self) -> dict:
        page_by_id = {page.page_id: page.name for page in self.pages}
        current_page_id = self.state.current_page_id
        pinned_page_id = self.state.pinned_page_id
        return {
            "running": self.state.running,
            "mode": self.state.mode,
            "current_page_id": current_page_id,
            "current_page_name": page_by_id.get(current_page_id) if current_page_id else None,
            "pinned_page_id": pinned_page_id,
            "pinned_page_name": page_by_id.get(pinned_page_id) if pinned_page_id else None,
            "page_ids": [page.page_id for page in self.pages],
            "brightness": self.state.brightness,
            "override_message": self.state.override_message,
            "last_frame": self._last_frame.model_dump(mode="json"),
        }
