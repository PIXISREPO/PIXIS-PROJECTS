# ESP32-C5 Audio Player

![ESP32-C5 Audio Player in portrait orientation, showing Absolute 80s artwork, track information and playback controls](assets/images/esp32-c5-audio-player-portrait-web.jpg)

*The working ESP32-C5 Audio Player. Photograph supplied by Peter; perspective-corrected, cropped and lightly retouched. Display content has not been replaced. This photograph shows the panel interface, not the complete CB-1 assembly.*

> **Review-branch upload in progress:** text files are uploaded through the GitHub connection. The firmware binary and photographs require a separate browser upload; their links will become available when that step is complete.

**CB-1 + Waveshare ESP32-C5-Touch-LCD-2.8 + Waveshare PCM5122 Audio Board (A). No Raspberry Pi fitted.**

Status: **working bench project; installation documentation in development**.
Peter reports that the supplied USB image flashed successfully from macOS,
followed the expected startup process, and played audio from the Waveshare
PCM5122 Audio Board (A). This is a reported functional result, not a completed
release-acceptance test or a guarantee for every PCM5122 HAT.

The panel runs a PCM5122 adaptation of @nerd / foonerd's
[evo-esp32](https://github.com/foonerd/evo-esp32) player. The original SD-card
configuration and Wi-Fi startup are retained. This is not Volumio running on an
ESP32, and is separate from the PIXIS Raspberry Pi / Volumio display projects.

## Start here

1. Read [hardware and power notes](docs/HARDWARE.md). U13/U1 roles are owner-confirmed for CB-1 v2.8; numbered cable pinouts
   and assembled photographs still require verification.
2. Follow [macOS backup, installation and recovery](docs/INSTALL-MAC.md).
3. Prepare a FAT32 microSD card with `evoconfig.txt` in its root. Keep an
   existing working file, or adapt [the minimal example](config/evoconfig.example.txt).
4. Check [validation and remaining work](docs/VALIDATION.md).

## One project, three firmware options

The common first-time-builder guide covers the panel, CB-1 installation,
SD-card Wi-Fi configuration, USB flashing and recovery. Completing the original
upstream hardware build is NOT a prerequisite to flashing a complete image.
The upstream repository remains the source and deeper technical reference.

| Firmware option | Hardware | Status |
|---|---|---|
| Original @nerd configuration | Original supported DAC arrangement, including PCM5102A | Upstream baseline; original image not packaged in this project yet |
| PCM5122 | Waveshare PCM5122 Audio Board (A) | Owner-reported successful playback; exact supplied image retained |
| PCM5242 | Raspberry Pi DAC Pro | Planned; no adapted or tested binary supplied yet |

Do not treat different HATs as electrically interchangeable. Genuine Raspberry
Pi / IQaudio DAC+ power and hardware behaviour have not been validated by the
Waveshare board's playback result. Future releases should pin one upstream
baseline and identify each variant, tested hardware revision and checksum.

## Firmware

- [Download the combined USB factory image](firmware/evo-c5-dacplus.factory.bin)
- [Image SHA256](firmware/SHA256SUMS)
- [Original build identity](firmware/BUILD.json)

The historical `dacplus` filename is retained so existing flashing instructions
and the tested image hash remain consistent. The reported working DAC is the
**Waveshare PCM5122 Audio Board (A)**. The earlier investigation of the Raspberry
Pi / IQaudio DAC+ does not establish that board's power requirements or hardware
validation. Do not conflate the boards.

The image is for the C5 panel with **32 MB flash and 8 MB PSRAM**. Flash the
combined file at **0x0** only after backing up the panel. Do not flash it to an
S3/C6, or use it as an application-only OTA image.

## What remains unchanged

The firmware mounts the panel's microSD card at `/sdcard`, reads its root-level
`evoconfig.txt`, and starts Wi-Fi from `wifi_ssid`, `wifi_password` and optional
`wifi_band`. SD mounting, `config.rs`, `net.rs`, and the Wi-Fi startup block were
compared with the pinned upstream and are unchanged. A card-mount failure idles
before Wi-Fi initialization; no configured SSID means no Wi-Fi connection.

The onboard speaker path remains enabled. The external stream is 16-bit stereo;
this build does not add native 24/32-bit output or 192 kHz operation. A successful
playback report does not validate every configured rate, format or source.

## Source, credit and licensing

Original player: **Just a Nerd / @nerd / foonerd**. This project documents its
PCM5122 adaptation and PIXIS integration; it does not imply upstream endorsement.

[Build instructions and exact source patch](docs/BUILD.md) pin the upstream
commit. The upstream firmware and its modifications retain **Business Source
License 1.1**, not this repository's MIT licence. See [licensing notes](LICENSES/README.md)
and [the complete upstream licence](LICENSES/evo-esp32-BUSL-1.1.txt).
The original licence limits commercial incorporation/distribution without a
separate written agreement. Do not present this as commercially cleared firmware.

Private signing keys, flash backups and real network credentials must never be
added to this project. This is a preparation package, not a published GitHub release.
