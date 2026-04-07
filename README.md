# Blinky LED v3.0.1

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
- YAML config + pydantic validation + `.env` secret loading

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

## Docs

- Simulator developer guide: `docs/DEVELOPMENT_SIMULATOR.md`
- Pi 5 deployment guide: `docs/DEPLOY_PI5_PIOMATTER.md`
- Migration notes: `docs/MIGRATION_V3.md`
- Archive notes: `docs/archive/LEGACY_RETIREMENT.md`
- Changelog: `CHANGELOG.md`
