# Firmware downloads — choose by DAC

This project has three named firmware options. The SD-card package is shared;
see the [project guide](../README.md#1-choose-your-firmware) for downloads and setup.

| Firmware | DAC | Availability |
|---|---|---|
| C5 Audio — Original (PCM5102A) | Pins-configured PCM5102A I2S modules | [Upstream v0.2.0 factory binary](https://github.com/foonerd/evo-esp32/releases/download/v0.2.0/evo-esp32-waveshare-esp32-c5-touch-lcd-28-0.2.0.factory.bin); [upstream checksums](https://github.com/foonerd/evo-esp32/releases/download/v0.2.0/SHA256SUMS). Not a PIXIS rebuild or claimed PCM5102A/CB-1 bench validation. |
| C5 Audio — PCM5122 | Waveshare PCM5122 Audio Board (A); genuine Pi / IQaudio DAC+ not yet validated | [Factory binary](https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/refs/heads/project/esp32-c5-pcm5122/ESP32-C5-AUDIO/firmware/evo-c5-dacplus.factory.bin), stored in this folder; [checksums](SHA256SUMS). Owner-reported successful playback with Waveshare board. |
| C5 Audio — PCM5242 | Raspberry Pi DAC Pro | Planned; no binary available. |

Both available downloads are combined USB factory images flashed at **0x0**,
not app-only OTA files. Do not substitute one DAC variant for another.

## PCM5122 bench artifact

This is the exact previously supplied factory image; it has NOT been rebuilt or
re-signed for project packaging. Owner-reported audio playback was subsequently
obtained with the Waveshare PCM5122 Audio Board (A). BUILD.json is historical
metadata, preserved unchanged; current validation scope is ../docs/VALIDATION.md.

Run `shasum -a 256 -c SHA256SUMS` from this directory before use. Flash the combined
file at 0x0 following ../docs/INSTALL-MAC.md. Do not flash at the internal app offset.

Private signing key: excluded. It is held by the owner, not required for USB
flashing and must never be uploaded with these files. Full flash backups and
live Wi-Fi configuration are also excluded. The firmware's licence is included
in ../LICENSES/ and is NOT the host repository's MIT licence.
