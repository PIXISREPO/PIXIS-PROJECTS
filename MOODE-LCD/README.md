# PIXIS MOODE-LCD

Waveshare 2.8" SPI LCD display with album art, metadata, and idle screen IP display for moOde Audio Player.

## Features

- **Album Art Display**: 240x240 portrait album art from moOde
- **Metadata**: Artist, album, and track name displayed below art
- **Idle Screen**: Shows hostname and IP address(es) when playback is stopped
- **Radio Paradise Integration**: Uses RP API for rich metadata and cover art
- **Always-On Backlight**: No PWM flicker — uses DigitalOutputDevice

## Requirements

- Raspberry Pi 3A+, 4, or 5
- moOde Audio Player (default install with user `moode`)
- Waveshare 2.8" SPI LCD (ST7789 driver)
- Internet access on the Pi (for Waveshare driver download)

## Installation

SSH into your moOde device, then:

    cd /tmp
    wget -q https://raw.githubusercontent.com/YOUR_GITHUB_USER/PIXISREPO/main/PIXIS-PROJECTS/MOODE-LCD/bootstrap.sh
    wget -q https://raw.githubusercontent.com/YOUR_GITHUB_USER/PIXISREPO/main/PIXIS-PROJECTS/MOODE-LCD/install.sh
    wget -q https://raw.githubusercontent.com/YOUR_GITHUB_USER/PIXISREPO/main/PIXIS-PROJECTS/MOODE-LCD/moode_lcd.py
    chmod +x bootstrap.sh install.sh
    sudo bash bootstrap.sh

The bootstrap will confirm your intent, then hand off to install.sh which:

1. Installs all dependencies (wget, unzip, Python packages)
2. Enables SPI in /boot/firmware/config.txt if not already active
3. Downloads and installs the Waveshare 2.8 driver from the official Waveshare ZIP
4. Copies moode_lcd.py into the Waveshare Python directory
5. Creates and enables the moode-lcd systemd service

If SPI was not previously enabled, reboot when prompted:

    sudo reboot

Then verify:

    ls -la /dev/spidev*
    sudo systemctl status moode-lcd.service

## Troubleshooting

LCD not displaying after reboot:

    sudo systemctl status moode-lcd.service
    sudo journalctl -n 50 -u moode-lcd.service
    ls -la /dev/spidev*

User not in gpio/spi groups:

    sudo usermod -aG gpio,spi moode
    sudo systemctl restart moode-lcd.service

SPI device not found — reboot and check again.

## Service Management

    sudo systemctl start moode-lcd.service
    sudo systemctl stop moode-lcd.service
    sudo systemctl restart moode-lcd.service
    sudo journalctl -u moode-lcd.service -f

## File Locations (after install)

| File | Path |
|---|---|
| LCD Python script | /home/moode/waveshare-2.8/Python/moode_lcd.py |
| Waveshare driver | /home/moode/waveshare-2.8/Python/LCD_2inch8.py |
| Systemd service | /etc/systemd/system/moode-lcd.service |
| SPI config | /boot/firmware/config.txt |
