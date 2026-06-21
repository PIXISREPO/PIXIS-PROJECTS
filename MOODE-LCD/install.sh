#!/bin/bash
set -e

echo "PIXIS MOODE-LCD Installer"
echo ""

WAVESHARE_DIR="/home/moode/waveshare-2.8/Python"
SERVICE_FILE="/etc/systemd/system/moode-lcd.service"
CONFIG_FILE="/boot/firmware/config.txt"

# Step 1: Install dependencies
echo "[INFO] Installing dependencies..."
apt-get update -qq
apt-get install -y wget unzip python3-pip python3-pil python3-requests python3-gpiozero

pip3 install --break-system-packages spidev 2>/dev/null || pip3 install spidev 2>/dev/null || true
pip3 install --break-system-packages RPi.GPIO 2>/dev/null || pip3 install RPi.GPIO 2>/dev/null || true

echo "[INFO] Dependencies installed"

# Step 2: Enable SPI if not already enabled
echo "[INFO] Checking SPI configuration..."

if ! grep -q "dtparam=spi=on" "$CONFIG_FILE" 2>/dev/null; then
    echo "[INFO] SPI not enabled. Enabling SPI..."
    echo "" >> "$CONFIG_FILE"
    echo "# PIXIS MOODE-LCD: SPI display" >> "$CONFIG_FILE"
    echo "dtparam=spi=on" >> "$CONFIG_FILE"
    echo "[INFO] SPI enabled."
else
    echo "[INFO] SPI already enabled"
fi

# Step 3: Install driver files
echo "[INFO] Setting up display driver directory..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "${WAVESHARE_DIR}"

echo "[INFO] Copying LCD_2inch8.py driver..."
cp "${SCRIPT_DIR}/LCD_2inch8.py" "${WAVESHARE_DIR}/LCD_2inch8.py"

echo "[INFO] Copying moode_lcd.py..."
cp "${SCRIPT_DIR}/moode_lcd.py" "${WAVESHARE_DIR}/moode_lcd.py"

chown -R moode:moode /home/moode/waveshare-2.8
echo "[INFO] Driver files installed to ${WAVESHARE_DIR}"

# Step 4: Create systemd service file
echo "[INFO] Creating systemd service..."

cat > "${SERVICE_FILE}" << 'SVCEOF'
[Unit]
Description=PIXIS Moode LCD display service
After=network.target
Wants=network.target

[Service]
Type=simple
User=moode
Group=moode
WorkingDirectory=/home/moode/waveshare-2.8/Python
ExecStart=/usr/bin/python3 /home/moode/waveshare-2.8/Python/moode_lcd.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF

echo "[INFO] Created service file: ${SERVICE_FILE}"

# Step 5: Add moode to gpio and spi groups
echo "[INFO] Adding moode user to gpio and spi groups..."
usermod -aG gpio,spi moode 2>/dev/null || true
echo "[INFO] moode user permissions updated"

# Step 6: Reload systemd and enable service
echo "[INFO] Enabling moode-lcd.service..."
systemctl daemon-reload
systemctl enable moode-lcd.service

echo ""
echo "============================================================"
echo " MOODE-LCD INSTALLED SUCCESSFULLY"
echo "============================================================"
echo ""
echo " A reboot is required to ensure SPI and group"
echo " permissions are fully active."
echo ""
echo " Rebooting in 10 seconds... (Ctrl+C to cancel)"
echo ""

for i in $(seq 10 -1 1); do
    printf "  %2d...\r" "$i"
    sleep 1
done

echo ""
echo "[INFO] Rebooting now."
reboot
