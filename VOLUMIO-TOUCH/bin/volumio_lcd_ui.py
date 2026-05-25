#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
Volumio‑LCD touch UI overlay:
- Bottom strip tap → show Back / Play‑Pause / Forward / Browse.
- Speaker icon → horizontal volume slider.
- Album‑art tap → Mute/Unmute with MUTE icon overlay.
"""

from PIL import Image, ImageDraw, ImageFont
import time
import sys
import requests

# Volumio HTTP API endpoint (assuming local backend)
VOLUMIO_API = "http://localhost:3000/api/v1"

# Coordinate layout for 240x320
ART_RECT     = (0, 0, 240, 240)      # 240×240 album art
META_STRIP   = (0, 240, 240, 80)     # 240×80 bottom metadata/touch strip
SLIDER_RECT  = (0, 270, 240, 30)     # 240×30 volume slider
SPEAKER_ICON = (10, 270, 34, 34)     # 24×24 approx speaker icon
BROWSE_ICON  = (190, 270, 40, 30)    # 40×30 browse icon

# Globals
current_overlay = None

# --- Utility functions ---


def is_in(rect, x, y):
    """Check if point (x,y) is inside rect (x, y, w, h)."""
    rx, ry, rw, rh = rect
    return rx <= x < rx + rw and ry <= y < ry + rh


def load_overlay_art():
    """Load your standard 240x240 album‑art image (stub)."""
    # Replace with your actual loader; this is just a stub.
    return Image.new("RGB", (240, 240), "black")


def draw_mute_overlay(canvas, drawing, art_image):
    """Draw MUTE icon on top of the album‑art."""
    # You can keep the base album‑art as art_image,
    # and draw on top of it for the overlay.
    width, height = art_image.size

    # Semi‑transparent black overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 150))
    art_image = art_image.copy()
    art_image.paste(overlay, (0, 0), overlay)

    # Draw a MUTE icon (simplified as a circle with slash)
    draw = ImageDraw.Draw(art_image)
    cx, cy = width // 2, height // 2
    radius = 30
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline="red", width=3)
    draw.line((cx - radius, cy - radius, cx + radius, cy + radius), fill="red", width=4)

    return art_image


def clear_overlay(art_image):
    """Return the base album‑art without overlay."""
    return art_image


# --- Volumio API helpers ---


def volumio_command(cmd_data):
    """Send a command to Volumio backend."""
    try:
        resp = requests.post(f"{VOLUMIO_API}/command", json=cmd_data)
        if resp.status_code != 200:
            print("Volumio API error:", resp.status_code, resp.text)
    except Exception as e:
        print("Volumio API call failed:", e)


def volumio_volume(direction):
    """Adjust volume up/down."""
    cmd = {"cmd": "volume", "value": direction}
    volumio_command(cmd)


def volumio_volume_exact(value):
    """Set exact volume (0–100)."""
    cmd = {"cmd": "volume", "value": value}
    volumio_command(cmd)


def volumio_play_pause():
    """Toggle play/pause."""
    cmd = {"cmd": "playpause"}
    volumio_command(cmd)


def volumio_prev():
    """Go to previous track."""
    cmd = {"cmd": "prev"}
    volumio_command(cmd)


def volumio_next():
    """Go to next track."""
    cmd = {"cmd": "next"}
    volumio_command(cmd)


def handle_touch(x, y, art_image, draw, lcd_driver, muted):
    """
    Main touch handler:
    - x, y: from CST328 coordinates.
    - art_image: PIL Image for album‑art.
    - draw: ImageDraw instance.
    - lcd_driver: your Volumio‑LCD display driver (e.g., LCD_2inch8).
    - muted: current mute state (bool).
    Returns new muted state.
    """
    global current_overlay

    # Default is no overlay change
    new_muted = muted

    # ----- 1. Bottom metadata strip: overall control overlay -----
    if is_in(META_STRIP, x, y):
        # Show Back / Play‑Pause / Forward / Browse overlay
        # Here in this stub, we just toggle mute on tap‑anywhere in strip
        # but in reality you can expand this to proper icon hit‑zones.

        volumio_play_pause()
        # Optionally toggle mute just for demo; later you can do:
        #   current_overlay = "CONTROL"

    # ----- 2. Speaker icon (bottom‑left) -----
    elif is_in(SPEAKER_ICON, x, y):
        # In a real implementation, you'd show a horizontal volume slider
        # and then map horizontal taps to volume levels.
        # Here we just bump volume a bit.

        print("Speaker icon tapped -> volume up")
        volumio_volume("up")

    # ----- 3. Album‑art area: Mute/Unmute -----
    elif is_in(ART_RECT, x, y):
        # Toggle Mute/Unmute and draw/erase overlay
        if not muted:
            # Mute
            volumio_command({"cmd": "mute", "value": True})
            new_art = draw_mute_overlay(art_image, draw, art_image)
            lcd_driver.ShowImage(new_art)  # your actual display call
            new_muted = True
            current_overlay = "MUTE"
            print("Muted")
        else:
            # Unmute
            volumio_command({"cmd": "mute", "value": False})
            lcd_driver.ShowImage(clear_overlay(art_image))  # your call
            new_muted = False
            current_overlay = None
            print("Unmuted")

    return new_muted


def main():
    """
    Entry point for volumio_lcd_ui.py
    In reality, this will be integrated with your Volumio‑LCD driver loop.
    """
    print("Starting VOLUMIO‑LCD touch UI overlay handler...")
    # In practice, you’ll integrate this with:
    #  - your existing LCD_2inch8 loop, and
    #  - CST328 touch events passed in as (x, y).
    # For now, this stub just shows the structure.

    # Example: once per second, simulate a tap
    for i in range(100):
        time.sleep(1)
        print(f"Simulated pass {i}")


if __name__ == "__main__":
    main()

