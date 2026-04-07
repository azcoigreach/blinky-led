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
