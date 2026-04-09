from app.core.config import DashboardConfig
from app.widgets.factory import build_widgets


def test_page_bound_widget_not_assigned_is_not_scheduled() -> None:
    config = DashboardConfig.model_validate(
        {
            "renderer": {"mode": "simulator"},
            "widgets": {
                "clock": {
                    "enabled": True,
                    "run_mode": "page_bound",
                    "refresh_seconds": 1,
                    "ttl_seconds": 2,
                    "retries": 1,
                    "config": {},
                },
                "custom_text": {
                    "enabled": True,
                    "run_mode": "background_always",
                    "refresh_seconds": 60,
                    "ttl_seconds": 120,
                    "retries": 1,
                    "config": {"message": "hello"},
                },
            },
            "pages": [
                {"page_id": "p1", "name": "P1", "layout": "single_kpi", "widgets": ["custom_text"]},
            ],
        }
    )

    widgets = build_widgets(config)

    assert "clock" not in widgets
    assert "custom_text" in widgets


def test_page_bound_widget_assigned_is_scheduled() -> None:
    config = DashboardConfig.model_validate(
        {
            "renderer": {"mode": "simulator"},
            "widgets": {
                "clock": {
                    "enabled": True,
                    "run_mode": "page_bound",
                    "refresh_seconds": 1,
                    "ttl_seconds": 2,
                    "retries": 1,
                    "config": {},
                },
            },
            "pages": [
                {"page_id": "p1", "name": "P1", "layout": "single_kpi", "widgets": ["clock"]},
            ],
        }
    )

    widgets = build_widgets(config)

    assert "clock" in widgets
