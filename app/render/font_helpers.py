from __future__ import annotations

from pathlib import Path

from PIL import ImageFont


def load_font(size: str = "small") -> ImageFont.ImageFont:
    base = Path(__file__).resolve().parents[1] / "media" / "fonts"
    mapping = {
        "small": base / "4x6.pil",
        "medium": base / "6x13.pil",
        "large": base / "9x15.pil",
    }
    selected = mapping.get(size, mapping["small"])
    if selected.exists():
        return ImageFont.load(str(selected))
    return ImageFont.load_default()
