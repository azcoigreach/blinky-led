# Blinky LED v3.1.0

Blinky v3 is a modular LED information dashboard platform for 128x32 HUB75 panels.

Primary target:

- Raspberry Pi 5
- Adafruit Piomatter backend (`adafruit-blinka-raspberry-pi5-piomatter`)
- Python 3.13+

The legacy `blinky/` command runtime has been retired. The only supported runtime is `app/` (v3 dashboard).

## Features

- FastAPI web control UI + REST API
- Piomatter renderer for Pi 5 hardware
- First-class simulator renderer (hardware-free local development)
- Widget/plugin system with background scheduling and TTL caching
- Page rotation with pinning and compact 128x32 layout templates
- Operational web controls for active/pinned page management and widget health/freshness monitoring
- YAML config + pydantic validation + `.env` secret loading
- Widget health lifecycle with retries, fallback, and debuggable status metadata
- Provider architecture for external-source widgets (`news`, `crypto`, `stocks/futures`, `poll`, `gas`)

Starter widgets:

- `clock`
- `weather`
- `stocks`
- `crypto`
- `gas`
- `news`
- `poll`
- `system`
- `custom_text`

## Architecture

```
app/
  core/       # config, models, scheduler, cache, logging, settings
  providers/  # provider interfaces + concrete source adapters + fixture/manual providers
  widgets/    # widget interface + starter widgets
  render/     # renderer abstraction + piomatter/simulator + layout engine
  web/        # FastAPI app, routes, templates, static
  services/   # fetch helpers and transforms
  pages/      # page definition and rotation control
```

## Packaging And Entrypoint

- Distribution package: `blinky-led`
- Python runtime package: `app`
- Console entrypoint: `blinky` -> `app.cli:cli`
- Build metadata source of truth: `pyproject.toml`

No legacy `blinky.commands.*` runtime path is supported.

## Quick start (simulator)

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp config.example.yaml config.yaml
cp .env.example .env
blinky serve --config config.yaml
```

Open http://localhost:8080.

## Quick start (Pi 5 + Piomatter)

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .[pi5]
cp config.example.yaml config.yaml
cp .env.example .env
```

Set `renderer.mode: piomatter` in `config.yaml`, then run:

```bash
sudo .venv/bin/blinky serve --config config.yaml --host 0.0.0.0 --port 8080
```

## Run On Reboot (Pi 5)

Install and enable the systemd service:

```bash
chmod +x deploy/systemd/install-service.sh
./deploy/systemd/install-service.sh
```

Check service state:

```bash
sudo systemctl status blinky-dashboard.service
sudo journalctl -u blinky-dashboard.service -f
```

## REST API

- `GET /api/status`
- `GET /api/widgets`
- `GET /api/pages`
- `GET /api/config`
- `GET /api/preview`
- `GET /api/schedule`
- `POST /api/override`
- `POST /api/brightness`
- `POST /api/pin-page`
- `POST /api/reload`

`/api/status` and `/api/widgets` are designed for lightweight frontend polling and now expose enough information to drive operational controls and health/freshness state in the web UI.

## Provider Architecture

External-source widgets use provider classes selected by widget config (`widgets.<name>.config.provider`). Widgets are responsible for panel presentation and fallback behavior, while providers own source-specific API/RSS logic and normalization.

Provider families:

- News: `fixture`, `rss`, `newsapi`
- Crypto: `binance`, `coingecko`, `fixture`
- Stocks/Futures: `fixture`, `marketdata` (adapter-ready)
- Poll: `fixture`, `external` (adapter-ready)
- Gas: `fixture`, `manual`, `aaa` (adapter-ready)

This keeps widget code extensible and avoids source-specific HTTP logic leaking into display components.

## Web UI Controls

The default FastAPI/Jinja UI includes practical operations for runtime control:

- pin selected page
- unpin current page
- active vs pinned page display and highlighting
- auto-refresh loop for status, preview, and widget health panel
- widget health table with source, freshness, fallback, and last success/failure visibility

## Widget Runtime Model

Widgets run with a shared lifecycle contract:

- `fetch_primary()` for normal data acquisition
- centralized retry policy (`retries` + `retry_backoff_seconds`)
- explicit fallback policy (`last_known_or_synthetic`, `last_known`, `synthetic`)
- operational status tracking in `/api/widgets` (attempts, last success/failure, consecutive failures, fallback state)

Each widget payload exposes normalized operational fields:

- freshness (`fresh`, `stale`, `fallback`, `error`)
- data origin (`primary`, `cache`, `fallback`, `synthetic`)
- health state (`healthy`, `degraded`, `failed`)
- status summary and debug metadata

This keeps the panel readable while making degraded and failed states visible in API/debug output.

## Docs

- Simulator developer guide: `docs/DEVELOPMENT_SIMULATOR.md`
- Pi 5 deployment guide: `docs/DEPLOY_PI5_PIOMATTER.md`
- Migration notes: `docs/MIGRATION_V3.md`
- Archive notes: `docs/archive/LEGACY_RETIREMENT.md`
- Changelog: `CHANGELOG.md`
