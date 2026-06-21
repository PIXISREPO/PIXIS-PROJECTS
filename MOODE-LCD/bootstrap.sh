#!/usr/bin/env bash
set -euo pipefail

GITHUB_RAW="https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/main/MOODE-LCD"
WORK_DIR="/tmp/moode-lcd-install"

info()  { echo "[moode-bootstrap] $*"; }
fail()  { echo "[moode-bootstrap] ERROR: $*" >&2; exit 1; }

confirm() {
  local reply
  read -r -p "${1:-Proceed? [y/N]: }" reply
  case "${reply,,}" in
    y|yes) return 0 ;;
    *) return 1 ;;
  esac
}

echo
echo "PIXIS MOODE-LCD Bootstrap"
echo
echo "This will download and install the PIXIS Moode LCD display service."
echo "It will:"
echo "  - Download install.sh, LCD_2inch8.py and moode_lcd.py from GitHub"
echo "  - Enable SPI if not already enabled"
echo "  - Copy driver files to /home/moode/waveshare-2.8/Python/"
echo "  - Create and enable moode-lcd.service"
echo

if ! confirm "Proceed with MOODE-LCD installation? [y/N]: "; then
  info "Cancelled by user."
  exit 0
fi

info "Creating work directory: $WORK_DIR"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

info "Downloading install.sh..."
wget -q "$GITHUB_RAW/install.sh" -O install.sh || fail "Failed to download install.sh"
chmod +x install.sh

info "Downloading LCD_2inch8.py..."
wget -q "$GITHUB_RAW/LCD_2inch8.py" -O LCD_2inch8.py || fail "Failed to download LCD_2inch8.py"

info "Downloading moode_lcd.py..."
wget -q "$GITHUB_RAW/moode_lcd.py" -O moode_lcd.py || fail "Failed to download moode_lcd.py"

info "Files downloaded to $WORK_DIR"
info "Handing off to install.sh..."
echo

exec bash install.sh
