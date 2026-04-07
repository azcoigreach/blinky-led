from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from datetime import UTC, datetime
from typing import Any

from app.core.models import DataOrigin, Freshness, HealthState, Severity, WidgetData, WidgetStatus


class Widget(ABC):
    widget_id: str

    def __init__(
        self,
        widget_id: str,
        refresh_seconds: int = 60,
        ttl_seconds: int = 180,
        retries: int = 2,
        retry_backoff_seconds: float = 0.4,
        fallback_policy: str = "last_known_or_synthetic",
        source_label: str = "local",
        config: dict[str, Any] | None = None,
    ) -> None:
        self.widget_id = widget_id
        self.refresh_seconds = refresh_seconds
        self.ttl_seconds = ttl_seconds
        self.retries = max(0, retries)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self.fallback_policy = fallback_policy
        self.source_label = source_label
        self.config = config or {}

        self._last_success: WidgetData | None = None
        self._last_success_time: datetime | None = None
        self._last_attempt_time: datetime | None = None
        self._last_failure_time: datetime | None = None
        self._last_error_message: str | None = None
        self._consecutive_failures = 0

    @abstractmethod
    async def fetch_primary(self) -> WidgetData:
        raise NotImplementedError

    async def fetch(self) -> WidgetData:
        # Backward compatibility for direct widget.fetch() usage in tests and callers.
        return await self.fetch_primary()

    def build_fallback(self, error: Exception | None, last_known: WidgetData | None) -> WidgetData:
        if last_known is not None and self.fallback_policy in {"last_known", "last_known_or_synthetic"}:
            fallback = last_known.model_copy(deep=True)
            fallback.timestamp = datetime.now(UTC)
            fallback.freshness = Freshness.stale
            fallback.data_origin = DataOrigin.cache
            fallback.health_state = HealthState.degraded
            fallback.status_summary = "serving last known data"
            fallback.debug.update(
                {
                    "fallback_reason": str(error) if error else "primary unavailable",
                    "fallback_policy": self.fallback_policy,
                }
            )
            return fallback

        message = str(error) if error else "primary unavailable"
        return self.normalized(
            self.widget_id.replace("_", " ").title(),
            "DATA ERR",
            severity=Severity.warning,
            freshness=Freshness.fallback,
            data_origin=DataOrigin.synthetic,
            health_state=HealthState.failed,
            status_summary="fallback synthetic output",
            debug={"error": message, "fallback_policy": self.fallback_policy},
            source_label=f"{self.source_label}:fallback",
        )

    async def run_cycle(self) -> tuple[WidgetData, WidgetStatus]:
        self._last_attempt_time = datetime.now(UTC)
        attempts = 0
        last_error: Exception | None = None
        max_attempts = self.retries + 1
        for attempt in range(max_attempts):
            attempts = attempt + 1
            try:
                data = await self.fetch_primary()
                data.timestamp = datetime.now(UTC)
                data.freshness = Freshness.fresh
                data.data_origin = DataOrigin.primary
                if data.health_state not in {HealthState.healthy, HealthState.degraded}:
                    data.health_state = HealthState.healthy
                data.source_label = data.source_label or self.source_label
                data.debug.update(
                    {
                        "attempts_made": attempts,
                        "retry_count_used": max(0, attempts - 1),
                    }
                )

                self._last_success = data.model_copy(deep=True)
                self._last_success_time = data.timestamp
                self._last_error_message = None
                self._consecutive_failures = 0
                status_health_state = data.health_state
                return data, self._build_status(
                    data=data,
                    health_state=status_health_state,
                    attempts=attempts,
                    last_error=None,
                    fallback_active=False,
                    serving_stale=False,
                )
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                self._last_error_message = str(exc)
                self._last_failure_time = datetime.now(UTC)
                if attempts < max_attempts:
                    backoff = self.retry_backoff_seconds * (2**attempt)
                    if backoff > 0:
                        await asyncio.sleep(backoff)

        self._consecutive_failures += 1
        fallback = self.build_fallback(last_error, self._last_success)
        fallback.timestamp = datetime.now(UTC)
        fallback.debug.update(
            {
                "attempts_made": attempts,
                "retry_count_used": max(0, attempts - 1),
                "last_error": str(last_error) if last_error else "unknown",
            }
        )
        serving_stale = fallback.freshness == Freshness.stale
        health_state = HealthState.degraded if serving_stale else HealthState.failed
        fallback.health_state = health_state
        return fallback, self._build_status(
            data=fallback,
            health_state=health_state,
            attempts=attempts,
            last_error=last_error,
            fallback_active=True,
            serving_stale=serving_stale,
        )

    def _build_status(
        self,
        *,
        data: WidgetData,
        health_state: HealthState,
        attempts: int,
        last_error: Exception | None,
        fallback_active: bool,
        serving_stale: bool,
    ) -> WidgetStatus:
        summary = data.status_summary
        if last_error is not None and not summary:
            summary = "primary fetch failed"
        return WidgetStatus(
            widget_id=self.widget_id,
            healthy=health_state == HealthState.healthy,
            health_state=health_state,
            last_refresh=data.timestamp,
            last_success_time=self._last_success_time,
            last_attempt_time=self._last_attempt_time,
            last_failure_time=self._last_failure_time,
            last_error=str(last_error) if last_error else None,
            last_error_message=self._last_error_message,
            retries=self.retries,
            retry_count_used=max(0, attempts - 1),
            attempts_made=attempts,
            consecutive_failures=self._consecutive_failures,
            source_health="ok" if health_state == HealthState.healthy else "degraded",
            source_label=data.source_label or self.source_label,
            fallback_active=fallback_active,
            serving_stale_data=serving_stale,
            last_data_origin=data.data_origin,
            last_freshness=data.freshness,
            status_summary=summary,
            debug={
                "widget_type": self.__class__.__name__,
                "fallback_policy": self.fallback_policy,
            },
        )

    def normalized(self, title: str, value: str, **kwargs: object) -> WidgetData:
        return WidgetData(
            widget_id=self.widget_id,
            title=title,
            value=value,
            delta=kwargs.get("delta"),
            trend=kwargs.get("trend"),
            severity=kwargs.get("severity", Severity.info),
            timestamp=datetime.now(UTC),
            freshness=kwargs.get("freshness", Freshness.fresh),
            data_origin=kwargs.get("data_origin", DataOrigin.primary),
            health_state=kwargs.get("health_state", HealthState.healthy),
            source_label=str(kwargs.get("source_label", "local")),
            status_summary=str(kwargs.get("status_summary", "ok")),
            debug=kwargs.get("debug", {}),
            extra=kwargs.get("extra", {}),
        )
