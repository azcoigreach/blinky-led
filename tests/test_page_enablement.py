from app.core.config import DashboardConfig
from app.pages.page_builder import build_pages


def test_page_enabled_defaults_true() -> None:
    config = DashboardConfig.model_validate(
        {
            "renderer": {"mode": "simulator"},
            "widgets": {
                "clock": {
                    "enabled": True,
                    "refresh_seconds": 1,
                    "ttl_seconds": 2,
                    "retries": 1,
                    "config": {},
                }
            },
            "pages": [
                {"page_id": "p1", "name": "P1", "layout": "single_kpi", "widgets": ["clock"]},
            ],
        }
    )

    assert config.pages[0].enabled is True


def test_build_pages_excludes_disabled_pages() -> None:
    config = DashboardConfig.model_validate(
        {
            "renderer": {"mode": "simulator"},
            "widgets": {
                "clock": {
                    "enabled": True,
                    "refresh_seconds": 1,
                    "ttl_seconds": 2,
                    "retries": 1,
                    "config": {},
                }
            },
            "pages": [
                {
                    "page_id": "p1",
                    "name": "Enabled",
                    "enabled": True,
                    "layout": "single_kpi",
                    "widgets": ["clock"],
                },
                {
                    "page_id": "p2",
                    "name": "Disabled",
                    "enabled": False,
                    "layout": "single_kpi",
                    "widgets": ["clock"],
                },
            ],
        }
    )

    pages = build_pages(config)

    assert [page.page_id for page in pages] == ["p1"]
