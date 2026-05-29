# CST328 Touch Capture for Waveshare 2.8" LCD

This repository contains the Python touch capture code used to interface the CST328 capacitive touch controller on a Waveshare 2.8" Capacitive Touch LCD (SKU 27579) connected by SPI and I2C to a Raspberry Pi SBC.

The final goal was not simply to read touch data, but to build a robust capture pipeline that reliably identifies valid touches, maps them to specific zones on the LCD and keeps enough tolerance for real-world finger placement and controller timing.

## What this project does

The code:
- Detects touch events from the CST328.
- Validates the interrupt line.
- Waits for the CST328 X, Y coordinates report to become ready.
- Reads stable X/Y coordinates.
- Maps the touch to a named artwork zone.
- Logs one accepted touch event per capture.

The final working capture script is:

- `touch_capture_final.py`

## Why this was needed

The CST328 is a capable touch controller, but in practice it does not behave like a simple button. It reports data over I2C, uses IRQ as a notification signal, and can produce edge timing that is not immediately obvious from the datasheet alone [file:1874].

We needed to solve several practical problems:
- Determine the correct IRQ polarity for the board path.
- Understand when `D005` becomes valid.
- Decide how much X/Y drift to accept.
- Validate the physical artwork zones on the LCD.
- Avoid missing real taps while still keeping output reliable.

In other words, the project was about turning a touch controller into a dependable input path for a real user interface, not just proving that I2C reads worked [file:1874].

## How it works

The final capture flow is:

1. Wait for an IRQ edge.
2. Sample the IRQ line to confirm it is a real event.
3. Poll `D005` until it shows a non-zero finger count.
4. Read the touch packet from `D000`.
5. Read several samples and accept the touch only when X/Y are stable enough.
6. Convert the coordinate to an artwork zone.
7. Emit one accepted event.
8. Clear `D005` so the controller can re-arm for the next touch.

The CST328 datasheet describes IRQ as the host notification mechanism and `D005` as the finger-number/report flag in normal mode, which matches the approach above [file:1874].

## Zone layout

The project does not use a generic grid label scheme. Instead, it uses the artwork layout shown in the spreadsheet image:

- A1: top-left.
- A2: top-right.
- A3: middle-left.
- A4: middle-right.
- B1: bottom-left.
- B2: bottom-centre.
- B3: bottom-right.

This mapping was verified in the corner and bottom-zone tests, and the final label logic matches the intended artwork layout.

## Final capture behavior

The final code was intentionally tuned to be permissive at capture time:
- It accepts active-high IRQ behavior for this board path.
- It uses `D005` as the real touch-valid gate.
- It allows a relaxed X/Y drift window.
- It keeps duplicates out of the critical path for now.

That was deliberate. It is better to capture a slightly noisy stream than to lose real touches, especially because duplicates can be handled later in the next stage.

## Test scripts used during development

Several small scripts were written while debugging the controller. These are worth keeping in the repo because they document the path to the final solution and can be reused when hardware changes.

### `int_test.py`

This was the key discovery script.

It was used to inspect the raw IRQ line timing and determine whether the touch signal was acting as active-high or active-low in the actual hardware path. That test was fundamental in changing the capture logic from a low-based assumption to an active-high one.

### `test1.py`

This script captured short IRQ windows and helped confirm that the signal was mostly high during touch activity, with only brief low blips around transitions.

### `test2.py`

This extended the same idea and helped validate the IRQ behavior across multiple short and long touches.

### `int_v36.py`

This version added lightweight debug around:
- IRQ validation,
- `D005` readiness,
- and X/Y stability.

It helped identify which stage of the capture pipeline was failing.

### `int_v38.py`

This became the first really usable capture version after IRQ polarity and `D005` handling were corrected. It reliably produced stable touch coordinates.

## Development notes

A few important lessons came out of the work:
- IRQ should be treated as an event hint, not the final truth.
- `D005` is the better gate for touch data readiness.
- Real finger touches jitter, so X/Y should be validated with a tolerance rather than requiring exact repeated values.
- The artwork zone map should reflect the UI design, not a generic numeric grid.
- Duplicate hits are acceptable at capture time if the next processing stage can dedupe them later.

## Repository contents

Suggested files to include:

- `touch_capture_final.py` - final production capture script.
- `int_test.py` - raw IRQ discovery script.
- `test1.py` - IRQ timing capture script.
- `test2.py` - extended IRQ timing capture script.
- `int_v36.py` - debug capture version.
- `int_v38.py` - stable capture version before final cleanup.
- `README.md` - this document.

## Hardware context

This code was developed for a CST328 touch controller used with a Raspberry Pi and a Waveshare 2.8" LCD. The CST328 datasheet confirms the controller provides I2C touch data, an IRQ line, and normal-mode finger reporting via `D005`, which is the basis of this implementation [file:1874].

## License

Choose the license that fits your repo before publishing. If this is intended for open-source reuse, add a standard license file such as MIT or BSD-3-Clause.

## Future work

Possible next steps:
- Add debounce/deduplication in the consumer stage.
- Add optional calibration offsets if the physical mounting changes.
- Add support for richer touch gestures if needed.
- Add a small zone test utility for future hardware revisions.
