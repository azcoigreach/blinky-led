# Migration Notes: v2 -> v3

## Breaking backend change

v3 no longer treats `rpi-rgb-led-matrix` as the primary backend.
The mainline hardware implementation is Raspberry Pi 5 + Adafruit Piomatter.

Legacy v2 command modules under `blinky/` remain in the repository for reference but are not the v3 runtime path.

## New runtime model

- v2: command-specific fetch/render loops.
- v3: scheduler-driven widgets + page/layout renderer + web/API control plane.

## Configuration changes

- v2 used CLI-heavy runtime options.
- v3 uses `config.yaml` (or `config.example.yaml`) with pydantic validation.
- Secrets moved to `.env` based keys.

## New entrypoint

- v2 default command behavior: old `blinky.commands.*`.
- v3 entrypoint: `blinky` -> `app.cli:cli`.

Examples:

- `blinky run --config config.yaml`
- `blinky serve --config config.yaml --host 0.0.0.0 --port 8080`

## Rendering modes

- `renderer.mode: piomatter` for Pi 5 hardware.
- `renderer.mode: simulator` for local development and CI.
