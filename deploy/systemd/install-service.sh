#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="blinky-dashboard"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CONFIG_PATH="$REPO_DIR/config.yaml"
ENV_PATH="$REPO_DIR/.env"
BLINKY_BIN="$REPO_DIR/.venv/bin/blinky"
HOST="0.0.0.0"
PORT="8080"
LOG_LEVEL="INFO"
START_NOW=1

while [[ $# -gt 0 ]]; do
    case "$1" in
        --service-name)
            SERVICE_NAME="$2"
            shift 2
            ;;
        --repo-dir)
            REPO_DIR="$2"
            CONFIG_PATH="$REPO_DIR/config.yaml"
            ENV_PATH="$REPO_DIR/.env"
            BLINKY_BIN="$REPO_DIR/.venv/bin/blinky"
            shift 2
            ;;
        --config)
            CONFIG_PATH="$2"
            shift 2
            ;;
        --env-file)
            ENV_PATH="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift 2
            ;;
        --enable-only)
            START_NOW=0
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

if [[ ! -x "$BLINKY_BIN" ]]; then
    echo "Missing executable: $BLINKY_BIN" >&2
    echo "Create the venv and install the project first." >&2
    exit 1
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
    echo "Missing config file: $CONFIG_PATH" >&2
    exit 1
fi

TMP_UNIT="$(mktemp)"
cleanup() {
    rm -f "$TMP_UNIT"
}
trap cleanup EXIT

cat > "$TMP_UNIT" <<EOF
[Unit]
Description=Blinky LED Dashboard v3
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$REPO_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$BLINKY_BIN serve --config $CONFIG_PATH --env-file $ENV_PATH --log-level $LOG_LEVEL --host $HOST --port $PORT
Restart=always
RestartSec=2
KillSignal=SIGINT
TimeoutStopSec=15

[Install]
WantedBy=multi-user.target
EOF

sudo install -m 0644 "$TMP_UNIT" "/etc/systemd/system/${SERVICE_NAME}.service"
sudo systemctl daemon-reload

if [[ "$START_NOW" -eq 1 ]]; then
    sudo systemctl enable --now "${SERVICE_NAME}.service"
else
    sudo systemctl enable "${SERVICE_NAME}.service"
fi

sudo systemctl status "${SERVICE_NAME}.service" --no-pager || true
