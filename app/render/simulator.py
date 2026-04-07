from __future__ import annotations

from pathlib import Path

from PIL import Image

from app.render.renderer import Renderer


class SimulatorRenderer(Renderer):
    def __init__(self, width: int, height: int, output_dir: str | None = None) -> None:
        self.width = width
        self.height = height
        self._brightness = 100
        self._last_image = Image.new("RGB", (width, height), (0, 0, 0))
        self._output_dir = Path(output_dir) if output_dir else None
        if self._output_dir:
            self._output_dir.mkdir(parents=True, exist_ok=True)

    def draw_frame(self, image: Image.Image) -> None:
        self._last_image = image.copy()
        if self._output_dir:
            self._last_image.save(self._output_dir / "preview.png")

    def set_brightness(self, brightness: int) -> None:
        self._brightness = max(1, min(100, brightness))

    def get_last_image(self) -> Image.Image:
        return self._last_image

    def close(self) -> None:
        return None
