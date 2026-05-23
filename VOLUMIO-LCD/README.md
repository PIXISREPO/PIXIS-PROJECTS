# Volumio LCD Album Art Display

A fully automated installer and runtime for a Waveshare 2.8" SPI LCD on Volumio 3. The screen shows album art and playback metadata from the currently selected Volumio music source.

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

This project installs the files needed to run a Waveshare 2.8" SPI LCD on a fresh Volumio 3 image. The display shows album art plus track metadata in a simple always-on layout. The installer is designed to run unattended and to complete all steps it can without user intervention.

## Requirements

### What the repo provides

These files come from the GitHub repository and are fetched by `bootstrap.sh`:

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

These items must be present on the Volumio image itself or installed during the first-run bootstrap:

- SPI enabled in `/boot/userconfig.txt`.
- `dtoverlay=spi-spidev` in `/boot/userconfig.txt`.
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
- `dtparam=spi=on` and `dtoverlay=spi-spidev` expose the SPI device node that the screen needs.

## Install flow

The installer runs automatically on a fresh Volumio 3 image:

1. `bootstrap.sh` stages the install payload.
2. `install.sh` copies the application files into place.
3. `install.sh` writes the required SPI boot settings.
4. `install.sh` installs the Python dependencies.
5. `install.sh` checks for `/dev/spidev0.0`.
6. If the device node is present, `volumio-lcd.service` is enabled and started.
7. If the device node is not yet present, the installer finishes its work, marks that a reboot is required, and exits cleanly.

Example bootstrap command:

```bash
PIXIS_BASE_URL=https://raw.githubusercontent.com/<owner>/<repo>/main bash bootstrap.sh
```

## Boot config

For a virgin Volumio 3 image, the installer writes the boot config directly. The target `/boot/userconfig.txt` should contain:

```text
dtparam=spi=on
dtoverlay=spi-spidev
```

These lines are required so the kernel exposes `/dev/spidev0.0`, which the Waveshare driver needs.

## Runtime packages

The installer installs the Python packages that the Waveshare driver imports:

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

Useful checks:

```bash
systemctl status volumio-lcd.service --no-pager -l
journalctl -u volumio-lcd.service -n 50 --no-pager
ls -l /dev/spidev*
```

A healthy system should show the service active and the display in its waiting-for-playback state.

## Security

This project is designed for a trusted-network installation workflow on a fresh Volumio 3 image. The installer pulls its files directly from the GitHub repository during bootstrap, so the installation source is the published repo itself.

### Immutable files

The installer and runtime assets are treated as immutable source artifacts in the repository. The Volumio target consumes them as delivered, and the installer does not modify the repository itself.

### What is and is not mutable

- Mutable on the Volumio target: `/boot/userconfig.txt`, service enablement state, installed packages, and runtime logs.
- Immutable from the repo side: `bootstrap.sh`, `install.sh`, systemd units, Python source, and the packaged assets fetched during bootstrap.

### Practical guidance

Keep the source files in GitHub as the single source of truth. The Volumio target should only receive the staged files and the runtime changes needed to complete installation.

## Troubleshooting

The installer should complete without prompting for manual recovery. If it cannot finish, it should report the reason clearly and stop.

Typical reasons an install can fail:

- The GitHub files could not be fetched.
- A required package could not be installed.
- The boot config could not be written.
- `/dev/spidev0.0` did not appear after the boot config was applied.
- The service failed to start after installation.

If the installer reports failure, the message should include the reason and any known next step.

If the Python script fails immediately, run it manually to expose the exact traceback:

```bash
python3 /home/volumio/waveshare-2.8/Python/volumio_lcd.py
```

## Developer notes

This repo is intended for a clean-image workflow. The installer handles SPI setup early, before enabling the LCD service. That keeps the hardware prerequisite ahead of the runtime service start, which avoids the import and device-node failures seen on the test rig.

