from __future__ import annotations

import numpy as np
from PIL import Image

from app.render.renderer import Renderer


class PiomatterRenderer(Renderer):
    """Primary Raspberry Pi 5 hardware backend using Adafruit Piomatter."""

    PINOUT_MAP = {
        "adafruit-hat": "AdafruitMatrixHat",
        "adafruit-hat-pwm": "AdafruitMatrixHat",
        "adafruit-bonnet": "AdafruitMatrixBonnet",
    }

    def __init__(self, width: int, height: int, hardware_mapping: str = "adafruit-hat", n_addr_lines: int = 4) -> None:
        try:
            from adafruit_blinka_raspberry_pi5_piomatter import (  # type: ignore
                Colorspace,
                Geometry,
                Orientation,
                Pinout,
                PioMatter,
            )
        except ImportError as exc:
            raise RuntimeError("Piomatter backend is unavailable. Install Adafruit Blinka Pi5 Piomatter.") from exc

        self.width = width
        self.height = height
        self._framebuffer = np.zeros(shape=(height, width, 3), dtype=np.uint8)
        pinout_name = self.PINOUT_MAP.get(hardware_mapping, "AdafruitMatrixHat")
        pinout = getattr(Pinout, pinout_name)
        geometry = Geometry(width=width, height=height, n_addr_lines=n_addr_lines, rotation=Orientation.Normal)
        self._matrix = PioMatter(
            colorspace=Colorspace.RGB888Packed,
            pinout=pinout,
            framebuffer=self._framebuffer,
            geometry=geometry,
        )
        self._last_image = Image.new("RGB", (width, height), (0, 0, 0))

    def draw_frame(self, image: Image.Image) -> None:
        arr = np.asarray(image.resize((self.width, self.height)))
        self._framebuffer[:] = arr
        self._last_image = image.copy()
        self._matrix.show()

    def set_brightness(self, brightness: int) -> None:
        # Piomatter currently has no stable global brightness API.
        # Stored for UI/reporting and future support.
        _ = max(1, min(100, brightness))

    def get_last_image(self) -> Image.Image:
        return self._last_image

    def close(self) -> None:
        self._framebuffer[:] = 0
        self._matrix.show()
