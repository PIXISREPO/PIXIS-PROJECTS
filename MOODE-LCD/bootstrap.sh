#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER="${ROOT}/install.sh"
PLAYER_SCRIPT="${ROOT}/moode_lcd.py"

info() {
  echo "[moode-bootstrap] $*"
}

fail() {
  echo "[moode-bootstrap] ERROR: $*" >&2
  exit 1
}

require_file() {
  local f="$1"
  [[ -f "$f" ]] || fail "Missing required file: $f"
}

confirm() {
  local prompt="${1:-Proceed? [y/N]: }"
  local reply
  read -r -p "$prompt" reply
  case "${reply,,}" in
    y|yes) return 0 ;;
    *) return 1 ;;
  esac
}

require_file "$INSTALLER"
require_file "$PLAYER_SCRIPT"

chmod +x "$INSTALLER"

echo
echo "PIXIS MOODE-LCD Bootstrap"
echo
echo "This bootstrap will:"
echo "  1. Run the MOODE-LCD installer from:"
echo "     $INSTALLER"
echo
echo "The installer is expected to:"
echo "  - Check and enable SPI in /boot/firmware/config.txt if needed"
echo "  - Install Waveshare support files if missing"
echo "  - Copy moode_lcd.py into /home/moode/waveshare-2.8/Python/"
echo "  - Create /etc/systemd/system/moode-lcd.service"
echo "  - Add user 'moode' to gpio and spi groups"
echo "  - Reload systemd, enable the service, and try to start it"
echo
echo "Required files found:"
echo "  - $INSTALLER"
echo "  - $PLAYER_SCRIPT"
echo

if ! confirm "Proceed with MOODE-LCD installation? [y/N]: "; then
  info "Cancelled by user."
  exit 0
fi

info "Handing off to install.sh..."
exec sudo bash "$INSTALLER"

