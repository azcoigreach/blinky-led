import asyncio

import pytest

from app.core.cache import TTLCache
from app.core.models import DataOrigin, HealthState, Severity, WidgetStatus
from app.core.scheduler import WidgetScheduler
from app.widgets.base import Widget


class EventuallyHealthyWidget(Widget):
    def __init__(self, *args, fail_times: int = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_times = fail_times
        self.calls = 0

    async def fetch_primary(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise RuntimeError("source timeout")
        return self.normalized("Retry", "GOOD", severity=Severity.ok, source_label="test")


@pytest.mark.asyncio
async def test_scheduler_uses_widget_retry_and_status() -> None:
    widget = EventuallyHealthyWidget(
        "retry_widget",
        refresh_seconds=1,
        ttl_seconds=5,
        retries=2,
        retry_backoff_seconds=0.0,
        fail_times=2,
    )
    status: dict[str, WidgetStatus] = {}
    scheduler = WidgetScheduler({"retry_widget": widget}, TTLCache(), status)
    scheduler._running = True

    task = asyncio.create_task(scheduler._run_widget(widget))
    await asyncio.sleep(0.05)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    assert scheduler.data["retry_widget"].value == "GOOD"
    assert scheduler.data["retry_widget"].data_origin == DataOrigin.primary
    assert status["retry_widget"].health_state == HealthState.healthy
    assert status["retry_widget"].retry_count_used == 2
    assert status["retry_widget"].attempts_made == 3


@pytest.mark.asyncio
async def test_scheduler_serves_synthetic_fallback_on_final_failure() -> None:
    widget = EventuallyHealthyWidget(
        "retry_widget",
        refresh_seconds=1,
        ttl_seconds=5,
        retries=1,
        retry_backoff_seconds=0.0,
        fail_times=99,
        fallback_policy="synthetic",
    )
    status: dict[str, WidgetStatus] = {}
    scheduler = WidgetScheduler({"retry_widget": widget}, TTLCache(), status)
    scheduler._running = True

    task = asyncio.create_task(scheduler._run_widget(widget))
    await asyncio.sleep(0.05)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)

    assert scheduler.data["retry_widget"].data_origin == DataOrigin.synthetic
    assert status["retry_widget"].health_state == HealthState.failed
    assert status["retry_widget"].fallback_active is True
    assert status["retry_widget"].last_error_message == "source timeout"
