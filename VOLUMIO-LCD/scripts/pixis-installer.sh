#!/bin/bash
set -euo pipefail

MARKER="/var/lib/pixis/installer.done"
LOG="/var/lib/pixis/installer.log"

if [ -f "$MARKER" ]; then
  exit 0
fi

mkdir -p /var/lib/pixis
date >> "$LOG"
echo "PIXIS first boot installer ran" >> "$LOG"
touch "$MARKER"
systemctl disable pixis-installer.service || true
exit 0
