#!/usr/bin/env python3
"""
LCD_2inch8.py  –  ST7789 240×320 SPI driver for Waveshare 2.8inch LCD
Pinout (BCM numbering):
  BL  = 18   (backlight, PWM capable)
  DC  = 25   (data/command)
  RST = 27   (reset)
  CS  = 8    (SPI CE0)
  CLK = 11   (SPI SCLK)
  DIN = 10   (SPI MOSI)
"""

import time
import spidev
import RPi.GPIO as GPIO
from PIL import Image

# GPIO pins (BCM)
_BL  = 18
_DC  = 25
_RST = 27
_CS  = 8

# ST7789 commands
_NOP     = 0x00
_SWRESET = 0x01
_SLPOUT  = 0x11
_NORON   = 0x13
_INVON   = 0x21
_DISPON  = 0x29
_CASET   = 0x2A
_RASET   = 0x2B
_RAMWR   = 0x2C
_MADCTL  = 0x36
_COLMOD  = 0x3A
_PORCTRL = 0xB2
_GCTRL   = 0xB7
_VCOMS   = 0xBB
_LCMCTRL = 0xC0
_VDVVRHEN= 0xC2
_VRHS    = 0xC3
_VDVS    = 0xC4
_FRCTRL2 = 0xC6
_PWCTRL1 = 0xD0
_PVGAMCTRL = 0xE0
_NVGAMCTRL = 0xE1


class LCD_2inch8:
    """240×320 ST7789 display on Waveshare 2.8inch LCD for Raspberry Pi."""

    WIDTH  = 240
    HEIGHT = 320

    def __init__(self, spi_bus=0, spi_device=0, spi_hz=40_000_000):
        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_device)
        self._spi.max_speed_hz = spi_hz
        self._spi.mode = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(_BL,  GPIO.OUT)
        GPIO.setup(_DC,  GPIO.OUT)
        GPIO.setup(_RST, GPIO.OUT)

        # Backlight on
        GPIO.output(_BL, GPIO.HIGH)

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    def _reset(self):
        GPIO.output(_RST, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(_RST, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(_RST, GPIO.HIGH)
        time.sleep(0.05)

    def _write_cmd(self, cmd):
        GPIO.output(_DC, GPIO.LOW)
        self._spi.writebytes([cmd])

    def _write_data(self, data):
        GPIO.output(_DC, GPIO.HIGH)
        if isinstance(data, int):
            self._spi.writebytes([data])
        else:
            # send in 4096-byte chunks to avoid SPI buffer limits
            data = list(data)
            for i in range(0, len(data), 4096):
                self._spi.writebytes(data[i:i + 4096])

    # ------------------------------------------------------------------
    # Initialisation sequence
    # ------------------------------------------------------------------
    def ST7789_Init(self):
        self._reset()

        self._write_cmd(_SWRESET); time.sleep(0.15)
        self._write_cmd(_SLPOUT);  time.sleep(0.05)

        self._write_cmd(_COLMOD);  self._write_data(0x55)   # 16-bit colour

        self._write_cmd(_MADCTL);  self._write_data(0x00)   # portrait, RGB

        self._write_cmd(_PORCTRL)
        self._write_data([0x0C, 0x0C, 0x00, 0x33, 0x33])

        self._write_cmd(_GCTRL);   self._write_data(0x35)

        self._write_cmd(_VCOMS);   self._write_data(0x19)

        self._write_cmd(_LCMCTRL); self._write_data(0x2C)

        self._write_cmd(_VDVVRHEN); self._write_data(0x01)

        self._write_cmd(_VRHS);    self._write_data(0x12)

        self._write_cmd(_VDVS);    self._write_data(0x20)

        self._write_cmd(_FRCTRL2); self._write_data(0x0F)

        self._write_cmd(_PWCTRL1)
        self._write_data([0xA4, 0xA1])

        self._write_cmd(_PVGAMCTRL)
        self._write_data([0xD0,0x04,0x0D,0x11,0x13,0x2B,0x3F,
                          0x54,0x4C,0x18,0x0D,0x0B,0x1F,0x23])

        self._write_cmd(_NVGAMCTRL)
        self._write_data([0xD0,0x04,0x0C,0x11,0x13,0x2C,0x3F,
                          0x44,0x51,0x2F,0x1F,0x1F,0x20,0x23])

        self._write_cmd(_INVON)
        self._write_cmd(_NORON)
        self._write_cmd(_DISPON)
        time.sleep(0.05)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def _set_window(self, x0=0, y0=0, x1=None, y1=None):
        x1 = (self.WIDTH  - 1) if x1 is None else x1
        y1 = (self.HEIGHT - 1) if y1 is None else y1
        self._write_cmd(_CASET)
        self._write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self._write_cmd(_RASET)
        self._write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self._write_cmd(_RAMWR)

    def ShowImage(self, image: Image.Image):
        """Send a PIL Image (any mode) to the display."""
        img = image.convert('RGB')
        if img.size != (self.WIDTH, self.HEIGHT):
            img = img.resize((self.WIDTH, self.HEIGHT))

        # Convert RGB888 → RGB565
        pixels = []
        for r, g, b in img.getdata():
            colour = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            pixels.append(colour >> 8)
            pixels.append(colour & 0xFF)

        self._set_window()
        self._write_data(pixels)

    def clear(self, colour=(0, 0, 0)):
        """Fill the display with a solid colour (default: black)."""
        img = Image.new('RGB', (self.WIDTH, self.HEIGHT), colour)
        self.ShowImage(img)

    def backlight(self, on: bool):
        """Turn backlight on or off."""
        GPIO.output(_BL, GPIO.HIGH if on else GPIO.LOW)

    def close(self):
        self._spi.close()
        GPIO.cleanup()
