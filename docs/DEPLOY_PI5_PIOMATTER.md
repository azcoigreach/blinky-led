# Raspberry Pi 5 + Piomatter Deployment

## Target platform

- Raspberry Pi 5
- Adafruit Matrix Bonnet/HAT for Pi 5 (Piomatter stack)
- Python 3.13+

## Install

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .[pi5]
cp config.example.yaml config.yaml
cp .env.example .env
```

Set in `config.yaml`:

```yaml
renderer:
  mode: piomatter
  hardware_mapping: adafruit-hat
  n_addr_lines: 4
```

## Start manually

```bash
sudo .venv/bin/blinky serve --config config.yaml --host 0.0.0.0 --port 8080
```

Root privileges are typically required for GPIO access.

## systemd unit

Use [deploy/systemd/blinky-dashboard.service](../deploy/systemd/blinky-dashboard.service) as a base and adjust user/group/paths.
