#!/usr/bin/env bash
set -euo pipefail

BASE_URL="https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/main/VOLUMIO-LCD"
STAGE_ROOT="${TMPDIR:-/tmp}/pixis/stage"
PAYLOAD_DIR="$STAGE_ROOT/VOLUMIO-LCD"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

fetch() {
  local path="$1"
  local dest="$2"
  mkdir -p "$(dirname "$dest")"
  curl -fsSL "$BASE_URL/$path" -o "$dest"
}

need_cmd curl
need_cmd chmod
need_cmd mkdir

rm -rf "$PAYLOAD_DIR"
mkdir -p "$PAYLOAD_DIR"

fetch "install.sh" "$PAYLOAD_DIR/install.sh"
fetch "systemd/pixis-installer.service" "$PAYLOAD_DIR/systemd/pixis-installer.service"
fetch "systemd/volumio-lcd.service" "$PAYLOAD_DIR/systemd/volumio-lcd.service"
fetch "scripts/pixis-installer.sh" "$PAYLOAD_DIR/scripts/pixis-installer.sh"
fetch "scripts/PiInstaller.sh" "$PAYLOAD_DIR/scripts/PiInstaller.sh"
fetch "config/userconfig.txt" "$PAYLOAD_DIR/config/userconfig.txt"
fetch "config/volumioconfig.txt" "$PAYLOAD_DIR/config/volumioconfig.txt"
fetch "README.md" "$PAYLOAD_DIR/README.md"

chmod +x "$PAYLOAD_DIR/install.sh"
chmod +x "$PAYLOAD_DIR/scripts/pixis-installer.sh"
chmod +x "$PAYLOAD_DIR/scripts/PiInstaller.sh"

echo "Bootstrap payload staged at: $PAYLOAD_DIR"
echo "Run install.sh from the staged payload when ready."

