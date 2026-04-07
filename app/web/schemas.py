from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import DashboardConfig, ScheduleConfig
from app.core.models import PageDefinition, RenderFrame, WidgetData, WidgetStatus


class ApiRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OverrideRequest(ApiRequestModel):
    message: str | None = Field(default=None, max_length=80, description="Temporary override message shown on the panel")

    @field_validator("message", mode="before")
    @classmethod
    def normalize_blank_message(cls, value: str | None) -> str | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class BrightnessRequest(ApiRequestModel):
    brightness: int = Field(ge=1, le=100, description="Panel brightness percentage")


class PinPageRequest(ApiRequestModel):
    page_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Page identifier to pin. Set null to clear pin.",
    )


class OverrideResponse(BaseModel):
    ok: bool = True
    message: str | None = None


class BrightnessResponse(BaseModel):
    ok: bool = True
    brightness: int


class PinPageResponse(BaseModel):
    ok: bool = True
    pinned_page_id: str | None = None


class ReloadResponse(BaseModel):
    ok: bool = True
    message: str = "runtime reloaded"


class StatusResponse(BaseModel):
    running: bool
    mode: str
    current_page_id: str | None = None
    pinned_page_id: str | None = None
    brightness: int
    override_message: str | None = None
    last_frame: RenderFrame


class WidgetsResponse(BaseModel):
    data: dict[str, WidgetData] = Field(default_factory=dict)
    status: dict[str, WidgetStatus] = Field(default_factory=dict)


class PagesResponse(BaseModel):
    pages: list[PageDefinition] = Field(default_factory=list)


class ConfigResponse(BaseModel):
    config: DashboardConfig


class ScheduleResponse(BaseModel):
    schedule: ScheduleConfig