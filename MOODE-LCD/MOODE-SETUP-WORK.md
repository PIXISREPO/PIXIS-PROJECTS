# MOODE Setup Work Log

Documentation of moOde LCD setup process and points to note for future Player Work Items.

## What We Built

Created MOODE-LCD project with:
- moode_lcd.py - LCD display script with album art + metadata
- install.sh - Complete installer (SPI + waveshare + service)
- README.md - Project overview
- setup.md - Detailed setup guide

## Installation Process That Works

On a fresh moOde setup, these steps work:

1. Enable SPI in /boot/firmware/config.txt:
   dtparam=spi=on
   dtoverlay=spi-spidev

2. Install waveshare-2.8:
   cd /home/moode
   git clone https://github.com/alanb128/Waveshare-2.8-inch-LCD.git waveshare-2.8

3. Add moode user to gpio and spi groups:
   usermod -aG gpio,spi moode

4. Copy moode_lcd.py to waveshare Python directory:
   cp moode_lcd.py /home/moode/waveshare-2.8/Python/

5. Create systemd service file at /etc/systemd/system/moode-lcd.service:
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

6. Reload and start service:
   systemctl daemon-reload
   systemctl enable moode-lcd.service
   systemctl start moode-lcd.service

## Points to Note for Future Player Work Items

### 1. User Permissions Are Critical

- The player user (moode, volumio, etc.) MUST be in gpio and spi groups
- Without this, gpiozero fails with BadPinFactory error
- Always add: usermod -aG gpio,spi <player_user>

### 2. Service Type Must Be "simple"

- Use Type=simple not Type=oneshot
- Type=simple keeps the service running continuously
- Type=oneshot exits after script completes (service becomes inactive)

### 3. Restart Settings Prevent Crashes

- Always include Restart=on-failure and RestartSec=5
- This auto-restarts the service if it crashes
- Without this, a crash leaves the service dead

### 4. WorkingDirectory Must Match Script Location

- WorkingDirectory must be the Python directory containing the script
- ExecStart must use full path to script
- Example:
  WorkingDirectory=/home/moode/waveshare-2.8/Python
  ExecStart=/usr/bin/python3 /home/moode/waveshare-2.8/Python/moode_lcd.py

### 5. PWM vs DigitalOutputDevice for Backlight

- PWMOutputDevice requires PWM-supporting pin factory (RPi.GPIO or pigpio)
- NativeFactory (gpiozero fallback) does NOT support PWM
- Use DigitalOutputDevice for backlight to avoid PWM errors
- Trade-off: Backlight is always ON (no PWM dimming), but no flicker

### 6. SPI Must Be Enabled Before First Run

- Add dtparam=spi=on and dtoverlay=spi-spidev to config.txt
- Reboot after enabling SPI
- Verify: ls -la /dev/spidev* shows spidev0.0 and spidev0.1

### 7. waveshare-2.8 Directory Structure

Expected path: /home/<player_user>/waveshare-2.8/Python/
- Contains LCD_2inch8.py (display driver)
- Place player script here (moode_lcd.py, volumio_lcd.py, etc.)

### 8. Pull Player-Specific API Calls

- moOde uses: http://localhost/command/?cmd=status and cmd=currentsong
- Volumio uses different API (Docker-based)
- Each player needs its own script with correct API calls
- Do NOT share scripts between players

### 9. Radio Paradise Integration

- moOde: Use RP API at https://api.radioparadise.com/api/now_playing?chan=0
- Works well for RP internet radio streams
- Gets rich metadata + cover art

### 10. Service Name Should Be Player-Specific

- moOde: moode-lcd.service
- Volumio: volumio-lcd.service
- Avoid confusion from mixing player names

### 11. Installer Should Handle All Prerequisites

Good installer does:
- Enables SPI if not enabled
- Installs waveshare if missing
- Adds user to gpio,spi groups
- Creates service file
- Starts service

Bad installer:
- Assumes prerequisites are already set up
- Requires manual steps before running

### 12. Testing Strategy

- Test on fresh player setup (not existing setup with prior config)
- This catches missing prerequisites in installer
- Moode3 had prior config (SPI enabled, groups added, waveshare installed)
- Fresh Moode4 will test real installer

## Common Errors and Fixes

### BadPinFactory: Unable to load default pin factory

Cause: User not in gpio/spi groups
Fix: usermod -aG gpio,spi <user>

### PinPWMUnsupported: PWM not supported on pin GPIO18

Cause: Using PWMOutputDevice with NativeFactory
Fix: Use DigitalOutputDevice instead (backlight always ON)

