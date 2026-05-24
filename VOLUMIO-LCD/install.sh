#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USERCONFIG="/boot/userconfig.txt"
VOLUMIOCONFIG="/boot/volumioconfig.txt"
LOGDIR="/var/log/pixis"
MARKER="/tmp/pixis/volumio-lcd.reboot-required"
PACKAGES=(python3-pil python3-spidev python3-numpy python3-gpiozero)

log() {
  echo "[volumio-lcd] $*"
}

require_file() {
  [ -f "$1" ] || {
    echo "Missing required file: $1" >&2
    exit 1
  }
}

ensure_line() {
  local line="$1"
  local file="$2"
  touch "$file"
  grep -qxF "$line" "$file" || echo "$line" >> "$file"
}

if [ ! -d "$ROOT" ]; then
  echo "Missing staged payload: $ROOT" >&2
  exit 1
fi

for f in \
  "$ROOT/systemd/pixis-installer.service" \
  "$ROOT/systemd/volumio-lcd.service" \
  "$ROOT/scripts/pixis-installer.sh" \
  "$ROOT/scripts/PiInstaller.sh" \
  "$ROOT/config/userconfig.txt" \
  "$ROOT/config/volumioconfig.txt" \
  "$ROOT/waveshare-2.8"
do
  require_file "$f"
done

install -d /etc/systemd/system
install -d /usr/local/sbin
install -d /usr/local/bin
install -d /boot
install -d "$LOGDIR"
install -d /tmp/pixis

install -m 0644 "$ROOT/systemd/pixis-installer.service" /etc/systemd/system/pixis-installer.service
install -m 0644 "$ROOT/systemd/volumio-lcd.service" /etc/systemd/system/volumio-lcd.service
install -m 0755 "$ROOT/scripts/pixis-installer.sh" /usr/local/sbin/pixis-installer.sh
install -m 0755 "$ROOT/scripts/PiInstaller.sh" /usr/local/bin/PiInstaller.sh

cp -f "$ROOT/config/userconfig.txt" "$USERCONFIG"
cp -f "$ROOT/config/volumioconfig.txt" "$VOLUMIOCONFIG"

ensure_line 'dtparam=spi=on' "$USERCONFIG"
ensure_line 'dtoverlay=spi-spidev' "$USERCONFIG"

install -d /home/volumio/waveshare-2.8
cp -a "$ROOT/waveshare-2.8/." /home/volumio/waveshare-2.8/
chown -R volumio:volumio /home/volumio/waveshare-2.8 || true

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y "${PACKAGES[@]}"

systemctl daemon-reload

if [ ! -e /dev/spidev0.0 ]; then
  log "SPI device /dev/spidev0.0 not present. Boot config updated; reboot required before enabling volumio-lcd.service."
  date >> "$LOGDIR/installer.log"
  echo "PIXIS staged install completed; reboot required for SPI" >> "$LOGDIR/installer.log"
  touch "$MARKER"
  touch "$LOGDIR/installer.done"
  exit 0
fi

rm -f "$MARKER"
systemctl enable volumio-lcd.service
systemctl restart volumio-lcd.service

date >> "$LOGDIR/installer.log"
echo "PIXIS staged install completed" >> "$LOGDIR/installer.log"
touch "$LOGDIR/installer.done"

