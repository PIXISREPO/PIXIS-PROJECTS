#!/usr/bin/env python3
"""
PIXIS LCD — moOde Audio player variant
Displays album art and playback metadata on a Waveshare 2.8" SPI LCD
"""

import io
import json
import time
import traceback
from urllib.parse import urljoin
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont

# ── Display config ────────────────────────────────────────────
WIDTH  = 320
HEIGHT = 240
POLL_SECONDS = 1
HTTP_TIMEOUT = 5

# ── moOde endpoints ───────────────────────────────────────────
SONG_URL   = "http://localhost/command/?cmd=currentsong"
STATUS_URL = "http://localhost/command/?cmd=status"
RP_API_URL = "https://api.radioparadise.com/api/now_playing?chan=0"
DEFAULT_COVER_URL = "http://localhost/images/default-album-cover.png"

# ── Fonts ─────────────────────────────────────────────────────
try:
    FONT_TITLE  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    FONT_ARTIST = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    FONT_INFO   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except:
    FONT_TITLE  = ImageFont.load_default()
    FONT_ARTIST = ImageFont.load_default()
    FONT_INFO   = ImageFont.load_default()

session = requests.Session()

# ── Import display driver ─────────────────────────────────────
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from LCD_2inch8 import LCD_2inch8


def truncate_text(text, font, max_width):
    """Truncate text to fit within max_width pixels."""
    bbox = font.getbbox(text)
    if bbox[2] - bbox[0] <= max_width:
        return text
    while text:
        text = text[:-1]
        candidate = text + "…"
        bbox = font.getbbox(candidate)
        if bbox[2] - bbox[0] <= max_width:
            return candidate
    return ""


def get_state():
    song_r = session.get(SONG_URL, timeout=HTTP_TIMEOUT)
    song_r.raise_for_status()
    song_data = song_r.json()

    status_r = session.get(STATUS_URL, timeout=HTTP_TIMEOUT)
    status_r.raise_for_status()
    status_data = status_r.json()

    # Extract play state
    status = "stop"
    for v in status_data.values():
        if v.startswith("state: "):
            status = v.replace("state: ", "").strip()
            break

    # Extract station name
    station = ""
    for v in song_data.values():
        if v.startswith("Name: "):
            station = v.replace("Name: ", "").strip()
            break

    # Radio Paradise — rich metadata + art from RP API
    if "radio paradise" in station.lower():
        try:
            rp = session.get(RP_API_URL, timeout=HTTP_TIMEOUT)
            rp.raise_for_status()
            rp_data = rp.json()
            return {
                "status":   status,
                "artist":   rp_data.get("artist", ""),
                "title":    rp_data.get("title", ""),
                "album":    rp_data.get("album", ""),
                "albumart": rp_data.get("cover", ""),
            }
        except:
            pass

    # Generic internet radio — parse "Artist - Title"
    raw_title = ""
    for v in song_data.values():
        if v.startswith("Title: "):
            raw_title = v.replace("Title: ", "").strip()
            break

    if " - " in raw_title:
        artist, title = raw_title.split(" - ", 1)
    else:
        artist = ""
        title = raw_title

    logo_url = "http://localhost/imagesw/radio-logos/" + urllib.parse.quote(station + ".jpg")

    return {
        "status":   status,
        "artist":   artist.strip(),
        "title":    title.strip(),
        "album":    station,
        "albumart": logo_url,
    }


def resolve_albumart_url(state):
    albumart = state.get("albumart", "") or ""
    if not albumart:
        return DEFAULT_COVER_URL
    if albumart.startswith("http://") or albumart.startswith("https://"):
        return albumart
    return DEFAULT_COVER_URL


def fetch_cover_image(state):
    url = resolve_albumart_url(state)
    try:
        r = session.get(url, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    except:
        try:
            r = session.get(DEFAULT_COVER_URL, timeout=HTTP_TIMEOUT)
            r.raise_for_status()
            return Image.open(io.BytesIO(r.content)).convert("RGB")
        except:
            return None


def render_cover_screen(state, cover_img):
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "black")

    # Album art — left square
    art_size = HEIGHT
    if cover_img:
        art = cover_img.resize((art_size, art_size), Image.LANCZOS)
        canvas.paste(art, (0, 0))

    # Metadata — right panel
    panel_x = art_size + 8
    panel_w = WIDTH - panel_x - 4
    draw = ImageDraw.Draw(canvas)

    artist = truncate_text(state.get("artist", ""), FONT_ARTIST, panel_w)
    title  = truncate_text(state.get("title", ""),  FONT_TITLE,  panel_w)
    album  = truncate_text(state.get("album", ""),  FONT_INFO,   panel_w)

    draw.text((panel_x, 10),  artist, font=FONT_ARTIST, fill="white")
    draw.text((panel_x, 30),  title,  font=FONT_TITLE,  fill="yellow")
    draw.text((panel_x, 55),  album,  font=FONT_INFO,   fill="grey")

    return canvas


def render_idle_screen():
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(canvas)
    line1 = "PIXIS LCD"
    line2 = "Waiting for Playback"
    bbox1 = FONT_ARTIST.getbbox(line1)
    bbox2 = FONT_INFO.getbbox(line2)
    w1, h1 = bbox1[2] - bbox1[0], bbox1[3] - bbox1[1]
    w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
    draw.text(((WIDTH - w1) // 2, HEIGHT // 2 - h1 - 4), line1, font=FONT_ARTIST, fill="white")
    draw.text(((WIDTH - w2) // 2, HEIGHT // 2 + 4),       line2, font=FONT_INFO,   fill="grey")
    return canvas


def main():
    disp = LCD_2inch8()
    disp.ST7789_Init()
    disp.clear()

    last_signature = None

    while True:
        try:
            state = get_state()
            status = state.get("status", "") or ""

            if status in ("play", "pause"):
                cover_img = fetch_cover_image(state)
                image = render_cover_screen(state, cover_img)
                signature = json.dumps(
                    {
                        "status":   status,
                        "artist":   state.get("artist", ""),
                        "album":    state.get("album", ""),
                        "title":    state.get("title", ""),
                        "albumart": state.get("albumart", ""),
                    },
                    sort_keys=True,
                )
            else:
                image = render_idle_screen()
                signature = "idle"

            if signature != last_signature:
                disp.ShowImage(image)
                last_signature = signature

        except Exception:
            traceback.print_exc()

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
