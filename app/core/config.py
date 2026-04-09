from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator


class PanelConfig(BaseModel):
    width: int = 128
    height: int = 32


class RendererConfig(BaseModel):
    mode: Literal["simulator", "piomatter"] = "simulator"
    hardware_mapping: str = "adafruit-hat"
    n_addr_lines: int = 4

    @field_validator("mode", mode="before")
    @classmethod
    def normalize_mode(cls, value: Any) -> str:
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized == "hardware":
                return "piomatter"
            return normalized
        return value


class ApiConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080


class ScheduleConfig(BaseModel):
    day_brightness: int = 70
    night_brightness: int = 25
    day_start_hour: int = 7
    night_start_hour: int = 22


class WidgetConfig(BaseModel):
    enabled: bool = True
    refresh_seconds: int = 60
    ttl_seconds: int = 180
    retries: int = 2
    retry_backoff_seconds: float = 0.4
    fallback_policy: str = "last_known_or_synthetic"
    source_label: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class ProviderFamilyConfig(BaseModel):
    enabled: bool = True
    provider: str | None = None
    primary: str | None = None
    fallback: str | None = None
    refresh_seconds: int | None = None
    stale_after_seconds: int | None = None
    symbols: list[str] = Field(default_factory=list)
    labels: dict[str, str] = Field(default_factory=dict)
    aliases: dict[str, str] = Field(default_factory=dict)
    api_key_env: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class ProvidersConfig(BaseModel):
    stocks: ProviderFamilyConfig = Field(default_factory=ProviderFamilyConfig)
    markets: ProviderFamilyConfig = Field(default_factory=ProviderFamilyConfig)
    futures: ProviderFamilyConfig = Field(default_factory=ProviderFamilyConfig)
    crypto: ProviderFamilyConfig = Field(default_factory=ProviderFamilyConfig)


class PageConfig(BaseModel):
    page_id: str
    name: str
    layout: str
    widgets: list[str] = Field(default_factory=list)
    duration_seconds: int = 8
    pinned: bool = False
    ticker_widget: str | None = None


class DashboardConfig(BaseModel):
    panel: PanelConfig = Field(default_factory=PanelConfig)
    renderer: RendererConfig = Field(default_factory=RendererConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    providers: ProvidersConfig = Field(default_factory=ProvidersConfig)
    widgets: dict[str, WidgetConfig] = Field(default_factory=dict)
    pages: list[PageConfig] = Field(default_factory=list)

    @field_validator("pages")
    @classmethod
    def pages_must_exist(cls, value: list[PageConfig]) -> list[PageConfig]:
        if not value:
            raise ValueError("At least one page must be configured")
        return value


def load_config(path: str | Path) -> DashboardConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as fp:
        payload = yaml.safe_load(fp) or {}
    return DashboardConfig.model_validate(payload)
