# Clock Launch Instructions for Pi 5 + Adafruit HAT

## Prerequisites
- Pi 5 running current OS
- Adafruit RGB Matrix HAT installed
- 128x32 LED matrix wired to HAT
- Virtual environment at `.venv/` with dependencies installed
- `/dev/pio0` accessible (already set to `gpio` group on this system)

## Launch Command — Adafruit PioMatter Backend (recommended for Pi 5)

### 2×64×32 Panel Setup
```bash
cd /home/azcoigreach/repos/blinky-led
sudo .venv/bin/blinky --rows 32 --cols 64 --chain_length 2 --hardware_mapping adafruit-hat-pwm --backend piomatter clock
```

### 4×32×32 Panel Setup (if four 32×32 panels chained)
```bash
sudo .venv/bin/blinky --rows 32 --cols 32 --chain_length 4 --hardware_mapping adafruit-hat-pwm --backend piomatter clock
```

## Legacy: rgbmatrix Backend (patched hzeller library, Pi 5 patch applied)

```bash
sudo .venv/bin/blinky --rows 32 --cols 64 --chain_length 2 --hardware_mapping adafruit-hat-pwm --gpio_slowdown 2 --backend rgbmatrix clock
```

## Parameters Explained

| Flag | Purpose | Value |
|------|---------|-------|
| `--rows` | Panel height | `32` |
| `--cols` | Columns per panel | `64` (2×64×32) or `32` (4×32×32) |
| `--chain_length` | Number of panels daisy-chained | `2` or `4` |
| `--hardware_mapping` | HAT pinout type | `adafruit-hat-pwm` |
| `--backend` | Driver library to use | `piomatter` (Pi 5) or `rgbmatrix` (patched) |
| `--n_addr_lines` | [piomatter only] Address lines | `4` for 32-row panels |
| `--gpio_slowdown` | [rgbmatrix only] GPIO timing | `2` for Pi 5 |

## To Stop
Press `Ctrl+C` in the terminal.

## Troubleshooting

### Blank/Garbled Display (piomatter)
Try toggling `--n_addr_lines` between `4` (default) and `5` — some 32-row panels use 5 address lines:
```bash
sudo .venv/bin/blinky --rows 32 --cols 64 --chain_length 2 --hardware_mapping adafruit-hat-pwm --backend piomatter --n_addr_lines 5 clock
```

### Blank/Garbled Display (rgbmatrix legacy)
Try increasing `--gpio_slowdown` to `3` or `4`:
```bash
sudo .venv/bin/blinky --rows 32 --cols 64 --chain_length 2 --hardware_mapping adafruit-hat-pwm --gpio_slowdown 3 --backend rgbmatrix clock
```

### Incorrect Geometry
Verify your panel arrangement and adjust `--cols` and `--chain_length` accordingly.

### Permission Denied on /dev/pio0
Make sure your user is in the `gpio` group and run with `sudo`:
```bash
sudo usermod -aG gpio $USER
```

## Code Changes Made (2026-04-06)

### Clock Command Fixes (`blinky/commands/cmd_clock.py`)
- Fixed font path resolution (was hardcoded to `/home/pi/`, now package-relative)
- **Fixed display overflow**: Changed from 10x20 font (20px, exceeds 32px display) to 9x15 fonts positioned at Y=1 (date) and Y=16 (time)
- Removed unused 10x20 font and cleaned up imports
- Clock now renders correctly on 128×32 matrix

### CLI Enhancements (`blinky/cli.py`)
- Added `--cols` option (default 32) to support configurable panel widths (32 or 64 columns)
- Proper configuration for 2× 64×32 or 4× 32×32 panel geometries

### Packaging (`setup.py`)
- Added media packages (fonts, images) to distribution
- Added missing runtime dependencies: Pillow, requests

### Pi 5 Official Support: Adafruit PioMatter Backend (`blinky/cli.py`)
- Added `PiomatterMatrix` wrapper class providing same interface (`SetImage`, `width`, `height`) as hzeller RGBMatrix
- Added `--backend [rgbmatrix|piomatter]` CLI option (default: `piomatter`)
- Added `--n_addr_lines` option for piomatter geometry (default: 4)
- PioMatter uses Pi 5's RP1 PIO coprocessor via `/dev/pio0` — no mmap/peripheral address issues
- Installed `Adafruit-Blinka-Raspberry-Pi5-Piomatter==1.0.0` and `numpy` in `.venv`

### Result
- Clock displays correctly on Pi 5 + Adafruit HAT + 128×32 matrix
- No mmap or peripheral address errors
- Hardware verified working: `PioMatter initialized OK, 128x32 with AdafruitMatrixHat`
