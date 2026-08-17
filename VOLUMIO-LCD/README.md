# PIXIS Volumio LCD Album Art Display

**Current release: VOLUMIO-LCD v1.0.0**

A PIXIS installer and runtime for the Waveshare 2.8" SPI LCD (SKU 27579) running with Volumio 3.

The display provides an appliance-style front panel showing album art and playback metadata from the currently selected Volumio music source.

> **VOLUMIO-LCD v1.0.0 — verified 17 August 2026**
>
> Tested with **Volumio 3.905** and the Waveshare 2.8" SPI LCD.
>
> Verified end-to-end:
>
> - clean Volumio 3.905 installation
> - PIXIS LCD installer
> - SPI configuration
> - `/dev/spidev0.0` available after reboot
> - `volumio-lcd.service` enabled and automatically started
> - Radio Paradise playback
> - album art displayed
> - playback metadata displayed
> - fixed GPIO18 backlight with no visible flicker
> - hostname and IPv4 address displayed on the startup/idle screen
>
> Release tag:
>
> `VOLUMIO-LCD-v1.0.0`

The earlier pre-backlight-fix baseline is retained as:

`VOLUMIO-LCD-V3.905-KNOWN-GOOD-2026-08-15`

## Platform

This release is for:

- Volumio **3.905**
- Debian Buster-based Volumio 3
- Raspberry Pi
- Waveshare 2.8" SPI LCD, SKU 27579
- 240 × 320 display
- SPI display interface

A separate Volumio 4 implementation will be required for the newer Debian base.

**Do not install this Volumio 3/Buster release on Volumio 4.**

Volumio and moOde are maintained as **separate PIXIS installer paths**. The Volumio installer does not select, configure or install moOde.

---

# Stage 1 — Install Volumio

The verified Volumio image is:

**Volumio 3.905 — 2026-01-28**

Download:

https://updates.volumio.org/pi/volumio/3.905/Volumio-3.905-2026-01-28-pi.zip

Write the image to a microSD card and boot the Raspberry Pi.

The new Volumio installation will normally broadcast a hotspot with an SSID similar to:

`Volumioxxxx`

Connect a phone, laptop or desktop computer to that hotspot and open the Volumio setup interface.

Follow the Volumio first-run instructions to:

1. connect the Pi to your Wi-Fi network;
2. give the Volumio player a hostname;
3. reboot;
4. reconnect to the Volumio web interface;
5. complete the initial audio configuration.

For initial testing, HDMI or the Raspberry Pi headphone output may be used. An audio HAT can be configured later.

A useful introductory video is:

https://www.youtube.com/watch?v=0KZs--x1uPY

A Volumio account may be created if required.

For the PIXIS acceptance test, the Radio Paradise plugin provides a convenient known streaming source.

Confirm that Volumio can play audio successfully before proceeding with the LCD installation.

---

# Stage 2 — Enable SSH

The LCD installation requires command-line access.

If a monitor and keyboard are attached directly to the Raspberry Pi, log in locally.

Otherwise enable SSH through the Volumio development page:

`http://volumio.local/dev`

or substitute the hostname assigned to the player.

Then connect from another computer:

```bash
ssh volumio@volumioname.local
```

Use the hostname assigned during the Volumio setup.

The normal initial Volumio SSH password is:

`volumio`

Before installing the LCD software, confirm that the Pi has Internet access:

```bash
ping google.com
```

Stop the test with `Ctrl-C`.

---

# Stage 3 — Install PIXIS VOLUMIO-LCD

Run:

```bash
wget -qO- https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/main/VOLUMIO-LCD/bootstrap.sh | bash -x && sudo /tmp/pixis/stage/VOLUMIO-LCD/install.sh
```

The bootstrap downloads the required PIXIS VOLUMIO-LCD files from this repository and stages them under:

```text
/tmp/pixis/stage/VOLUMIO-LCD
```

The installer then performs the privileged installation steps.

The installer will request the Volumio password when `sudo` is reached. This is expected.

## First reboot

The installer enables SPI in `/boot/userconfig.txt`.

If `/dev/spidev0.0` is not yet available, the installer records that a reboot is required and exits cleanly.

Reboot:

```bash
sudo reboot
```

After reboot, the LCD service should start automatically.

A successful startup/idle display shows:

```text
Volumio LCD
Host: <hostname>
IP: <IPv4 address>
```

Start playback from the Volumio interface.

The LCD should then display album art and playback metadata.

---

# What the installer changes

The installer adds the required SPI settings to:

```text
/boot/userconfig.txt
```

Required settings are:

```text
dtparam=spi=on
dtoverlay=spi-spidev
```

The installer deliberately **does not overwrite `/boot/volumioconfig.txt`**.

Volumio owns that file and its existing configuration must be preserved.

---

# Runtime packages

The installer installs the Python packages required by the Waveshare driver and PIXIS LCD application:

