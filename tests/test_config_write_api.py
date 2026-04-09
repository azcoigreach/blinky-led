from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import load_config
from app.runtime import DashboardRuntime
from app.web.server import create_web_app


def _write_base_config(path: Path) -> None:
    path.write_text(
        """
renderer:
  mode: simulator
widgets:
  clock:
    enabled: true
    refresh_seconds: 1
    ttl_seconds: 2
    retries: 1
    config: {}
pages:
  - page_id: p1
    name: Home
    layout: single_kpi
    widgets: [clock]
""".strip(),
        encoding="utf-8",
    )


def test_config_widget_upsert_and_apply(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    _write_base_config(config_path)

    runtime = DashboardRuntime(load_config(config_path))
    app = create_web_app(runtime, config_path=config_path)
    with TestClient(app) as client:
        save = client.post(
            "/api/config/widgets/custom_text",
            json={
                "widget": {
                    "enabled": True,
                    "refresh_seconds": 15,
                    "ttl_seconds": 30,
                    "retries": 2,
                    "config": {"message": "hello from ui"},
                }
            },
        )
        assert save.status_code == 200

        apply_config = client.post("/api/config/apply", json={"reload_runtime": True})
        assert apply_config.status_code == 200

    reloaded = load_config(config_path)
    assert "custom_text" in reloaded.widgets
    assert reloaded.widgets["custom_text"].config["message"] == "hello from ui"
    assert runtime.config.widgets["custom_text"].refresh_seconds == 15


def test_config_provider_upsert_stores_plaintext_fields(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    _write_base_config(config_path)

    runtime = DashboardRuntime(load_config(config_path))
    app = create_web_app(runtime, config_path=config_path)
    with TestClient(app) as client:
        response = client.post(
            "/api/config/providers/stocks",
            json={
                "provider": {
                    "enabled": True,
                    "primary": "finnhub",
                    "fallback": "alphavantage",
                    "api_key_env": "FINNHUB_API_KEY",
                    "symbols": ["AAPL", "SPY"],
                    "config": {
                        "api_base": "https://api.example.test/v1",
                        "token": "plain-text-token",
                    },
                }
            },
        )
        assert response.status_code == 200

    reloaded = load_config(config_path)
    assert reloaded.providers.stocks.config["token"] == "plain-text-token"
    assert reloaded.providers.stocks.config["api_base"] == "https://api.example.test/v1"


def test_pages_crud_and_reorder(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    _write_base_config(config_path)

    runtime = DashboardRuntime(load_config(config_path))
    app = create_web_app(runtime, config_path=config_path)
    with TestClient(app) as client:
        add_page = client.post(
            "/api/config/pages",
            json={
                "page": {
                    "page_id": "p2",
                    "name": "Second",
                    "layout": "single_kpi",
                    "widgets": ["clock"],
                    "duration_seconds": 10,
                }
            },
        )
        assert add_page.status_code == 200

        reorder = client.post("/api/config/pages/reorder", json={"page_ids": ["p2", "p1"]})
        assert reorder.status_code == 200

        delete = client.delete("/api/config/pages/p1")
        assert delete.status_code == 200

    reloaded = load_config(config_path)
    assert [page.page_id for page in reloaded.pages] == ["p2"]
