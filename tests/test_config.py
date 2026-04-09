from pathlib import Path

from app.core.config import load_config


def test_load_config(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
panel:
  width: 128
  height: 32
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
    conf = load_config(cfg)
    assert conf.panel.width == 128
    assert conf.renderer.mode == "simulator"
    assert conf.pages[0].page_id == "p1"


def test_hardware_mode_alias_maps_to_piomatter(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
renderer:
  mode: hardware
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
    conf = load_config(cfg)
    assert conf.renderer.mode == "piomatter"


def test_provider_family_config_loads(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
providers:
  stocks:
    enabled: true
    primary: finnhub
    fallback: alphavantage
    symbols: [AAPL, SPY]
    labels:
      SPY: S&P
widgets:
  stocks:
    enabled: true
    refresh_seconds: 60
    ttl_seconds: 180
    retries: 1
    config: {}
pages:
  - page_id: p1
    name: P1
    layout: single_kpi
    widgets: [stocks]
""".strip(),
        encoding="utf-8",
    )
    conf = load_config(cfg)
    assert conf.providers.stocks.primary == "finnhub"
    assert conf.providers.stocks.fallback == "alphavantage"
    assert conf.providers.stocks.symbols == ["AAPL", "SPY"]


def test_widget_run_mode_defaults_to_background_always(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
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
    conf = load_config(cfg)
    assert conf.widgets["clock"].run_mode == "background_always"


def test_widget_run_mode_explicit_page_bound(tmp_path: Path) -> None:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
renderer:
  mode: simulator
widgets:
  clock:
    enabled: true
    run_mode: page_bound
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
    conf = load_config(cfg)
    assert conf.widgets["clock"].run_mode == "page_bound"
