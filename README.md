# PIXIS Projects

## Latest PIXIS Volumio Touch project

**[Open PIXIS Volumio Touch for Volumio 4 →](https://github.com/PIXISREPO/VOLUMIO-4-TOUCH)**

The current CB-1 touchscreen music-player guide has its own repository: **VOLUMIO-4-TOUCH**. It covers Raspberry Pi 3A+ and Zero 2 W using foonerd’s rpi-waveshare28 software.

Start there for a new Volumio 4 build. The similarly named folders below contain earlier PIXIS software or separate component work.

## ESP32-C5 Audio Player — working bench project

**[Open the ESP32-C5 Audio Player project →](ESP32-C5-AUDIO/)**

CB-1 v2.8 with the Waveshare ESP32-C5-Touch-LCD-2.8 and an external audio DAC,
without a Raspberry Pi. One common installation guide with DAC-specific firmware
options: original configuration, PCM5122 (reported working), and PCM5242 (planned).
Assembly documentation is in development. Binary and photo uploads are being
completed on this review branch. Third-party firmware retains its upstream
Business Source License 1.1, not this repository's MIT licence.

## Other projects and earlier work

| Folder | Purpose |
|---|---|
| [MOODE-LCD](MOODE-LCD/) | Separate moOde Audio display project. |
| [VOLUMIO-LCD](VOLUMIO-LCD/) | Earlier PIXIS Python display for **Volumio 3.905**. Retained for existing installations and recovery. |
| [PIXIS-TOUCH](PIXIS-TOUCH/) | Standalone CST328 touch-capture component and technical reference. |
| [VOLUMIO-TOUCH](VOLUMIO-TOUCH/) | Earlier Python touchscreen development, including mute experiments and Waveshare setup files. |
| [EO-OS-BRIDGE-TEST](EO-OS-BRIDGE-TEST/) | Repository integration test material. |

The current Volumio 4 project is not inside either `PIXIS-TOUCH` or `VOLUMIO-TOUCH`. You do not need those folders to follow its guide.

Earlier file paths are retained so existing download links, installers and recovery references continue to work.

## About PIXIS

PIXIS is an open-source modular hardware and software platform for Raspberry Pi and similar single-board computers. Projects include audio players, smart-home hubs, dashboards and custom embedded builds.

Visit [PIXIS](https://pixis.uk) for the platform and hardware.
