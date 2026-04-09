from __future__ import annotations

from app.core.config import DashboardConfig
from app.widgets.base import Widget
from app.widgets.clock import ClockWidget
from app.widgets.crypto import CryptoWidget
from app.widgets.custom_text import CustomTextWidget
from app.widgets.futures import FuturesWidget
from app.widgets.gas import GasWidget
from app.widgets.markets import MarketsWidget
from app.widgets.news import NewsWidget
from app.widgets.poll import PollWidget
from app.widgets.stocks import StocksWidget
from app.widgets.system import SystemWidget
from app.widgets.weather import WeatherWidget

WIDGET_TYPES: dict[str, type[Widget]] = {
    "clock": ClockWidget,
    "weather": WeatherWidget,
    "stocks": StocksWidget,
    "markets": MarketsWidget,
    "futures": FuturesWidget,
    "crypto": CryptoWidget,
    "gas": GasWidget,
    "news": NewsWidget,
    "poll": PollWidget,
    "system": SystemWidget,
    "custom_text": CustomTextWidget,
}


def build_widgets(config: DashboardConfig) -> dict[str, Widget]:
    widgets: dict[str, Widget] = {}
    assigned_widget_ids = {widget_id for page in config.pages for widget_id in page.widgets}
    for name, widget_cfg in config.widgets.items():
        if not widget_cfg.enabled:
            continue
        if widget_cfg.run_mode == "page_bound" and name not in assigned_widget_ids:
            continue
        widget_cls = WIDGET_TYPES.get(name)
        if not widget_cls:
            continue
        widget_runtime_config = dict(widget_cfg.config)
        provider_family = getattr(config.providers, name, None)
        if provider_family is not None:
            family_payload = provider_family.model_dump(exclude_none=True)
            widget_runtime_config = {
                **family_payload.get("config", {}),
                **widget_runtime_config,
            }
            if "symbols" in family_payload and family_payload["symbols"]:
                widget_runtime_config.setdefault("symbols", family_payload["symbols"])
            if "labels" in family_payload and family_payload["labels"]:
                widget_runtime_config.setdefault("labels", family_payload["labels"])
            if "aliases" in family_payload and family_payload["aliases"]:
                widget_runtime_config.setdefault("aliases", family_payload["aliases"])
            if family_payload.get("provider"):
                widget_runtime_config.setdefault("provider", family_payload["provider"])
            if family_payload.get("primary"):
                widget_runtime_config.setdefault("primary", family_payload["primary"])
            if family_payload.get("fallback"):
                widget_runtime_config.setdefault("fallback", family_payload["fallback"])
            if family_payload.get("refresh_seconds"):
                widget_runtime_config.setdefault("refresh_seconds", family_payload["refresh_seconds"])
            if family_payload.get("stale_after_seconds"):
                widget_runtime_config.setdefault("stale_after_seconds", family_payload["stale_after_seconds"])
            if family_payload.get("enabled") is False:
                continue
        widgets[name] = widget_cls(
            widget_id=name,
            refresh_seconds=widget_cfg.refresh_seconds,
            ttl_seconds=widget_cfg.ttl_seconds,
            retries=widget_cfg.retries,
            retry_backoff_seconds=widget_cfg.retry_backoff_seconds,
            fallback_policy=widget_cfg.fallback_policy,
            source_label=widget_cfg.source_label or name,
            config=widget_runtime_config,
        )
    return widgets
