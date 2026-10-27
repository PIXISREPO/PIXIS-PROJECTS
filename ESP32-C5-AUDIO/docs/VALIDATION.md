# Validation record and remaining work

## Offline validation completed

- Full ESP32-C5 release build: passed.
- Release Clippy with warnings denied: passed.
- Independent PCM5122 driver tests: 7 passed.
- ECDSA signature block 0: verified.
- Image target: ESP32-C5; DIO, 80 MHz, 32 MB flash.
- Factory image: 4,653,056 bytes; signed app: 4,521,984 bytes.
- Application fits 5,505,024-byte factory partition.
- Internal offsets: bootloader 0x2000, table 0x8000, app 0x20000.
- Combined image is flashed at 0x0. Regions match input files byte-for-byte.
- SD/config/Wi-Fi startup compared with pinned original: unchanged.

Logs in evidence/ were generated BEFORE the owner performed the hardware test.
Their original 'not hardware tested' wording is historical, not a denial of the
later report. Unused signature blocks 1 and 2 are normal; block 0 verifies.

## Owner-reported result

Peter reported that the binary worked as expected and audio was playing from
the Waveshare PCM5122 Audio Board (A), following the macOS USB installation.
The report supports successful flashing and audio playback on that rig. It did
not include rail readings, scope traces, exact tested sample rates, network
logs, DAC revision photographs or endurance results. These are not claimed.

Original build metadata still says 'DAC+' and 'untested on hardware': this
identifies the historical artifact and has not been rewritten to imply a new
build or bit-identical rebuild. The binary itself is unchanged.

## Audio implementation limits

16-bit stereo, 16-bit Philips I2S slots (BCK = 32 x LRCK). Driver clock plans
cover 32, 44.1, 48, 88.2 and 96 kHz; support in code is not a physical test result
for each rate. Other rates/widths mute the external DAC and log a warning.
No native 24/32-bit sink, resampling or 192 kHz support is added. The onboard
speaker path remains enabled; `dac` / `output` settings are not implemented
as output selectors in this patch. DAC setup failures log and allow the player
to continue; UI or Wi-Fi success alone therefore does not prove DAC success.

## Gates before a customer-ready release

- [ ] Record CB-1, panel and DAC revisions with photographs.
- [ ] Net-check and illustrate CB-1 connector-level assembly.
- [ ] Record power entry, rail readings, current budget and USB supply behaviour.
- [ ] Repeat installation from a clean SD card and verify Wi-Fi/status output.
- [ ] Measure I2S timing and test each advertised rate.
- [ ] Test restart, missing-card, missing-config and disconnected-DAC behaviour.
- [ ] Test volume/mute, sources/formats and extended playback.
- [ ] Exercise USB backup/restore; document recovery result.
- [ ] Verify signed OTA with this build's key before advertising that route.
- [ ] Confirm upstream licence permissions for any proposed commercial use.
- [ ] Review and publish a versioned firmware release with matching checksums.

The Raspberry Pi / IQaudio DAC+ is not hardware-validated by the Waveshare
playback report and must be tested separately if added as a supported option.
