# Legacy Runtime Retirement

As of v3, this repository no longer ships the legacy `blinky/` command runtime (`blinky.cli` + `blinky.commands.*`).

Reason for retirement:

- v3 replaces the old command-dispatch architecture with a scheduler-driven dashboard runtime under `app/`
- Raspberry Pi 5 + Piomatter is now the primary hardware target
- keeping both runtime paths created packaging and operational ambiguity

Current supported runtime:

- `blinky` console script -> `app.cli:cli`
- `app/` is the only supported application package
