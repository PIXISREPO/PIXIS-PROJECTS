# MOODE-LCD Setup Guide

## Overview

This guide covers the full setup of the PIXIS Moode LCD display on a
Waveshare 2.8inch SPI LCD connected to a Raspberry Pi running Moode Audio.

---

## Hardware Required

- Raspberry Pi (any model with 40-pin GPIO)
- Waveshare 2.8inch LCD for Raspberry Pi (SPI interface)
- MicroSD with Moode Audio installed

---

## Wiring

The Waveshare 2.8inch LCD connects via the full 40-pin GPIO header.

| Function | GPIO (BCM) | Physical Pin |
|----------|------------|--------------|
| SPI MOSI | GPIO 10    | Pin 19       |
| SPI SCLK | GPIO 11    | Pin 23       |
| SPI CE0  | GPIO 8     | Pin 24       |
| DC       | GPIO 25    | Pin 22       |
| RST      | GPIO 27    | Pin 13       |
| BL       | GPIO 18    | Pin 12       |

---

## Installation

### 1. Copy files to the Pi

From your Mac:

    scp -r /Users/peter/Documents/PIXISREPO/PIXIS-PROJECTS/MOODE-LCD/ moode@moode.local:/home/moode/moode-lcd-install/

### 2. SSH into Moode

    ssh moode@moode.local

### 3. Run the installer

    cd /home/moode/moode-lcd-install
    sudo bash install.sh

The installer will:
- Install Python dependencies (including `mpc`)
- Enable SPI in /boot/firmware/config.txt if not already enabled
- Download and install the Waveshare 2.8 Python driver
- Copy moode_lcd.py to the driver directory
- Create and enable the `moode-lcd.service` systemd service
- Create and enable the `mpd-autoplay.service` for auto-resume on boot

### 4. Reboot when prompted

The installer reboots automatically after 10 seconds. After reboot:

- The LCD will display album art and metadata immediately
- Playback will resume automatically — no manual Play tap required

---

## Auto-Resume on Boot

By default, MPD boots into a paused state even though it saves its playlist
and position on shutdown. The installer creates a small systemd service
(`mpd-autoplay.service`) that fires `mpc play` 5 seconds after MPD starts,
so playback resumes automatically every time the Pi reboots.

This works for both local files and live radio streams. MPD saves the stream
URL across reboots and reconnects automatically.

To verify the service is running:

    sudo systemctl status mpd-autoplay.service

---

## Verifying the Installation

    sudo systemctl status moode-lcd.service
    sudo systemctl status mpd-autoplay.service
    sudo journalctl -u moode-lcd.service -f
    ls -la /dev/spidev*

---

## What the Display Shows

1. Now Playing - track title, artist, album art (from Moode API)
2. Playback status - play/pause state, elapsed time, volume
3. Network info - IP address, hostname, WiFi SSID

Refreshes every 2 seconds when playing, every 10 seconds when idle.

---

## Troubleshooting

Display blank/white:
- Check SPI: ls /dev/spidev*
- Check GPIO wiring
- Check logs: sudo journalctl -u moode-lcd.service -f

No module named spidev:
    sudo pip3 install --break-system-packages spidev

No module named LCD_2inch8:
Re-run install.sh or manually copy Waveshare Python files to
/home/moode/waveshare-2.8/Python/

Service runs but wrong data shown:
- Check Moode API: curl http://localhost/command/?cmd=currentsong
- Check MOODE_API_URL at top of moode_lcd.py

Permission denied on /dev/spidev0.0:
    sudo usermod -aG spi moode
    sudo reboot

Playback not resuming after reboot:
    sudo systemctl status mpd-autoplay.service
    sudo journalctl -u mpd-autoplay.service

---

## Uninstalling

    sudo systemctl stop moode-lcd.service
    sudo systemctl disable moode-lcd.service
    sudo rm /etc/systemd/system/moode-lcd.service
    sudo systemctl stop mpd-autoplay.service
    sudo systemctl disable mpd-autoplay.service
    sudo rm /etc/systemd/system/mpd-autoplay.service
    sudo systemctl daemon-reload
    rm -rf /home/moode/waveshare-2.8
