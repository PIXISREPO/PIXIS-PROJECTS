# MOODE Setup Work Log

Documentation of moOde LCD setup process and points to note for future Player Work Items.

## What We Built

Created MOODE-LCD project with:
- moode_lcd.py - LCD display script with album art + metadata
- install.sh - Complete installer (SPI + waveshare + service)
- README.md - Project overview
- setup.md - Detailed setup guide
- bootstrap.sh - One-step installer bootstrap
- MOODE-SETUP-WORK.md - This work log

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

## Installer and Bootstrap Notes

The current repo includes a documented one-step install path:

```bash
cd /tmp
wget https://raw.githubusercontent.com/PIXISREPO/PIXIS-PROJECTS/main/MOODE-LCD/bootstrap.sh
chmod +x bootstrap.sh
sudo bash bootstrap.sh
```

The bootstrap downloads `install.sh`, `LCD_2inch8.py`, and `moode_lcd.py` from GitHub into `/tmp/moode-lcd-install`, confirms with the user, then hands off to `install.sh`.

The installer does the following:
- Installs dependencies: `wget`, `unzip`, `python3-pip`, `python3-pil`, `python3-requests`, `python3-gpiozero`, and `mpc`
- Attempts to install `spidev` and `RPi.GPIO`
- Enables `dtparam=spi=on` if needed
- Comments out `vc4-kms-v3d` if present for headphone jack compatibility
- Copies `LCD_2inch8.py` and `moode_lcd.py` into `/home/moode/waveshare-2.8/Python/`
- Creates and enables `moode-lcd.service`
- Adds user `moode` to `gpio` and `spi`
- Seeds first boot with Radio Paradise Mellow Mix
- Creates and enables `mpd-autoplay.service`
- Reboots automatically after a short countdown

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

- moOde uses localhost command endpoints and player state fields
- Volumio uses different API (Docker-based)
- Each player needs its own script with correct API calls
- Do NOT share scripts between players

### 9. Radio Paradise Integration

- Radio Paradise works well as a validation stream because it supplies rich metadata and remote cover art
- It was used successfully to validate both metadata display and real album art fetching

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
- A previously configured box can hide missing installer steps
- Fresh installs are the only real validation of the bootstrap path

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
Local Cover Art Fallback: http://localhost/coverart.php

Relevant state fields used by the LCD script:
- state: play/pause/stop
- status: fallback state field in some code paths
- Name: station name (for internet radio)
- Title: artist - title (for internet radio)
- coverurl: preferred album art source when present
- albumart: secondary album art source when present

### Album Art Fetch Order

This point is important and was confirmed during the 2026-06-29 debugging session.

The LCD script now fetches album art in this order:
1. `coverurl` from the moOde/player state
2. `albumart` from the same state if `coverurl` is missing or invalid
3. `DEFAULT_COVER_URL` as the final fallback

This means:
- The LCD does NOT primarily use `http://localhost/coverart.php` anymore
- The local moOde cover art endpoint is now a fallback path only
- For Radio Paradise, the correct real album art came from the remote `coverurl` metadata URL

In code, this is handled by:

```python
def resolve_albumart_url(state):
    coverurl = (state.get("coverurl", "") or "").strip()
    if coverurl.startswith("http://") or coverurl.startswith("https://"):
        return coverurl

    albumart = (state.get("albumart", "") or "").strip()
    if albumart.startswith("http://") or albumart.startswith("https://"):
        return albumart

    return DEFAULT_COVER_URL
```

### Volumio API

Different API (Docker-based, web interface)
Not compatible with moOde script

## Files Created

- moode_lcd.py - Main display script
- install.sh - Complete installer
- bootstrap.sh - Bootstrap installer
- README.md - Project overview
- setup.md - Setup guide
- MOODE-SETUP-WORK.md - This work log

## Version History

