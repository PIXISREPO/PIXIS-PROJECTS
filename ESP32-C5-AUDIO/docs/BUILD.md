# Build the PCM5122 adaptation

Upstream: https://github.com/foonerd/evo-esp32

Pinned commit: `e446e9e870a5ce0df273c7121c6fd756b8cbe15a`.
Companion dependencies are pinned to `c73cb2bd21a520502155f5126082e2e52fdb9227`.

Read ../LICENSES/README.md before distributing or commercially using a build.
The patch retains upstream licensing and adds the no_std PCM5122 driver/tests,
shared I2C control, and sample-rate-following DAC initialization. It does not
change SD configuration or Wi-Fi startup. The driver's historical DAC+ naming
is retained; project hardware validation is scoped in VALIDATION.md.

```sh
git clone https://github.com/foonerd/evo-esp32.git
cd evo-esp32
git checkout -b pixis-pcm5122 e446e9e870a5ce0df273c7121c6fd756b8cbe15a
git apply --check /path/to/ESP32-C5-AUDIO/source/pcm5122.patch
git apply /path/to/ESP32-C5-AUDIO/source/pcm5122.patch
```

Install the pinned firmware Rust toolchain `nightly-2026-10-17`, `rust-src`,
Clippy, `ldproxy` and the ESP-IDF prerequisites. Firmware targets
`riscv32imac-esp-espidf`; ESP-IDF is pinned to v5.5.5. The full successful build
was performed on Linux. A Mac can FLASH the supplied image without having any
Rust/ESP-IDF build environment; a complete native macOS build is not verified.

```sh
cargo +nightly-2026-10-17 test --manifest-path drivers/pcm5122/Cargo.toml --locked
cd firmware/waveshare-esp32-c5-touch-lcd-28
cargo build --release --locked
cargo clippy --release --locked -- -D warnings
cd ../..
```

The original build environment needed CMake, Ninja, a usable libclang library
for bindgen, and Python outside an existing virtual environment while ESP-IDF
created its own environment. Preserve the upstream sdkconfig and partition table.

## Signing and factory assembly

Use an authorized private signing key OUTSIDE the repository:

```sh
EVO_SIGNING_KEY=/private/path/to/key.pem   bash scripts/image.sh firmware/waveshare-esp32-c5-touch-lcd-28
```

The script generates a custom partition table, assembles the Rust ELF as an
application image, signs it, checks capacity and creates the combined factory
image. Do not distribute ESP-IDF's placeholder `libespidf.bin` as the player.

The shipped bench image uses an owner-held ECDSA P-256 key, no hardware Secure
Boot and no eFuse programming. A new key changes which later signed OTA updates
are accepted; do not silently substitute keys. USB replacement remains the route
between signing domains on an unrestricted device. Never commit a private key.

Use ESP-IDF's actual flasher_args.json: C5 bootloader is at 0x2000 in this build,
not an assumed offset. The resulting combined factory image is flashed at 0x0.
The app sits at 0x20000. Partition and image hashes must be verified again after
any rebuild. Signing keys, timestamps, tools and git build IDs can alter bytes;
this patch is source reproduction, not a promise of a bit-identical binary.

The supplied image reports version 0.2.0 and `build:unknown`, because the original
build used a modified source ZIP without git metadata. Use SHA256 and BUILD.json
to identify it; do not relabel it as an official upstream release.
