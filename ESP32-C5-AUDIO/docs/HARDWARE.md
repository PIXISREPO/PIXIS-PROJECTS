# Hardware, wiring and power

## Target configuration

- PIXIS CB-1 v2.8: reference carrier; assembled connector photographs still to be recorded.
- Waveshare **ESP32-C5-Touch-LCD-2.8**, 32 MB flash / 8 MB PSRAM.
- Waveshare **PCM5122 Audio Board (A)**, the DAC identified in Peter's playback report.
- FAT32 microSD card in the panel, suitable power source and USB-C data cable.

Manufacturer references:
- https://docs.waveshare.com/ESP32-C5-Touch-LCD-2.8
- https://www.waveshare.com/wiki/PCM5122-Audio-Board-A

Waveshare specifies 5 V supply, 3.3 V logic, I2C control at 0x4C and I2S audio
for this DAC. Its documented supported controller is Raspberry Pi; this custom
ESP32 integration is outside that documented support scope.

## Dedicated CB-1 v2.8 connections

Peter confirms the following intended connections:

| Carrier connector | Panel connection | Function |
|---|---|---|
| U13, dedicated JST | Panel audio/power wiring; numbered pinout pending | I2S signals, 5 V and ground linked to the 40-pin HAT interface |
| U1, QWIIC | Panel J5 | I2C connection to the 40-pin HAT SDA/SCL lines |

The connector callout guide identifies U13 as callout 16 and U1 as callout 1.
It is a location guide, not an electrical schematic. U13 pin order, JST series,
cable orientation, and the U1 3.3 V net connection still need confirmation from
the electrical schematic. Because QWIIC includes a power conductor, do not call
the assembled HAT connection '5 V only' until its 3.3 V path has been traced.
Do not infer power direction, source isolation or current rating from labels.

## Signal map used by this firmware

| Function | ESP32 GPIO | Panel connector | DAC physical 40-pin position |
|---|---:|---|---:|
| BCK | 2 | J8 pin 7 | 12 |
| LRCK / WS | 3 | J8 pin 8 | 35 |
| Data into DAC | 11 | J6 pin 2 / TXD | 40 |
| I2C SDA | 0 | J5 pin 2 | 3 |
| I2C SCL | 1 | J5 pin 1 | 5 |
| Ground | — | J6 pin 4 or verified ground | 6 |

This is the firmware/panel signal mapping, NOT an approved CB-1 connector-level
assembly drawing. Check the actual carrier revision's nets and pin 1 before
connecting. Physical header positions are not Raspberry Pi BCM GPIO numbers.
The ESP32 supplies I2S clocks. No MCLK wire is used; the PCM5122 PLL uses BCK.
The 0x4C setting is known-board initialization, not automatic unique DAC identification.

## Power precautions

Power everything off before changing wiring. Do not hot-plug. Never apply 5 V
to 3.3 V logic or GPIO. Keep the normal assembled system's grounds common.
Do not join independent 5 V supplies through the panel's USB VBUS connection.
The final CB-1 power route, current budget and USB/carrier coexistence still
need recording for a repeatable customer guide.

The panel schematic identifies MP1605 main 3.3 V conversion rated 2 A TOTAL;
that is not a verified external-accessory current allowance. No spare-current
claim is made here. Do not add a panel-to-HAT 3.3 V wire or parallel regulator
outputs based on the earlier Raspberry Pi DAC+ discussion.

The Raspberry Pi / IQaudio DAC+ was investigated earlier, but is NOT the board
identified in the successful playback report. No measured U2 supply readings
or complete supply-net trace for that HAT were supplied. Its requirements remain
separate from the Waveshare board specification and must not be inferred from it.

## Mechanical installation gate

Before describing a ready-to-follow CB-1 installation, add:
- CB-1 revision and labelled connector photographs / net-checked pinout.
- A photograph of the actual DAC and its revision markings.
- Panel mounting, suitable spacers, rear output access and cable routing.
- Explicit power entry / USB-flashing arrangement and supply rating.
- An assembled photograph and a repeat build from these instructions.

Do not assume the 40-pin connector is safe simply because it physically fits.

## Planned rear-accessible microSD extension

The existing PIXIS microSD-shaped FPC adapter design will be lengthened to reach
the ESP32 panel's card socket, with signal integrity considered in the longer
layout. Intended path: panel card socket -> longer FPC -> U6 -> rear socket U8.
The example photograph supplied by Peter shows the existing Pi Zero assembly;
U6 contact compatibility must be confirmed for the new panel cable.

This is a planned accessory, not a newly tested installation. Until available,
use the PANEL's onboard microSD slot for evoconfig.txt and music. The extension
is intended to retain the existing SD interface and firmware startup, subject
to testing. Do not connect the card to a Pi and ESP32 simultaneously. Insert or
remove cards with power off unless hot-swap operation is separately validated.
