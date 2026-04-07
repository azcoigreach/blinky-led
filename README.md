## Blinky LED v2 [WIP]

* Requires:
Matrix Driver - https://github.com/hzeller/rpi-rgb-led-matrix

* **Pi 5 Support:**
  - **Option 1 (This Project)**: Patched hzeller library for Pi 5
    - Uses Pi 4 peripheral address mapping (0xfe000000) which is compatible with Pi 5's GPIO
    - Added Pi 5 revision detection (code 0x17, CM5 code 0x18)
    - Works with single channel Adafruit HAT/Bonnet setups
    - See issue: https://github.com/hzeller/rpi-rgb-led-matrix/issues/1603
  
  - **Option 2 (Official Adafruit Solution)**: Use Adafruit's PioMatter library
    - Separate standalone driver using RP1 PIO interface
    - Supports both single and 3-channel output
    - Repository: https://github.com/adafruit/Adafruit_Blinka_Raspberry_Pi5_Piomatter
    - Guide: https://learn.adafruit.com/adafruit-triple-led-matrix-bonnet-for-raspberry-pi-with-hub75/raspberry-pi-5-setup

* Usage:
```
$ pip3 install --editable .
$ blinky --help
```

* Running the clock on Pi 5 (piomatter backend — recommended):
```
sudo .venv/bin/blinky --rows 32 --cols 64 --chain_length 2 --hardware_mapping adafruit-hat-pwm --backend piomatter clock
```
