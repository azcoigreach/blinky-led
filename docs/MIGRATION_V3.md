# Migration Notes: v2 -> v3

## Breaking backend change

v3 no longer treats `rpi-rgb-led-matrix` as the primary backend.
The mainline hardware implementation is Raspberry Pi 5 + Adafruit Piomatter.

The legacy `blinky/` runtime has been retired and removed from active packaging.

## New runtime model

- v2: command-specific fetch/render loops.
- v3: scheduler-driven widgets + page/layout renderer + web/API control plane.

## Configuration changes

- v2 used CLI-heavy runtime options.
- v3 uses `config.yaml` (or `config.example.yaml`) with pydantic validation.
- Secrets moved to `.env` based keys.

## New entrypoint

- v2 default command behavior: old `blinky.commands.*` (retired).
- v3 entrypoint: `blinky` -> `app.cli:cli` (only supported entrypoint).

Examples:

- `blinky run --config config.yaml`
- `blinky serve --config config.yaml --host 0.0.0.0 --port 8080`

## Rendering modes

- `renderer.mode: piomatter` for Pi 5 hardware.
- `renderer.mode: simulator` for local development and CI.

## Archival note

Legacy runtime modules were removed to avoid a split architecture. See `docs/archive/LEGACY_RETIREMENT.md`.
