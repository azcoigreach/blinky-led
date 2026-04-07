# Changelog

## 3.0.3 - 2026-04-06

- Added provider architecture under `app/providers/` for `news`, `crypto`, `stocks/futures`, `poll`, and `gas` with fixture/manual and adapter-ready external providers.
- Refactored external-source widgets to consume provider objects instead of embedding source-specific HTTP logic in widget classes.
- Upgraded web control UI with pin selected page, unpin current page, active/pinned page visibility, and auto-refresh polling for status and preview.
- Added operational widget health table in UI with health/freshness badges, source labels, fallback state, and last success/failure timestamps.
- Expanded tests for pin/unpin API flow, provider selection behavior, provider normalization, and widget/provider integration.

## 3.0.2 - 2026-04-06

- Hardened the widget runtime around a shared lifecycle with centralized retry, fallback, and status tracking.
- Expanded normalized widget data and status models so degraded, stale, fallback, and failed states are explicit in API output.
- Upgraded local `clock` and `system` widgets with richer configuration, structured metadata, and robust degraded behavior.
- Added targeted tests for retry handling, stale last-known-good serving, synthetic fallback output, and scheduler/widget integration.

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
