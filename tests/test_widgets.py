import pytest

from app.widgets.clock import ClockWidget
from app.widgets.custom_text import CustomTextWidget


@pytest.mark.asyncio
async def test_clock_widget_normalized() -> None:
    widget = ClockWidget("clock", refresh_seconds=1, ttl_seconds=2, config={})
    data = await widget.fetch()
    assert data.widget_id == "clock"
    assert data.title == "Clock"
    assert len(data.value) == 8


@pytest.mark.asyncio
async def test_custom_text_widget() -> None:
    widget = CustomTextWidget("custom_text", config={"message": "hello"})
    data = await widget.fetch()
    assert data.value == "hello"
