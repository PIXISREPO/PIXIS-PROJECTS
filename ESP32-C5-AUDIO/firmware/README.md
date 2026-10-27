# Bench firmware artifact

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
