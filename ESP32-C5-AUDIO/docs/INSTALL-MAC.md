# macOS USB installation and recovery

READ FIRST: This is a bench build with owner-reported successful USB flashing and audio playback for the
Waveshare ESP32-C5-Touch-LCD-2.8 with 32 MB flash and 8 MB PSRAM. It is not for
ESP32-S3/C6 or the DAC Pro/DigiAMP+. The original on-board speaker path remains
enabled. Start with external amplifier and headphones disconnected.

The image includes bootloader, custom partition table and signed application.
Flash the combined factory file at **0x0**, NOT at the internal application
offset of 0x20000. It replaces firmware and initial flash data, including NVS
and OTA selection. It does not erase the SD card. Back up your board first.

The CB-1 power wiring and electrical measurements have not been fully documented.
The target DAC is Waveshare PCM5122 Audio Board (A), not the earlier Raspberry Pi
DAC+ under investigation. Read HARDWARE.md before wiring either board.

## 1. Hardware preparation

Use a data-capable USB-C cable. For the first flash/boot, test the panel alone:
power everything off before disconnecting CB-1/HAT signal and supply wiring.
Avoid joining independent 5 V supplies through USB VBUS. Never hot-plug wiring.
After the panel works, complete the HAT rail checks before reconnecting it and
trying audio. Keep amplifier/headphones disconnected until levels are safe.

Close any serial monitor before esptool accesses the port. These commands do
not enable hardware Secure Boot, flash encryption, or burn eFuses. If the board
already has security restrictions, or esptool reports a security/encryption
error, STOP; do not use --force or alter eFuses.

## 2. Install the command-line tool on macOS

Requires Python 3. Run in Terminal:

```sh
python3 -m venv ~/espflash-venv
source ~/espflash-venv/bin/activate
python -m pip install 'esptool==5.6.0'
```

Download this repository as a ZIP, unzip it, and enter the firmware folder
(adjust the path if using a branch ZIP or a different download location):

```sh
cd ~/Downloads/PIXIS-PROJECTS-main/ESP32-C5-AUDIO/firmware
shasum -a 256 -c SHA256SUMS
ls /dev/cu.usbmodem*
```

All checksum entries must report OK. Replace the placeholder below with the
actual /dev/cu.usbmodem... device returned for your panel; do not type it unchanged.

```sh
PORT='/dev/cu.usbmodemREPLACE_WITH_YOUR_PORT'
python -m esptool --chip esp32c5 --port "$PORT" flash-id
```

Confirm the chip is ESP32-C5 and detected flash is **32 MB**. If not, STOP.

## 3. Back up the existing 32 MB flash

Choose a new backup filename; do not overwrite a previous known-good backup.
The backup can contain credentials, so keep it private. Also keep a separate
copy of the SD card, especially evoconfig.txt.

```sh
python -m esptool --chip esp32c5 --port "$PORT" read-flash 0x0 0x2000000 panel-before-dacplus.bin
```

Require a successful completed backup before proceeding.

## 4. Flash the factory image

```sh
python -m esptool --chip esp32c5 --port "$PORT" write-flash 0x0 evo-c5-dacplus.factory.bin
```

Wait for writing and verification to finish successfully; do not unplug during
writing. Do not run erase-flash: it is not required. If automatic reset fails,
use the board's documented BOOT/reset download-mode procedure, recheck the
serial-port name and retry. The port name may change after reset.

## 5. First boot

Reset if necessary. A panel-only test should run the UI and log that the
external DAC is unavailable; that is expected while the HAT is disconnected.
Do not assume silence means a successful DAC test. Complete the power checks,
then reconnect the verified HAT with all power off. Use a quiet known 44.1 kHz
or 48 kHz stereo file and low player volume for the first audio test.

The firmware reads evoconfig.txt and music from the SD card. Keep your existing
configuration; do not replace it with a generic example. Neither DAC hardware
support above 96 kHz nor native 24/32-bit sink output is added by this patch.

The identifying initialization log is:

    pcm5122: DAC+ configured at 0x4c, 44100 Hz 16-bit, BCK PLL, 0 dB

Its presence reports I2C initialization and the PLL-lock check, not measured
analogue performance. See HARDWARE.md and VALIDATION.md for wiring and format limits.

## Recovery and signing

With hardware security restrictions absent, the full backup can be restored
using the same USB procedure:

```sh
python -m esptool --chip esp32c5 --port "$PORT" write-flash 0x0 panel-before-dacplus.bin
```

This bench image uses a newly generated ECDSA P-256 application-signing key,
provided in a SEPARATE private-key archive. Keep that archive private, backed
up and outside source control. It is not needed for USB flashing. Future OTA
updates accepted by this build need the same key; an original-project OTA may
be rejected. Return to the original image by USB reflash, not by assuming its
OTA signature will be accepted. No hardware security setting is changed by
the supplied flashing command.

## Validation and reproducibility

Full release build passed. Release Clippy passed with warnings denied. Seven
PCM5122 driver tests passed. ECDSA signature, ESP32-C5 image identity, image
hash/checksum, partition capacity and merged byte layout were checked offline.
The owner subsequently reported successful panel flashing and DAC audio playback.
CB-1 electrical measurements, per-rate checks and long-duration testing remain open.
The log's build ID is `unknown` because this was built from the modified source
ZIP rather than a git checkout; use the SHA256 and BUILD.json to identify it.

This project includes a source patch and offline validation evidence. No private
signing key is included here. Additional signature blocks 1 and 2 being unused
in the verification log is normal: block 0 is the verified ECDSA signature.
