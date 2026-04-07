from __future__ import annotations

from datetime import UTC, datetime

from app.core.models import DataOrigin, Freshness, HealthState, Severity, WidgetData
from app.widgets.base import Widget


class ClockWidget(Widget):
    async def fetch_primary(self) -> WidgetData:
        now = datetime.now()
        show_seconds = bool(self.config.get("show_seconds", True))
        show_date = bool(self.config.get("show_date", False))
        use_24h = bool(self.config.get("use_24h", True))
        mode = str(self.config.get("display_mode", "time")).lower()

        default_time_format = "%H:%M:%S" if use_24h else "%I:%M:%S %p"
        if not show_seconds:
            default_time_format = "%H:%M" if use_24h else "%I:%M %p"

        time_format = str(self.config.get("time_format") or default_time_format)
        date_format = str(self.config.get("date_format", "%Y-%m-%d"))

        time_value = now.strftime(time_format).lstrip("0") if not use_24h else now.strftime(time_format)
        date_value = now.strftime(date_format)

        if mode == "date":
            visible = date_value
        elif mode == "datetime" or show_date:
            visible = f"{time_value} {date_value}".strip()
        else:
            visible = time_value

        return self.normalized(
            "Clock",
            visible,
            severity=Severity.ok,
            source_label="local-clock",
            status_summary="time generated locally",
            extra={
                "time": time_value,
                "date": date_value,
                "display_mode": mode,
                "show_seconds": show_seconds,
                "show_date": show_date,
                "use_24h": use_24h,
                "time_format": time_format,
                "date_format": date_format,
                "hour": now.hour,
                "minute": now.minute,
                "second": now.second,
            },
        )

    def build_fallback(self, error: Exception | None, last_known: WidgetData | None) -> WidgetData:
        if last_known is not None:
            fallback = last_known.model_copy(deep=True)
            fallback.timestamp = datetime.now(UTC)
            fallback.freshness = Freshness.stale
            fallback.data_origin = DataOrigin.cache
            fallback.health_state = HealthState.degraded
            fallback.status_summary = "clock fallback using last known"
            fallback.debug.update({"error": str(error) if error else "clock primary unavailable"})
            return fallback

        return self.normalized(
            "Clock",
            "CLOCK ERR",
            severity=Severity.warning,
            freshness=Freshness.fallback,
            data_origin=DataOrigin.synthetic,
            health_state=HealthState.failed,
            source_label="local-clock:fallback",
            status_summary="clock fallback synthetic",
            debug={"error": str(error) if error else "clock error"},
            extra={"time": None, "date": None},
        )
