#!/usr/bin/env bash
export DISPLAY=1:0
xset -dpms s off s noblank &
exec matchbox-window-manager &
while true; do
  python3 /home/pi/blinky-led/app/touch_gui.py
done