- `python3-pil`
- `python3-spidev`
- `python3-gpiozero`
- `python3-numpy`

These provide the dependencies used by `volumio_lcd.py` and `LCD_2inch8.py`.

---

# LCD service

The production service is:

```text
volumio-lcd.service
```

It runs:

```text
/usr/bin/python3 /home/volumio/waveshare-2.8/Python/volumio_lcd.py
```

The service is enabled for automatic startup.

Useful checks:

```bash
systemctl status volumio-lcd.service --no-pager -l
systemctl is-enabled volumio-lcd.service
journalctl -u volumio-lcd.service -n 50 --no-pager -l
ls -l /dev/spidev*
```

A healthy installation should show:

- `/dev/spidev0.0`
- `volumio-lcd.service` enabled
- `volumio-lcd.service` active/running
- LCD displaying hostname and IPv4 address on the startup/idle screen
- album art and metadata while playing

---

# Backlight — GPIO18

The Waveshare LCD backlight is controlled from:

- BCM GPIO: **GPIO18**
- Raspberry Pi physical header pin: **12**

The original Waveshare Python driver used `PWMOutputDevice` at approximately 1 kHz and an 80% duty cycle.

During PIXIS hardware testing on 15 August 2026, GPIO18 was examined with an oscilloscope. The PWM waveform showed timing jitter and the LCD exhibited visible backlight flicker.

The diagnosis was confirmed by holding GPIO18 continuously HIGH at approximately 3.3 V. The flicker disappeared.

PIXIS does not currently require adjustable LCD brightness, so the verified driver uses GPIO18 as a fixed digital output:

```python
DigitalOutputDevice(BL_PIN, active_high=True, initial_value=True)
```

GPIO18 therefore remains HIGH while the LCD driver is active.

The compatibility brightness methods remain in the driver, but operation is effectively binary:

- `0` = backlight OFF
- non-zero = backlight ON

Variable PWM brightness is intentionally disabled in this release.

---

# Repository structure

The Volumio installer uses files under:

```text
VOLUMIO-LCD/
```

Important components include:

```text
bootstrap.sh
install.sh
systemd/pixis-installer.service
systemd/volumio-lcd.service
scripts/pixis-installer.sh
scripts/PiInstaller.sh
config/userconfig.txt
waveshare-2.8/Python/
```

The active Volumio service is `systemd/volumio-lcd.service`.

The earlier shared/template `volumio-lcd@.service` is not part of the current standalone Volumio installation.

---

# Volumio and moOde

PIXIS previously explored sharing parts of the installation architecture between Volumio and moOde.

That approach is no longer used.

The two players have sufficiently different operating environments and installation requirements that they are maintained independently:

```text
VOLUMIO-LCD/
MOODE-LCD/
```

Changes to one installer must not automatically be assumed appropriate for the other.

---

# Troubleshooting

## Backlight on but no PIXIS display

Check SPI:

```bash
ls -l /dev/spidev*
```

Then check the service:

```bash
systemctl status volumio-lcd.service --no-pager -l
```

## Service errors

```bash
journalctl -u volumio-lcd.service -n 50 --no-pager -l
```

## Test the Python application directly

Stop the service first:

```bash
sudo systemctl stop volumio-lcd.service
```

Then:

```bash
python3 /home/volumio/waveshare-2.8/Python/volumio_lcd.py
```

Restart the service afterwards:

```bash
sudo systemctl start volumio-lcd.service
```

## Startup / idle screen

Before playback has begun, the LCD displays the Volumio LCD title together with the player's hostname and IPv4 address.

If this screen is visible, the LCD hardware, SPI interface and display application are operating.

Start playback in Volumio. Album art and metadata should replace the startup/idle screen.

---

# Known-good recovery points

## Original verified Volumio 3.905 LCD baseline

```text
VOLUMIO-LCD-V3.905-KNOWN-GOOD-2026-08-15
```

Commit:

```text
9105d13
```

Verified:

- clean installation
- SPI
- service autostart
- Radio Paradise audio
- album art
- metadata

This baseline retains the original PWM backlight behaviour.

## Backlight-fix verified baseline

```text
VOLUMIO-LCD-V3.905-KNOWN-GOOD-BACKLIGHT-FIX-2026-08-15
```

Commit:

```text
e863e34
```

This adds the hardware-tested fixed GPIO18 backlight and eliminates the observed PWM flicker.

**This remains a historical recovery point. VOLUMIO-LCD v1.0.0 supersedes it as the current release.**

---

# Development policy

The local PIXIS repository and GitHub repository are maintained together as the source of truth for this project.

Changes should be:

1. tested on actual PIXIS hardware;
2. copied back to the local repository;
3. syntax checked where applicable;
4. committed deliberately;
5. pushed to GitHub;
6. tagged when a new known-good recovery point has been established.

Do not replace a hardware-tested known-good file merely because another repository version appears newer.

For problems or reproducible defects, please open a GitHub Issue.
