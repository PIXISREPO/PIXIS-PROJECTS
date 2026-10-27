# Functional source patch

Apply pcm5122.patch to the pinned upstream commit as described in ../docs/BUILD.md.
Only functional source/manifests/locks are patched. Historical bench README and
Raspberry Pi DAC+ setup prose are intentionally excluded: use this project's
hardware and installation documentation instead. The patch does not relicense
upstream work. See ../LICENSES/.

Changed paths:

- `Cargo.toml`
- `drivers/pcm5122/.gitignore`
- `drivers/pcm5122/Cargo.lock`
- `drivers/pcm5122/Cargo.toml`
- `drivers/pcm5122/src/lib.rs`
- `drivers/pcm5122/src/tests.rs`
- `firmware/waveshare-esp32-c5-touch-lcd-28/Cargo.lock`
- `firmware/waveshare-esp32-c5-touch-lcd-28/Cargo.toml`
- `firmware/waveshare-esp32-c5-touch-lcd-28/src/main.rs`
