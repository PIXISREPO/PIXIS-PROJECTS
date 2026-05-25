#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
CST328 capacitive touch driver for Waveshare 2.8\" LCD.
Exports touch events as a Linux uinput device.
Assumes you have:
  - Touch_2inch8.CST328_init()
  - touch_data coords available in 240x320.
"""

import time
import signal
import functools

import uinput

# Import your Waveshare modules (same path as on the Pi)
import LCD_2inch8
import Touch_2inch8
from Touch_2inch8 import touch_data, Touch_Data_Old


# Virtual touch device; 240x320 area
TOUCH_DEV = uinput.Device(
    [
        uinput.REL_X,
        uinput.REL_Y,
        uinput.ABS_X + (0, 239, 0, 0),  # 240 px wide
        uinput.ABS_Y + (0, 319, 0, 0),  # 320 px high
        uinput.BTN_TOUCH,
    ],
    name="VOLUMIO‑LCD‑TOUCH CST328",
)


def main():
    # Same setup as in your 2inch8_LCD_test.py
    touch = Touch_2inch8.Touch_2inch8()
    touch.CST328_init()

    disp = LCD_2inch8.LCD_2inch8()
    disp.ST7789_Init()
    # disp.clear()  # your volumio‑lcd.service already drives the screen

    print("Touch bridge running; press Ctrl+C to stop.")
    last_x = -1
    last_y = -1

    try:
        while True:
            if touch_data.state:
                touch_data.state = 0

                if touch_data.points > 0:
                    # Only use single‑touch point 0
                    x = touch_data.coords[0]["x"]
                    y = touch_data.coords[0]["y"]

                    if last_x != x or last_y != y:
                        TOUCH_DEV.emit(uinput.ABS_X, x)
                        TOUCH_DEV.emit(uinput.ABS_Y, y)
                        TOUCH_DEV.emit(uinput.BTN_TOUCH, 1)
                        TOUCH_DEV.syn()

                    last_x, last_y = x, y

                else:
                    # Lift‑up
                    TOUCH_DEV.emit(uinput.BTN_TOUCH, 0)
                    TOUCH_DEV.syn()
                    last_x = last_y = -1

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Stopping touch bridge.")
    finally:
        TOUCH_DEV.destroy()
        disp.LCD_module_exit()


if __name__ == "__main__":
    main()