- 2026-06-20: Initial moOde LCD setup completed
  - Service running, LCD displays album art + metadata
  - Installer created with SPI + waveshare installation
  - Backlight uses DigitalOutputDevice (no PWM flicker)

- 2026-06-21: Auto-resume playback after reboot documented
  - Tested: LCD shows correct album art and metadata on reboot
  - Issue: Playback paused after reboot, requires manual Play tap
  - Fix: mpd-autoplay.service (Option 1, recommended)

- 2026-06-29: Playback state and album art source fixes completed
  - Root cause 1: playback loop needed to prefer `state` over `status`
  - Root cause 2: album art logic needed to prefer `coverurl` over local/default art
  - Validated: LCD now shows metadata correctly
  - Validated: LCD now enters playback screen correctly
  - Validated: LCD now shows the real album art instead of the default moOde image
  - Repo updated and pushed to GitHub
  - Commit pushed: `0fc3089` - `Fix playback state and prefer remote cover art`

## 2026-06-29 Session Notes

### Problem Summary

A fresh round of testing found that the LCD service was partially working:
- The LCD hardware initialised and the script was running
- Metadata could be shown after fixes
- Real album art was not shown at first; the display fell back to the default moOde image

### Root Causes Found

#### 1. Playback state detection was using the wrong field

The playback loop was checking `status` rather than trusting `state` first.

On the working Pi, the running script fix was:

```python
state = str(song_data.get("state", status_data.get("state", "")) or "").lower()
```

In the repo version, the equivalent fix is:

```python
status = str(state.get("state", state.get("status", "stop")) or "stop").lower()
```

This corrected the issue where the LCD stayed on the idle or waiting path even though playback was active.

#### 2. Album art fetch logic was using the wrong source

The earlier running script on the Pi used a local fetch routine that only requested the local moOde cover endpoint. That was enough to show the default image, but not always the real remote cover for Radio Paradise.

The working fix was to prefer the `coverurl` value from track metadata first, and only fall back to moOde's local or default cover art URL if necessary.

### Validation Results

After applying the fixes on the Pi:
- The LCD showed metadata correctly
- The LCD switched into the playback screen correctly
- The LCD displayed the real album art instead of the default moOde image

### Repo Update Completed

The local repo at `PIXIS-PROJECTS/MOODE-LCD` was patched and pushed to GitHub.

Committed changes included:
- Prefer `coverurl` over `albumart` or default art in `resolve_albumart_url(state)`
- Prefer `state` over `status` for playback detection in the main loop
- The pushed commit was `0fc3089` with message: `Fix playback state and prefer remote cover art`

### Fresh Install Notes

A clean install should verify these exact lines in the installed file:

```python
status = str(state.get("state", state.get("status", "stop")) or "stop").lower()
```

```python
coverurl = (state.get("coverurl", "") or "").strip()
```

## Auto-Resume Playback After Reboot

By default, MPD saves its state (playlist, position, volume) on shutdown but deliberately boots into a paused state. After a reboot the LCD can show album art and metadata, but playback may not resume automatically unless a play command is issued.

### Option 1 - `mpc play` on Boot via systemd (Recommended)

A small oneshot systemd service fires `mpc play` after MPD has fully started. This is the preferred approach because it works for both local files and live radio streams without touching moOde's MPD configuration.

Create the service file:

```bash
sudo nano /etc/systemd/system/mpd-autoplay.service
```

Paste the following:

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

Enable and start the service:

```bash
sudo systemctl enable mpd-autoplay.service
sudo systemctl start mpd-autoplay.service
```

The `sleep 5` delay gives MPD time to fully initialise before the play command fires. This value can be tuned down if boot completes faster on your hardware.

## Next Player Items

When building SPI-LCD-TOUCH or other Player LCD projects:

1. Use this work log as reference for service configuration
2. Follow the installation process above
3. Adapt moode_lcd.py for new player by changing API calls and state handling
4. Update install.sh with correct player user name
5. Test on a fresh player setup
6. Document any new issues in this work log