### Service exits immediately (inactive/dead)

Cause: Type=oneshot or script exits
Fix: Use Type=simple and ensure script has while True loop

### spidev not found

Cause: SPI not enabled
Fix: Add dtparam=spi=on and dtoverlay=spi-spidev to config.txt, reboot

### Permission denied on .lgd-nfy files

Cause: lgpio trying to create files in wrong directory
Fix: Install RPi.GPIO or pigpio for better pin factory

## Player-Specific API Reference

### moOde API

Status: http://localhost/command/?cmd=status
Current Song: http://localhost/command/?cmd=currentsong
Cover Art: http://localhost/coverart.php

Response format (JSON):
- state: play/pause/stop
- Name: station name (for internet radio)
- Title: artist - title (for internet radio)

### Volumio API

Different API (Docker-based, web interface)
Not compatible with moOde script

## Files Created

- moode_lcd.py - Main display script
- install.sh - Complete installer
- README.md - Project overview
- setup.md - Setup guide
- MOODE-SETUP-WORK.md - This work log

## Next Player Items

When building SPI-LCD-TOUCH or other Player LCD projects:

1. Use this work log as reference for service configuration
2. Follow the installation process above
3. Adapt moode_lcd.py for new player (change API calls)
4. Update install.sh with correct player user name
5. Test on fresh player setup
6. Document any new issues in this work log

## Version History

- 2026-06-20: Initial moOde LCD setup completed
  - Service running, LCD displays album art + metadata
  - Installer created with SPI + waveshare installation
  - Backlight uses DigitalOutputDevice (no PWM flicker)

- 2026-06-21: Auto-resume playback after reboot documented
  - Tested: LCD shows correct album art and metadata on reboot
  - Issue: Playback paused after reboot, requires manual Play tap
  - Fix: mpd-autoplay.service (Option 1, recommended)

---

## Auto-Resume Playback After Reboot

By default, MPD saves its state (playlist, position, volume) on shutdown but deliberately boots into a **paused** state. After a reboot the LCD correctly shows album art and metadata, but playback does not resume automatically. Two approaches fix this.

---

### Option 1 — `mpc play` on Boot via systemd (Recommended)

A small oneshot systemd service fires `mpc play` after MPD has fully started. This is the preferred approach because it works for both local files and live radio streams without touching moOde's MPD configuration.

**Create the service file:**

```bash
sudo nano /etc/systemd/system/mpd-autoplay.service
```

**Paste the following:**

```ini
[Unit]
Description=MPD Auto Play on Boot
After=mpd.service
Requires=mpd.service

[Service]
Type=oneshot
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/mpc play
User=mpd
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

**Enable and start the service:**

```bash
sudo systemctl enable mpd-autoplay.service
sudo systemctl start mpd-autoplay.service
```

The `sleep 5` delay gives MPD time to fully initialise before the play command fires. This value can be tuned down if boot completes faster on your hardware.

> **Radio streams:** MPD saves the stream URL and playlist position across reboots. `mpc play` will reconnect to the last stream automatically.

---

### Option 2 — Disable `restore_paused` in `mpd.conf`

MPD has a built-in `restore_paused` setting that controls boot behaviour. If set to `"yes"`, MPD will always boot paused.

**Check the current setting:**

```bash
grep -i restore /etc/mpd.conf
```

**If `restore_paused "yes"` is present**, change it to `"no"`:

```bash
sudo nano /etc/mpd.conf
# Change:  restore_paused "yes"
# To:      restore_paused "no"
```

**Restart MPD to apply:**

```bash
sudo systemctl restart mpd
```

> **Note:** Editing `mpd.conf` directly may conflict with moOde's internal configuration management. Option 1 is safer for moOde installations as it does not modify any moOde-managed files.

---

### Comparison

| | Option 1 (systemd service) | Option 2 (mpd.conf) |
|---|---|---|
| Works for streams | ✅ Yes | ✅ Yes |
| Works for local files | ✅ Yes | ✅ Yes |
| Touches moOde config | ❌ No | ⚠️ Yes |
| Survives moOde updates | ✅ Yes | ⚠️ May be overwritten |
| Adjustable delay | ✅ Yes (sleep N) | ❌ No |
| Recommended | ✅ **Yes** | Only if Option 1 fails |

---

### Test Results

- Reboot confirmed: LCD shows correct album art and metadata on return ✅
- Radio stream (Flux FM Electronic Chillout) reconnects correctly ✅
- API calls (`currentsong`, `status`) responding correctly over localhost ✅
- LCD and web UI displaying identical playback state ✅
