from __future__ import annotations

from PIL import Image, ImageDraw

from app.core.models import PageDefinition, WidgetData
from app.render.font_helpers import load_font
from app.render.primitives import severity_color
from app.render.ticker import TickerState


class LayoutEngine:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.ticker = TickerState()

    def render_page(self, page: PageDefinition, data_map: dict[str, WidgetData], override: str | None = None) -> Image.Image:
        image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        small = load_font("small")
        med = load_font("medium")
        large = load_font("large")

        if page.layout == "alert_fullscreen" and override:
            draw.rectangle((0, 0, self.width - 1, self.height - 1), fill=(120, 0, 0), outline=(255, 255, 0))
            draw.text((2, 8), override[:18], font=large, fill=(255, 255, 255))
            return image

        if page.layout == "ticker_only":
            text = " | ".join(data_map[w].value for w in page.widgets if w in data_map)
            draw.text((1, 12), self.ticker.next_text(text, 28), font=med, fill=(120, 220, 255))
            return image

        if page.layout == "single_kpi":
            wd = data_map.get(page.widgets[0]) if page.widgets else None
            if wd:
                draw.text((1, 0), wd.title[:20], font=small, fill=(140, 140, 140))
                draw.text((1, 14), wd.value[:18], font=large, fill=severity_color(wd.severity))
            return image

        if page.layout == "two_column":
            for idx, wid in enumerate(page.widgets[:2]):
                wd = data_map.get(wid)
                if not wd:
                    continue
                x = 1 + (idx * (self.width // 2))
                draw.text((x, 1), wd.title[:10], font=small, fill=(170, 170, 170))
                draw.text((x, 12), wd.value[:9], font=med, fill=severity_color(wd.severity))
            return image

        if page.layout == "split_banner":
            top = data_map.get(page.widgets[0]) if page.widgets else None
            lower = data_map.get(page.widgets[1]) if len(page.widgets) > 1 else None
            if top:
                draw.text((1, 1), f"{top.title}: {top.value}"[:27], font=med, fill=severity_color(top.severity))
            if lower:
                draw.rectangle((0, 18, self.width - 1, self.height - 1), fill=(0, 0, 40))
                draw.text((1, 22), lower.value[:28], font=small, fill=(220, 220, 220))
            return image

        draw.rectangle((0, 0, self.width - 1, self.height - 1), outline=(30, 30, 120))
        draw.text((2, 12), page.name[:24], font=med, fill=(255, 255, 255))
        return image
