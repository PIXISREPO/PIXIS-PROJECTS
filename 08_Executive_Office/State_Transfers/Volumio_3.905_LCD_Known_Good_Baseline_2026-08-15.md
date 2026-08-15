# PIXIS Volumio 3.905 LCD — Known-Good Baseline

**Date:** 2026-08-15  
**Status:** FROZEN — KNOWN GOOD  
**System:** PIXIS CB-1 / Volumio 3.905 / Waveshare 2.8-inch SPI LCD

## Purpose

This record establishes the verified known-good PIXIS Volumio 3.905 LCD baseline following recovery of the Volumio LCD installer and application.

This baseline must not be modified as part of subsequent Volumio 4 development.

## Known-Good Git State

Repository:

PIXISREPO/PIXIS-PROJECTS

Commit:

9105d133758c9048a64195e0cd5d1c4e4d1d0d15

Commit description:

Restore known-good Volumio LCD application

Annotated Git tag:

VOLUMIO-LCD-V3.905-KNOWN-GOOD-2026-08-15

The tag was created in the local Mac repository and pushed to GitHub.

At acceptance, local HEAD and origin/main both resolved to:

9105d133758c9048a64195e0cd5d1c4e4d1d0d15

## Known-Good LCD Application

File:

VOLUMIO-LCD/waveshare-2.8/Python/volumio_lcd.py

SHA256:

52f4fdded03064136e627cabaf13a3ae765f7ffa6f8954c9750ffa8489433164

This exact file was recovered from the working Volumio system `volumio2` and verified before committing to the repository.

The application uses the Volumio API on localhost port 3000.

## Acceptance Test

The test began from the clean image:

VolumioNerd_V3.905_RadioParadise_T0_2026-08-15.img

The following end-to-end behaviour was verified:

1. Volumio 3.905 booted successfully.
2. HDMI login prompt appeared.
3. Volumio Web UI operated correctly.
4. Radio Paradise was available.
5. Radio Paradise playback produced audio.
6. PIXIS standalone Volumio LCD installer ran successfully.
7. SPI configuration was written to `/boot/userconfig.txt`.
8. System rebooted with SPI available.
9. `/dev/spidev0.0` and `/dev/spidev0.1` were present.
10. `volumio-lcd.service` was installed and enabled.
11. `volumio-lcd.service` started automatically after reboot.
12. LCD initially displayed `Waiting for Playback`.
13. Starting Radio Paradise playback caused album art and metadata to appear on the LCD.
14. Audio playback continued correctly.

**Acceptance Result: PASS**

## Installer Architecture

Volumio now uses a standalone service:

`volumio-lcd.service`

The installer:

- configures SPI through `/boot/userconfig.txt`;
- does not overwrite `/boot/volumioconfig.txt`;
- enables `volumio-lcd.service` before a required SPI reboot;
- allows systemd to start the LCD application automatically after reboot.

## Regression Found

The earlier working Volumio implementation had been broken during the June 2026 work to introduce Moode support and share installer architecture.

The shared-player refactor introduced Moode-specific behaviour into the Volumio path.

The failed Volumio application attempted to access:

`http://localhost:80/command/?cmd=currentsong`

This is not the required Volumio API.

The resulting connection-refused errors prevented the LCD application from reaching its normal display state.

The shared refactor also introduced a templated:

`volumio-lcd@.service`

and `config.env` dependency which were not present in the proven working Volumio installation.

## Recovery

The Volumio installer was reconstructed from repository history and comparison with the known-working `volumio2` installation.

The simple standalone:

`volumio-lcd.service`

architecture was restored.

The known-working `volumio_lcd.py` was recovered directly from `volumio2`, verified by SHA256, committed and pushed.

The complete installation was then tested successfully.

## Decision

**Volumio and Moode will have separate end-to-end installers.**

They will not share a common player-selection/forking installer architecture.

Their implementations are sufficiently different that maintaining independent installation paths provides greater reliability, clarity and recoverability.

## Volumio 4 Development Rule

The Volumio 3.905 baseline recorded here is frozen.

Volumio 4 adaptation must be developed separately.

Changes required for Volumio 4 must not be made by altering this tagged known-good Volumio 3 baseline.

The Git tag provides the permanent technical recovery point:

`VOLUMIO-LCD-V3.905-KNOWN-GOOD-2026-08-15`

## Recovery Reference

If future Volumio LCD development fails or becomes uncertain, return first to:

- Git tag `VOLUMIO-LCD-V3.905-KNOWN-GOOD-2026-08-15`
- commit `9105d133758c9048a64195e0cd5d1c4e4d1d0d15`
- `volumio_lcd.py` SHA256 `52f4fdded03064136e627cabaf13a3ae765f7ffa6f8954c9750ffa8489433164`

These identify the verified working PIXIS Volumio 3.905 LCD implementation.

## Post-Baseline Backlight Fix — 2026-08-15

A visible LCD backlight flicker was traced to software-timed PWM on GPIO18 / physical pin 12.

The Waveshare driver used:

`PWMOutputDevice(BL_PIN, frequency=1000)`

through gpiozero's `RPiGPIOFactory`, producing a jittery approximately 80% duty-cycle waveform.

The diagnosis was confirmed experimentally: holding GPIO18 continuously HIGH at 3.3 V eliminated the flicker.

PIXIS does not currently require adjustable LCD brightness, so the production fix is to remove PWM and use a fixed digital HIGH backlight while the LCD service is active.

The driver now uses:

`DigitalOutputDevice(BL_PIN, active_high=True, initial_value=True)`

The compatibility methods remain present so existing calls do not fail, but brightness control is binary only: 0 = OFF, non-zero = ON.

Acceptance result:

- `volumio-lcd.service` active and running
- GPIO18 steady HIGH
- backlight flicker eliminated
- LCD operation otherwise unchanged

This fix is recorded separately from the original frozen Volumio 3.905 baseline.

Post-baseline tag:

`VOLUMIO-LCD-V3.905-KNOWN-GOOD-BACKLIGHT-FIX-2026-08-15`
