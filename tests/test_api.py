from fastapi.testclient import TestClient
from click.testing import CliRunner

from app.cli import cli
from app.core.config import DashboardConfig
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
