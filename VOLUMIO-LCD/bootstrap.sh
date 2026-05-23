#!/bin/bash
set -euo pipefail

STAGE_ROOT="/var/lib/pixis/stage"
PAYLOAD_DIR="$STAGE_ROOT/VOLUMIO-LCD"
BASE_URL="${PIXIS_BASE_URL:-}"

usage() {
  cat <<'EOF'
Usage:
  PIXIS_BASE_URL=http://192.168.5.139:8000/PIXIS-PROJECTS/VOLUMIO-LCD bash bootstrap.sh
EOF
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1"
    exit 1
  }
}

fetch_file() {
  local rel="$1"
  local dest="$PAYLOAD_DIR/$rel"
  mkdir -p "$(dirname "$dest")"
  curl -fsSL "$BASE_URL/$rel" -o "$dest"
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

if [ -z "$BASE_URL" ]; then
  echo "PIXIS_BASE_URL is not set"
  usage
  exit 1
fi

need_cmd curl
need_cmd install
need_cmd chmod

mkdir -p "$PAYLOAD_DIR"

fetch_file "install.sh"
fetch_file "systemd/pixis-installer.service"
fetch_file "systemd/volumio-lcd.service"
fetch_file "scripts/pixis-installer.sh"
fetch_file "scripts/PiInstaller.sh"
fetch_file "config/userconfig.txt"
fetch_file "config/volumioconfig.txt"

fetch_file "waveshare-2.8/Python/2inch8_LCD_test.py"
fetch_file "waveshare-2.8/Python/LCD_2inch8.py"
fetch_file "waveshare-2.8/Python/LCD_2inch8.py.bak"
fetch_file "waveshare-2.8/Python/Touch_2inch8.py"
fetch_file "waveshare-2.8/Python/test_fill.py"
fetch_file "waveshare-2.8/Python/volumio_lcd.py"
fetch_file "waveshare-2.8/Python/volumio_lcd.py.working"
fetch_file "waveshare-2.8/Python/pic/LCD_2inch8_1.jpg"
fetch_file "waveshare-2.8/Python/pic/LCD_2inch8_2.jpg"
fetch_file "waveshare-2.8/Python/pic/LCD_2inch8_3.jpg"

chmod +x "$PAYLOAD_DIR/install.sh"
chmod +x "$PAYLOAD_DIR/scripts/pixis-installer.sh"
chmod +x "$PAYLOAD_DIR/scripts/PiInstaller.sh"

exec "$PAYLOAD_DIR/install.sh"
