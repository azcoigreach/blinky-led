from __future__ import annotations

from app.core.config import DashboardConfig
from app.widgets.base import Widget
from app.widgets.clock import ClockWidget
from app.widgets.crypto import CryptoWidget
from app.widgets.custom_text import CustomTextWidget
from app.widgets.gas import GasWidget
from app.widgets.news import NewsWidget
from app.widgets.poll import PollWidget
from app.widgets.stocks import StocksWidget
from app.widgets.system import SystemWidget
from app.widgets.weather import WeatherWidget

WIDGET_TYPES: dict[str, type[Widget]] = {
    "clock": ClockWidget,
    "weather": WeatherWidget,
    "stocks": StocksWidget,
    "crypto": CryptoWidget,
    "gas": GasWidget,
    "news": NewsWidget,
    "poll": PollWidget,
    "system": SystemWidget,
    "custom_text": CustomTextWidget,
}


def build_widgets(config: DashboardConfig) -> dict[str, Widget]:
    widgets: dict[str, Widget] = {}
    for name, widget_cfg in config.widgets.items():
        if not widget_cfg.enabled:
            continue
        widget_cls = WIDGET_TYPES.get(name)
        if not widget_cls:
            continue
        widgets[name] = widget_cls(
            widget_id=name,
            refresh_seconds=widget_cfg.refresh_seconds,
            ttl_seconds=widget_cfg.ttl_seconds,
            retries=widget_cfg.retries,
            retry_backoff_seconds=widget_cfg.retry_backoff_seconds,
            fallback_policy=widget_cfg.fallback_policy,
            source_label=widget_cfg.source_label or name,
            config=widget_cfg.config,
        )
    return widgets
