from __future__ import annotations


class TickerState:
    def __init__(self) -> None:
        self.offset = 0

    def next_text(self, text: str, width_chars: int) -> str:
        if not text:
            return ""
        padded = text + "   "
        if len(padded) <= width_chars:
            return padded
        start = self.offset % len(padded)
        out = (padded[start:] + padded[:start])[:width_chars]
        self.offset = (self.offset + 1) % len(padded)
        return out
