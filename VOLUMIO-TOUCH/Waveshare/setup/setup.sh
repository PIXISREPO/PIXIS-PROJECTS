#!/bin/bash
set -euo pipefail

# VOLUMIO-TOUCH installer
# Run on the Pi as:
#   cd /home/volumio/PIXIS/VOLUMIO-TOUCH
#   sudo ./setup.sh

# Ensure we're on a Pi with systemd and that VOLUMIO-LCD is present
if ! command -v systemctl >/dev/null; then
    echo "ERROR: systemd not found; this install requires systemd." >&2
    exit 1
fi

if ! systemctl list-units --type=service | grep -q volumio-lcd; then
    echo "WARNING: volumio-lcd.service not found; LCD is not running." >&2
    echo "Run this setup only after VOLUMIO-LCD is installed and verified." >&2
fi

echo "=== Installing VOLUMIO-TOUCH on Volumio ==="

# (1) Ensure uinput is available and loaded
if ! grep -q uinput /etc/modules 2>/dev/null; then
    echo "uinput" | sudo tee -a /etc/modules
fi

if ! lsmod | grep -q uinput; then
    sudo modprobe uinput
fi

# (2) Install python3-uinput if not present
if ! dpkg -l | grep -q python3-uinput; then
    echo "Installing python3-uinput..."
    sudo apt-get update
    sudo apt-get install -y python3-uinput
fi

# (3) Create target dirs on the Pi (if run from /home/volumio/PIXIS/VOLUMIO-TOUCH)
TARGET_ROOT="/home/volumio/PIXIS/VOLUMIO-TOUCH"
echo "Installing VOLUMIO-TOUCH files to ${TARGET_ROOT}"
sudo mkdir -p "${TARGET_ROOT}/bin"

# Copy Python modules (assumes this script is run from the project root)
sudo cp -f bin/waveshare_cst328_touch.py "${TARGET_ROOT}/bin/"
sudo cp -f bin/volumio_lcd_ui.py      "${TARGET_ROOT}/bin/"

# (4) Install systemd service
SERVICE_FILE="/etc/systemd/system/volumio-touch.service"
cat << 'EOF' | sudo tee "${SERVICE_FILE}"
[Unit]
Description=Volumio CST328 Touch + Volumio‑LCD Overlays
After=volumio-lcd.service
Requires=volumio-lcd.service

[Service]
Type=simple
User=volumio
Group=volumio
WorkingDirectory=/home/volumio/PIXIS/VOLUMIO-TOUCH/bin
ExecStart=/usr/bin/python3 waveshare_cst328_touch.py
ExecStart=/usr/bin/python3 volumio_lcd_ui.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable volumio-touch.service

# (5) Mark installed state
sudo mkdir -p /var/lib/volumio-touch
sudo touch /var/lib/volumio-touch/installed

echo ""
echo "=== VOLUMIO-TOUCH installation complete ==="
echo "You can now:"
echo "  sudo systemctl start volumio-touch.service"
echo "  sudo systemctl status volumio-touch.service"
echo ""
echo "To roll back to the last‑known‑good VOLUMIO-LCD state:"
echo "  sudo /home/volumio/rollback_volumio_touch.sh"

