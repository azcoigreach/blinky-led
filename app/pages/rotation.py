from __future__ import annotations

import time

from app.core.models import PageDefinition


class RotationController:
    def __init__(self, pages: list[PageDefinition]) -> None:
        self.pages = pages
        self.index = 0
        self._last_switch = 0.0

    def current(self, pinned_page_id: str | None = None) -> PageDefinition:
        if pinned_page_id:
            for page in self.pages:
                if page.page_id == pinned_page_id:
                    return page
        return self.pages[self.index]

    def tick(self, pinned_page_id: str | None = None) -> PageDefinition:
        page = self.current(pinned_page_id)
        if pinned_page_id:
            return page
        now = time.monotonic()
        if now - self._last_switch >= page.duration_seconds:
            self.index = (self.index + 1) % len(self.pages)
            self._last_switch = now
        return self.pages[self.index]
