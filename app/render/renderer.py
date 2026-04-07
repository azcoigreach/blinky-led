from __future__ import annotations

from abc import ABC, abstractmethod

from PIL.Image import Image


class Renderer(ABC):
    width: int
    height: int

    @abstractmethod
    def draw_frame(self, image: Image) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_brightness(self, brightness: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_last_image(self) -> Image:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
