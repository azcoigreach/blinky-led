import pytest

from app.core.models import DataOrigin, Freshness, HealthState, Severity
from app.widgets.base import Widget
from app.widgets.clock import ClockWidget
from app.widgets.custom_text import CustomTextWidget
from app.widgets.system import SystemWidget


class FlakyWidget(Widget):
    def __init__(self, *args, fail_times: int = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_times = fail_times
        self.calls = 0

    async def fetch_primary(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError("boom")
        return self.normalized("Flaky", "OK", severity=Severity.ok, source_label="test")


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


@pytest.mark.asyncio
async def test_clock_widget_configuration_output() -> None:
    widget = ClockWidget(
        "clock",
        config={
            "use_24h": False,
            "show_seconds": False,
            "show_date": True,
            "date_format": "%d/%m",
            "display_mode": "datetime",
        },
    )
    data = await widget.fetch()
    assert data.title == "Clock"
    assert "/" in data.value
    assert data.extra["show_seconds"] is False
    assert data.extra["use_24h"] is False


@pytest.mark.asyncio
async def test_widget_retry_eventual_success() -> None:
    widget = FlakyWidget("flaky", retries=2, retry_backoff_seconds=0.0, fail_times=2)
    data, status = await widget.run_cycle()

    assert data.value == "OK"
    assert data.data_origin == DataOrigin.primary
    assert status.health_state == HealthState.healthy
    assert status.retry_count_used == 2
    assert status.attempts_made == 3
    assert status.last_error is None


@pytest.mark.asyncio
async def test_widget_retry_final_failure_uses_synthetic_fallback() -> None:
    widget = FlakyWidget("flaky", retries=1, retry_backoff_seconds=0.0, fail_times=10, fallback_policy="synthetic")
    data, status = await widget.run_cycle()

    assert data.freshness == Freshness.fallback
    assert data.data_origin == DataOrigin.synthetic
    assert status.health_state == HealthState.failed
    assert status.fallback_active is True
    assert status.attempts_made == 2
    assert status.last_error_message == "boom"


@pytest.mark.asyncio
async def test_widget_failure_then_stale_last_known_fallback() -> None:
    widget = FlakyWidget("flaky", retries=0, retry_backoff_seconds=0.0, fail_times=0)
    first_data, first_status = await widget.run_cycle()
    assert first_status.health_state == HealthState.healthy

    widget.fail_times = 100
    second_data, second_status = await widget.run_cycle()
    assert second_data.value == first_data.value
    assert second_data.freshness == Freshness.stale
    assert second_data.data_origin == DataOrigin.cache
    assert second_status.health_state == HealthState.degraded
    assert second_status.serving_stale_data is True
    assert second_status.consecutive_failures == 1


@pytest.mark.asyncio
async def test_system_widget_degraded_without_psutil(monkeypatch) -> None:
    import app.widgets.system as system_module

    monkeypatch.setattr(system_module, "psutil", None)
    widget = SystemWidget("system", config={})
    data, status = await widget.run_cycle()

    assert data.title == "System"
    assert data.source_label == "os"
    assert data.health_state == HealthState.degraded
    assert "missing_metrics" in data.extra
    assert status.health_state == HealthState.degraded
    assert status.fallback_active is False


@pytest.mark.asyncio
async def test_status_fields_updated_on_failure() -> None:
    widget = FlakyWidget("flaky", retries=0, retry_backoff_seconds=0.0, fail_times=1, fallback_policy="synthetic")
    _, status = await widget.run_cycle()

    assert status.widget_id == "flaky"
    assert status.last_attempt_time is not None
    assert status.last_failure_time is not None
    assert status.last_success_time is None
    assert status.last_error_message == "boom"
    assert status.retry_count_used == 0
    assert status.attempts_made == 1
