# Simulator Development

## Requirements

- Python 3.13+
- No physical LED matrix required

## Setup

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp config.example.yaml config.yaml
cp .env.example .env
```

## Run in simulator mode

Set in `config.yaml`:

```yaml
renderer:
  mode: simulator
```

Start runtime + web UI:

```bash
blinky serve --config config.yaml
```

Open:

- http://localhost:8080
- Preview PNG: http://localhost:8080/api/preview

The simulator also writes `.simulator/preview.png` on each frame.

## Run tests

```bash
pytest -q
```
