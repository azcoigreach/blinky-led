# Raspberry Pi 5 + Piomatter Deployment

## Target platform

- Raspberry Pi 5
- Adafruit Matrix Bonnet/HAT for Pi 5 (Piomatter stack)
- Python 3.13+
- v3 dashboard runtime (`app/`) only

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

The checked-in unit file is an example only. For a real Pi install, use the installer script so the service points at the current checkout and is enabled on boot.

```bash
chmod +x deploy/systemd/install-service.sh
./deploy/systemd/install-service.sh
```

That will:

- install `/etc/systemd/system/blinky-dashboard.service`
- run `systemctl daemon-reload`
- enable the service for reboot startup
- start it immediately

Useful commands:

```bash
sudo systemctl status blinky-dashboard.service
sudo journalctl -u blinky-dashboard.service -f
sudo systemctl restart blinky-dashboard.service
sudo systemctl disable --now blinky-dashboard.service
```
