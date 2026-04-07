# Changelog

## 3.0.1 - 2026-04-06

- Finalized packaging migration to `pyproject.toml` and removed legacy `setup.py`.
- Retired legacy `blinky/` runtime path so `app/` is the only supported runtime package.
- Updated deployment and migration docs to reflect the v3-only architecture.

## 3.0.0 - 2026-04-06

- Re-architected project as a modular dashboard platform under `app/`.
- Primary hardware target changed to Raspberry Pi 5 + Adafruit Piomatter backend.
- Added renderer abstraction with `PiomatterRenderer` and first-class `SimulatorRenderer`.
- Added FastAPI web interface and REST API (`/api/status`, `/api/widgets`, `/api/pages`, `/api/config`, `/api/preview`, `/api/override`, `/api/brightness`, `/api/schedule`, `/api/pin-page`, `/api/reload`).
- Added widget plugin framework and starter widgets: `clock`, `weather`, `stocks`, `crypto`, `gas`, `news`, `poll`, `system`, `custom_text`.
- Added async scheduler with widget refresh intervals, retries, stale markers, and TTL cache.
- Added page layout engine with templates: `single_kpi`, `two_column`, `ticker_only`, `split_banner`, `alert_fullscreen`.
- Added YAML config + pydantic validation and `.env` secret loading.
- Added simulator-friendly tests for config, cache, widgets, rotation, API, and rendering.
- Raised minimum Python version to 3.13.

## 2.x

- Legacy implementation built around `rpi-rgb-led-matrix` assumptions.
