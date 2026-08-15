#!/bin/bash
set -euo pipefail

REPO="https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/main"
STAGE="/tmp/pixis/stage/VOLUMIO-LCD"

mkdir -p "$STAGE/systemd"
mkdir -p "$STAGE/scripts"
mkdir -p "$STAGE/config"
mkdir -p "$STAGE/waveshare-2.8/Python"

fetch() {
  local src="$1"
  local dst="$2"
  curl -fsSL "$REPO/$src" -o "$dst"
}

fetch "VOLUMIO-LCD/install.sh" "$STAGE/install.sh"
fetch "VOLUMIO-LCD/systemd/pixis-installer.service" "$STAGE/systemd/pixis-installer.service"
fetch "VOLUMIO-LCD/systemd/volumio-lcd.service" "$STAGE/systemd/volumio-lcd.service"
fetch "VOLUMIO-LCD/scripts/pixis-installer.sh" "$STAGE/scripts/pixis-installer.sh"
fetch "VOLUMIO-LCD/scripts/PiInstaller.sh" "$STAGE/scripts/PiInstaller.sh"
fetch "VOLUMIO-LCD/config/userconfig.txt" "$STAGE/config/userconfig.txt"
fetch "VOLUMIO-LCD/config/volumioconfig.txt" "$STAGE/config/volumioconfig.txt"

fetch "VOLUMIO-LCD/waveshare-2.8/Python/volumio_lcd.py" "$STAGE/waveshare-2.8/Python/volumio_lcd.py"
fetch "VOLUMIO-LCD/waveshare-2.8/Python/LCD_2inch8.py" "$STAGE/waveshare-2.8/Python/LCD_2inch8.py"
fetch "VOLUMIO-LCD/waveshare-2.8/Python/2inch8_LCD_test.py" "$STAGE/waveshare-2.8/Python/2inch8_LCD_test.py"
fetch "VOLUMIO-LCD/waveshare-2.8/Python/Touch_2inch8.py" "$STAGE/waveshare-2.8/Python/Touch_2inch8.py"
fetch "VOLUMIO-LCD/waveshare-2.8/Python/test_fill.py" "$STAGE/waveshare-2.8/Python/test_fill.py"

chmod +x "$STAGE/install.sh"
chmod +x "$STAGE/scripts/pixis-installer.sh"
chmod +x "$STAGE/scripts/PiInstaller.sh"

echo "Bootstrap staged in $STAGE"

