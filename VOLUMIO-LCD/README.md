# Volumio LCD Album Art Display

A fully automated installer and runtime for a Waveshare 2.8" SPI LCD, SKU 27579 on Volumio 3. The display shows album art and playback metadata from the currently selected Volumio music source. This build is for Volumio 3 based on Debian Buster (10). A release for Volumio 4 Debian Bookworm (12) is in the pipeline and will be released here soon. Do not attempt to install this Buster version on Volumio 4 - it will fail.  

You can download the latest Volumio 3 Raspberry Pi image from the Volumio 3.x download links thread on the Volumio community forum - using the link below - then use this VOLUMIO‑LCD installer to overlay the LCD stack on top of this Volumio image.”

'''bash
https://updates.volumio.org/pi/volumio/3.905/Volumio-3.905-2026-01-28-pi.zip
'''

Burn this to a micro SD card and use it to boot your Raspberry Pi.

The Volumio instance will broadcast a Hotspot SSID 'Volumio xxxx'. Connect your device (Phone, Laptop, Desktop) to that Hotspot and open a browser at volumio.local. 

Follow the simple instructions to reconnect your Pi to your home wifi network, save and reboot the Pi. The Pi should now automatically connect to your home network. Change your device wifi from the Volumio Hotspot back to your home network wifi so that your device and the Pi are on the same network. Revisit volumio.local on your device and follow the on screen instructions to complete the first time Volumio setup. If you have connected a Monitor to your Pi you can use HDMI as the Audio out. If not then use Headphone as your Audio out.

A useful short Youtube explainer is here. 

https://www.youtube.com/watch?v=0KZs--x1uPY

Install the Radio Paradise Plugin on your Pi and check you can stream Audio to your Audio out device. 

The next step requires a command line instruction to your Pi. If you have connected a Monitor and keyboard to your Pi then you can log in using user volumio with password volumio and then proceed from there. If you do not have a Monitor and Keyboard connected to your Pi you will need to ssh into your instance of Volumio from another device on your home network. Go to volumio.local/dev on your device browser and ENABLE ssh. You can then remote in from a terminal on your device using 

ssh volumio@volumio.local 
with password volumio.

From the command line on your Monitor or from the ssh session on a terminal on your device ping google.com to check that the Pi has an Internet connection. Once confirmed you may start the VOLUMIO-LCD installation on your Pi from the command line on your Monitor or your device terminal.

To install the Volumio LCD package on your Pi, run the wget command below. This will download the bootstrap and installer files from the PIXIS Github repo, stage them on the Volumio system and then if the bootstrap download completed successfully it will launch the installer. The installer will prompt for the Volumio password (volumio) when it reaches the privileged system changes, which is normal.

```bash
wget -qO- https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/main/VOLUMIO-LCD/bootstrap.sh | bash -x && sudo /tmp/pixis/stage/VOLUMIO-LCD/install.sh
```

A successful installation will complete with a message on the LCD.

Volumio LCD
Waiting for Playback

Go to http://Pi-IP-address in the browser on your device. This is your Volumio 'Controller' and from it you can navigate the Volumio User Interface and select your preferred music source. You can also install the Volumio App on your smart phone and 'Control' the Pi Player from your phone App.

A full description of what the wget command does is below.


## Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Install flow](#install-flow)
- [Boot config](#boot-config)
- [Runtime packages](#runtime-packages)
- [Service](#service)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Developer notes](#developer-notes)

## Overview

This project installs the files needed to run a Waveshare 2.8" SPI LCD on a fresh Volumio 3 image. The display shows album art and related metadata in a simple always-on layout. The installer is designed to run unattended and complete all supported setup steps without user intervention.

## Requirements

### What the repo provides

The following files are fetched by `bootstrap.sh` from the PIXISREPO GitHub repository and used to install and run the display stack:

- `bootstrap.sh`
- `install.sh`
- `systemd/pixis-installer.service`
- `systemd/volumio-lcd.service`
- `scripts/pixis-installer.sh`
- `scripts/PiInstaller.sh`
- `waveshare-2.8/Python/*`
- `config/userconfig.txt`
- `config/volumioconfig.txt`
- `README.md`

### What the Volumio image needs

These items must already exist on the Volumio image or will be installed during the first-run bootstrap:

- SPI enabled in `/boot/userconfig.txt`
- `dtoverlay=spi-spidev` in `/boot/userconfig.txt`
- Python runtime packages:
  - `python3-pil`
  - `python3-spidev`
  - `python3-numpy`
  - `python3-gpiozero`

### Why these are needed

- `python3-pil` provides the `PIL` import used by the display code.
- `python3-spidev` provides access to `/dev/spidev0.0`.
- `python3-numpy` is imported by the Waveshare driver.
- `python3-gpiozero` is imported by the LCD driver.
- `dtparam=spi=on` and `dtoverlay=spi-spidev` expose the SPI device node required by the screen.

## Install flow

The installer runs automatically on a fresh Volumio 3 image:

1. `bootstrap.sh` downloads the required files from the PIXISREPO GitHub repository and then hands off to install.sh
2. `install.sh` copies the application files into place.
3. `install.sh` writes the required SPI boot settings.
4. `install.sh` installs the Python dependencies.
5. `install.sh` checks for `/dev/spidev0.0`.
6. If the device node is present, `volumio-lcd.service` is enabled and started.
7. If the device node is not yet present, the installer completes its work, marks that a reboot is required, and exits cleanly.

The bootstrap command should you wish to review it is 

```bash
bash bootstrap.sh
```

## Boot config

For a fresh Volumio 3 image, the installer writes the boot configuration directly. The target `/boot/userconfig.txt` will contain:

```text
dtparam=spi=on
dtoverlay=spi-spidev
```

These lines are required so the kernel exposes `/dev/spidev0.0`, which the Waveshare driver needs.

## Runtime packages

The installer installs the Python packages imported by the Waveshare driver and the display runtime:

- `python3-pil`
- `python3-spidev`
- `python3-numpy`
- `python3-gpiozero`

These packages cover the import chain used by `volumio_lcd.py` and `LCD_2inch8.py`.

## Service

The main service is `volumio-lcd.service`, which runs:

```text
/home/volumio/waveshare-2.8/Python/volumio_lcd.py
```

Should you need them here are some useful checks:

```bash
systemctl status volumio-lcd.service --no-pager -l
journalctl -u volumio-lcd.service -n 50 --no-pager
ls -l /dev/spidev*
```

A healthy system will show the service active and the display in its 'VOLUMIO LCD Waiting-for-playback' state.

## Security

This project is designed for a trusted-network installation workflow on a fresh Volumio 3 image. The installer pulls all required files from the PIXISREPO GitHub repository during bootstrap, and that repository is the single source of truth for installer and runtime assets.

### Immutable files

The installer and runtime assets are treated as immutable source artifacts in the repository. The Volumio target consumes them as delivered, and the installer does not modify the repository itself.

### What is and is not mutable

- Mutable on the Volumio target: `/boot/userconfig.txt`, service enablement state, installed packages, and runtime logs.
- Immutable from the repo side: `bootstrap.sh`, `install.sh`, systemd units, Python source, and the packaged assets fetched during bootstrap.

### Practical guidance

The source files in the PIXISREPO GitHub repository are the single source of truth. The Volumio target should only receive the staged files and the runtime changes needed to complete installation.

## Troubleshooting

The installer should complete without prompting for manual recovery. If it cannot finish, it should report the reason clearly and stop.

Typical reasons an install can fail:

- The required files could not be fetched from the PIXISREPO GitHub repository.
- A required package could not be installed.
- The boot config could not be written.
- `/dev/spidev0.0` did not appear after the boot config was applied.
- The service failed to start after installation.

If the installer reports failure, the message should include the reason and any known fix or next step.

If the Python script fails immediately, run it manually to expose the exact traceback:

```bash
python3 /home/volumio/waveshare-2.8/Python/volumio_lcd.py
```

## Developer notes

This repo is intended for a clean-image workflow. The installer handles SPI setup early, before enabling the LCD service. That keeps the hardware prerequisite ahead of runtime service startup which should avoid any import and device-node failures. Should you experience problems please post an 'Issue'.

