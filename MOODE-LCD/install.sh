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
apt-get install -y git wget unzip python3-pip python3-pil python3-requests python3-gpiozero

pip3 install --break-system-packages spidev 2>/dev/null || pip3 install spidev 2>/dev/null || true
pip3 install --break-system-packages RPi.GPIO 2>/dev/null || pip3 install RPi.GPIO 2>/dev/null || true

echo "[INFO] Dependencies installed"

# Step 2: Enable SPI if not already enabled
echo "[INFO] Checking SPI configuration..."

SPI_ADDED=false
if ! grep -q "dtparam=spi=on" "$CONFIG_FILE" 2>/dev/null; then
    echo "[INFO] SPI not enabled. Enabling SPI..."
    echo "" >> "$CONFIG_FILE"
    echo "# PIXIS MOODE-LCD: SPI display" >> "$CONFIG_FILE"
    echo "dtparam=spi=on" >> "$CONFIG_FILE"
    echo "dtoverlay=spi-spidev" >> "$CONFIG_FILE"
    SPI_ADDED=true
    echo "[INFO] SPI enabled. Reboot required after installation."
else
    echo "[INFO] SPI already enabled"
fi

# Step 3: Install Waveshare 2.8 files if not present
echo "[INFO] Checking Waveshare 2.8 driver..."

if [[ ! -d "${WAVESHARE_DIR}" ]]; then
    echo "[INFO] Waveshare driver not found. Cloning from GitHub..."

    git clone --depth=1 https://github.com/waveshare/2.8inch_LCD_for_Raspberry_Pi.git /tmp/waveshare-2.8-src || {
        echo "[ERROR] Failed to clone Waveshare driver from GitHub"
        echo "[INFO]  Check internet connectivity and try again."
        exit 1
    }

    PYTHON_SRC="$(find /tmp/waveshare-2.8-src -type d -name Python | head -1)"
    if [[ -z "$PYTHON_SRC" ]]; then
        echo "[ERROR] Python directory not found in cloned Waveshare repo"
        echo "[INFO]  Repo contents:"
        ls /tmp/waveshare-2.8-src/
        exit 1
    fi

    mkdir -p /home/moode/waveshare-2.8
    cp -r "$PYTHON_SRC" /home/moode/waveshare-2.8/Python
    chown -R moode:moode /home/moode/waveshare-2.8

    rm -rf /tmp/waveshare-2.8-src

    echo "[INFO] Waveshare driver installed to ${WAVESHARE_DIR}"
else
    echo "[INFO] Waveshare driver found: ${WAVESHARE_DIR}"
fi

# Step 4: Copy moode_lcd.py
echo "[INFO] Installing moode_lcd.py..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "${SCRIPT_DIR}/moode_lcd.py" "${WAVESHARE_DIR}/moode_lcd.py"
chown moode:moode "${WAVESHARE_DIR}/moode_lcd.py"

echo "[INFO] Copied moode_lcd.py to ${WAVESHARE_DIR}"

# Step 5: Create systemd service file
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

# Step 6: Add moode to gpio and spi groups
echo "[INFO] Adding moode user to gpio and spi groups..."
usermod -aG gpio,spi moode 2>/dev/null || true
echo "[INFO] moode user permissions updated"

# Step 7: Reload systemd and start service
echo "[INFO] Enabling moode-lcd.service..."
systemctl daemon-reload
systemctl enable moode-lcd.service

if [[ "$SPI_ADDED" == "true" ]]; then
    echo ""
    echo "============================================================"
    echo " REBOOT REQUIRED"
    echo " SPI was just enabled. You must reboot before the LCD"
    echo " service will start correctly."
    echo ""
    echo " After reboot, verify SPI is active:"
    echo "   ls -la /dev/spidev*"
    echo ""
    echo " Then start the service:"
    echo "   sudo systemctl start moode-lcd.service"
    echo "   sudo systemctl status moode-lcd.service"
    echo "============================================================"
    echo ""
else
    echo "[INFO] Starting moode-lcd.service..."
    systemctl start moode-lcd.service
    sleep 2
    systemctl status moode-lcd.service
    echo ""
    echo "MOODE-LCD installed and running!"
fi

echo ""
echo "Useful commands:"
echo "  sudo systemctl status moode-lcd.service"
echo "  sudo journalctl -u moode-lcd.service -f"
echo ""
