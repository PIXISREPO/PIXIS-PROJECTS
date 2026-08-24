# PIXIS CST328 Touch Capture

Python touch-capture and zone-mapping code for the CST328 capacitive-touch controller used with the PIXIS/Waveshare 2.8-inch display work.

The production capture script is `touch_capture_final.py`.

## Status

This revision incorporates datasheet-backed corrections reviewed on 17 August 2026 while deliberately retaining the existing hardware-validated IRQ and coordinate-stability behaviour.

This is a narrow correction release, not an IRQ redesign or gesture-layer rewrite.

## Acknowledgement

Special thanks to **@nerd** for his careful independent review of the CST328 implementation and for turning the CST328 datasheet details into specific, testable corrections. His follow-up analysis corrected the reset-timing interpretation, confirmed the X/Y packing, identified the documented packet validity fields, clarified the D005 finger-count field, and distinguished CST328 address-only commands from register writes.

Those contributions materially improved the precision of this driver and its documentation.

## Changes in this revision

### Reset timing

The reset pulse remains 1 ms.

The post-reset recovery delay changes from 50 ms to 250 ms. The datasheet indicates approximately 200 ms for re-initialisation after reset, so 250 ms provides margin before the first I2C transaction.

### Packet validation

`read_xy_packet()` now reads 28 bytes from `0xD000` and rejects a report unless:

- `buf[6] == 0xAB`, the documented fixed marker at `0xD006`;
- `(buf[0] & 0x0F) == 0x06`, the documented pressed status.

### X/Y parsing

The existing X/Y arithmetic was confirmed and is unchanged:

```python
x = ((buf[1] << 4) + ((buf[3] & 0xF0) >> 4))
y = ((buf[2] << 4) + (buf[3] & 0x0F))
```

### Finger count

The redundant second D005 read inside `read_xy_packet()` has been removed.

The count now comes from the packet itself:

```python
points = buf[5] & 0x7F
```

Bit 7 is the documented button flag.

PIXIS is likely to use no more than two simultaneous touches, but the low-level parser deliberately reports the controller's real count. Any two-touch product limit belongs upstream in the gesture/application layer.

### Invalid packet handling

`read_xy_packet()` may now return `None`.

`read_stable_xy()` skips invalid/non-pressed reports safely and still requires the existing number of valid stable samples.

### Register-write helper

The old helper did not correctly represent a one-byte write to a 16-bit register address.

The new helper uses:

```python
bus.write_i2c_block_data(
    CST328_ADDRESS,
    (reg >> 8) & 0xFF,
    [reg & 0xFF, val & 0xFF]
)
```

## D005 clear caveat

The existing capture path clears `0xD005` after an accepted touch.

That behaviour is retained in this revision to avoid changing the established re-arm behaviour at the same time as the datasheet corrections.

However, the CST328 datasheet does **not** document a D005 clear operation. The corrected helper makes the intended write transaction valid; it does not establish that the clear is required.

This remains a hardware-validation question.

## Deliberately unchanged

The following are not changed in this revision:

- rising-edge / active-high IRQ behaviour;
- IRQ sample counts;
- D005 readiness polling;
- three-sample X/Y stability;
- X/Y drift tolerance;
- artwork zone mapping;
- duplicate-event policy;
- panel-resolution auto-detection;
- kernel-driver integration;
- gesture interpretation;
- a two-finger application limit.

These should be tested independently.

## Current capture flow

1. Wait for the currently validated rising IRQ transition.
2. Confirm the IRQ with the existing sampling rule.
3. Poll D005 for readiness.
4. Read the 28-byte normal-mode report from D000.
5. Validate the fixed `0xAB` marker.
6. Validate pressed status `0x06`.
7. Decode X, Y and finger count from the same packet.
8. Require the existing stable valid X/Y samples.
9. Map the touch to the PIXIS artwork zone.
10. Log the accepted event.
11. Perform the existing D005 clear using the corrected register-write helper.

## Zone mapping

The verified zone mapping is unchanged:

- A1 — top-left
- A2 — top-right
- A3 — middle-left
- A4 — middle-right
- B1 — bottom-left
- B2 — bottom-centre
- B3 — bottom-right

## Hardware constants

- CST328 7-bit I2C address: `0x1A`
- Touch IRQ: BCM GPIO `4`
- Touch reset: BCM GPIO `17`

The documented default 8-bit I2C pair `0x34/0x35` corresponds to 7-bit address `0x1A`.

## Follow-up experiments

These are worth testing separately, but are not production changes in this revision:

- falling-edge IRQ timing versus current rising-edge behaviour;
- reducing stability sampling now that packet-validity fields are checked;
- operation with and without the undocumented D005 clear;
- reading panel resolution from `0xD1F8`.

## Historical development

Earlier hardware work established that:

- `int_test.py` was fundamental to understanding the IRQ behaviour;
- D005 readiness polling improved capture reliability;
- X/Y drift tolerance was widened to preserve genuine taps;
- the A1/A2/A3/A4 + B1/B2/B3 artwork map was verified;
- duplicates are acceptable at capture time and can be handled upstream.

The new datasheet-backed validation supplements those observations rather than replacing them.

## Validation before release

Before this revision becomes a new known-good GitHub baseline, verify on target hardware:

- clean start after reset;
- repeated single-finger taps;
- all artwork zones;
- rapid taps;
- press/release behaviour;
- no increase in missed touches;
- correct finger-count logging;
- continued re-arming after the D005 clear;
- duplicate behaviour remains acceptable.

Only after hardware validation should the corrected files be committed as the production versions and tagged as known-good.
