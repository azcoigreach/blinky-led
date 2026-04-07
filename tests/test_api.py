from fastapi.testclient import TestClient
from click.testing import CliRunner

from app.cli import cli
from app.core.config import DashboardConfig
from app.core.models import Freshness, HealthState, WidgetStatus
from app.runtime import DashboardRuntime
from app.web.server import create_web_app


def _make_config() -> DashboardConfig:
    return DashboardConfig.model_validate(
        {
            "renderer": {"mode": "simulator"},
            "widgets": {
                "clock": {"enabled": True, "refresh_seconds": 1, "ttl_seconds": 2, "retries": 1, "config": {}},
                "custom_text": {
                    "enabled": True,
                    "refresh_seconds": 60,
                    "ttl_seconds": 120,
                    "retries": 1,
                    "config": {"message": "test"},
                },
            },
            "pages": [
                {"page_id": "p1", "name": "P1", "layout": "single_kpi", "widgets": ["clock"]},
            ],
        }
    )


def test_api_status_and_preview() -> None:
    runtime = DashboardRuntime(_make_config())
    app = create_web_app(runtime)
    with TestClient(app) as client:
        status = client.get("/api/status")
        assert status.status_code == 200
        status_payload = status.json()
        assert {"running", "mode", "brightness", "last_frame"}.issubset(status_payload.keys())
        assert isinstance(status_payload["brightness"], int)
        assert {"page_id", "width", "height", "rendered_at"}.issubset(status_payload["last_frame"].keys())

        widgets = client.get("/api/widgets")
        assert widgets.status_code == 200
        widgets_payload = widgets.json()
        assert "data" in widgets_payload
        assert "status" in widgets_payload

        preview = client.get("/api/preview")
        assert preview.status_code == 200
        assert preview.headers["content-type"] == "image/png"


def test_api_override() -> None:
    runtime = DashboardRuntime(_make_config())
    app = create_web_app(runtime)
    with TestClient(app) as client:
        response = client.post("/api/override", json={"message": "ALERT"})
        assert response.status_code == 200
        assert response.json()["message"] == "ALERT"


def test_api_override_invalid_message_length() -> None:
    runtime = DashboardRuntime(_make_config())
    app = create_web_app(runtime)
    with TestClient(app) as client:
        response = client.post("/api/override", json={"message": "A" * 81})
        assert response.status_code == 422


def test_api_brightness_valid_and_invalid_range() -> None:
    runtime = DashboardRuntime(_make_config())
    app = create_web_app(runtime)
    with TestClient(app) as client:
        valid = client.post("/api/brightness", json={"brightness": 42})
        assert valid.status_code == 200
        assert valid.json() == {"ok": True, "brightness": 42}

        invalid = client.post("/api/brightness", json={"brightness": 101})
        assert invalid.status_code == 422


def test_api_pin_page_valid_and_invalid() -> None:
    runtime = DashboardRuntime(_make_config())
    app = create_web_app(runtime)
    with TestClient(app) as client:
        valid = client.post("/api/pin-page", json={"page_id": "p1"})
        assert valid.status_code == 200
        assert valid.json()["pinned_page_id"] == "p1"

        unpin = client.post("/api/pin-page", json={"page_id": None})
        assert unpin.status_code == 200
        assert unpin.json()["pinned_page_id"] is None

        invalid_shape = client.post("/api/pin-page", json={"page_id": "bad id"})
        assert invalid_shape.status_code == 422

        unknown_page = client.post("/api/pin-page", json={"page_id": "missing"})
        assert unknown_page.status_code == 404


def test_api_widgets_status_shape() -> None:
    runtime = DashboardRuntime(_make_config())
    runtime.state.widget_status["clock"] = WidgetStatus(
        widget_id="clock",
        healthy=True,
        health_state=HealthState.healthy,
        source_label="fixture",
        last_freshness=Freshness.fresh,
        status_summary="ok",
    )
    app = create_web_app(runtime)
    with TestClient(app) as client:
        widgets = client.get("/api/widgets")
        assert widgets.status_code == 200
        status_payload = widgets.json()["status"]["clock"]
        assert {
            "widget_id",
            "health_state",
            "last_freshness",
            "source_label",
            "last_success_time",
            "last_failure_time",
            "fallback_active",
            "status_summary",
        }.issubset(status_payload.keys())


def test_cli_accepts_config_after_subcommand(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
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
    name: P1
    layout: single_kpi
    widgets: [clock]
""".strip(),
        encoding="utf-8",
    )

    calls = []

    def fake_run(app, host, port):
        calls.append((app, host, port))

    monkeypatch.setattr("app.cli.uvicorn.run", fake_run)
    runner = CliRunner()
    result = runner.invoke(cli, ["serve", "--config", str(config_path), "--log-level", "INFO"])
    assert result.exit_code == 0
    assert calls
