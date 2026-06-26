# PIXIS MOODE-LCD
Waveshar 2.8" SPI LCD display with album art, metadata, and idle screen IP display for moOde Audio Player.

## Features

- **Album Art Display**: 240x240 portrait album art from moOde
- **Metadata**: Artist, album, and track name displayed below art
- **Idle Screen**: Shows hostname and IP address(es) when playback is stopped
- **Radio Paradise Integration**: Uses RP API for rich metadata and cover art as an example.
- **Always-On Backlight**: No PWM flicker — uses DigitalOutputDevice
- **Auto-Resume on Boot**: Playback resumes automatically after reboot via `mpd-autoplay.service`
- **Full Moode Controller**: Available via Web Browser to Moode IP address

## Requirements

- Raspberry Pi 3A+, Pi Zero2W, Pi3, Pi4, or Pi5
- moOde Audio Player (default install with user `moode`)
- Waveshare SKU27579 2.8" SPI LCD (ST7789 driver)
- Internet access on the Pi (for Waveshare driver download)
- Optional Audio HATs of your choice.
  
## Installation

SSH into your moOde device, then copy and paste these four commands into your SSH terminal:

```bash
cd /tmp
wget https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/main/MOODE-LCD/bootstrap.sh
chmod +x bootstrap.sh
sudo bash bootstrap.sh
```

Click the copy icon in the top-right of the code block, paste into your SSH terminal, and hit Return.

### Two-Step Install (Inspect Before Installing)

If you want to inspect the files before installing:

```bash
cd /tmp
wget https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/main/MOODE-LCD/bootstrap.sh
chmod +x bootstrap.sh
```

Then review the files:

```bash
cat bootstrap.sh
```

When you're ready to install:

```bash
sudo bash bootstrap.sh
```

The bootstrap will download install.sh, LCD_2inch8.py and moode_lcd.py from GitHub, confirm your intent, then hand off to install.sh which:

1. Installs all dependencies (wget, unzip, Python packages, mpc)
2. Enables SPI in /boot/firmware/config.txt if not already active
3. Downloads and installs the Waveshare 2.8 driver from the official Waveshare ZIP
4. Copies moode_lcd.py into the Waveshare Python directory
5. Creates and enables the `moode-lcd` systemd service
6. Creates and enables the `mpd-autoplay` systemd service for auto-resume on boot

The installer reboots automatically. After reboot the LCD will display
album art and metadata, and playback will resume without any manual input.

## Troubleshooting

LCD not displaying after reboot:

    sudo systemctl status moode-lcd.service
    sudo journalctl -n 50 -u moode-lcd.service
    ls -la /dev/spidev*

User not in gpio/spi groups:

    sudo usermod -aG gpio,spi moode
    sudo systemctl restart moode-lcd.service

SPI device not found — reboot and check again.

Playback not resuming after reboot:

    sudo systemctl status mpd-autoplay.service
    sudo journalctl -u mpd-autoplay.service

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
| LCD systemd service | /etc/systemd/system/moode-lcd.service |
| Auto-resume service | /etc/systemd/system/mpd-autoplay.service |
| SPI config | /boot/firmware/config.txt |
```


