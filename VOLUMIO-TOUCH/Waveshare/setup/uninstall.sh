#!/bin/bash
set -euo pipefail

# VOLUMIO‑TOUCH uninstall / rollback
# Run on the Pi as:
#   cd /home/volumio/PIXIS/VOLUMIO-TOUCH
#   sudo ./uninstall.sh
# or for users later:
#   wget -O - https://.../VOLUMIO-TOUCH/uninstall.sh | bash

echo "=== Uninstalling VOLUMIO-TOUCH ==="

# Stop service if running
if systemctl is-active --quiet volumio-touch.service; then
    echo "Stopping volumio-touch.service..."
    sudo systemctl stop volumio-touch.service
fi

# Disable and remove service unit
if systemctl list-unit-files | grep -q volumio-touch.service; then
    echo "Disabling and removing volumio-touch.service..."
    sudo systemctl disable volumio-touch.service
    sudo rm -f /etc/systemd/system/volumio-touch.service
    sudo systemctl daemon-reload
fi

# Remove VOLUMIO‑TOUCH runtime files
TARGET_ROOT="/home/volumio/PIXIS/VOLUMIO-TOUCH"
if [ -d "${TARGET_ROOT}" ]; then
    echo "Removing VOLUMIO‑TOUCH files..."
    sudo rm -rf "${TARGET_ROOT}"
fi

# Clean up state (optional)
if [ -d "/var/lib/volumio-touch" ]; then
    echo "Removing VOLUMIO‑TOUCH state..."
    sudo rm -rf /var/lib/volumio-touch
fi

# Do NOT remove python3‑uinput or uinput from /etc/modules;
# they are harmless and may be used by other apps.

echo ""
echo "=== VOLUMIO-TOUCH removed ==="
echo "VOLUMIO-LCD and core Volumio are unchanged."
echo "To verify: systemctl status volumio-lcd.service"

