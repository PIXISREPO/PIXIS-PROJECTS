#!/usr/bin/env python3
import io
import os
import time
import json
import socket
import traceback
import urllib.parse

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

from LCD_2inch8 import LCD_2inch8

MOODE_BASE = "http://localhost"
DEFAULT_COVER_URL = "http://localhost/coverart.php"

WIDTH = 240
HEIGHT = 320
ART_H = 240
POLL_SECONDS = 1.0
HTTP_TIMEOUT = 5

try:
    FONT_ARTIST = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14
    )
    FONT_ALBUM = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13
    )
    FONT_TRACK = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11
    )
    FONT_INFO = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
    )
except:
    FONT_ARTIST = FONT_ALBUM = FONT_TRACK = FONT_INFO = ImageFont.load_default()

session = requests.Session()


def get_ip_addresses():
    ips = []
    try:
        import subprocess
        result = subprocess.check_output(
            ["hostname", "-I"], timeout=3
        ).decode().strip()
        ips = [ip for ip in result.split() if "." in ip]
    except:
        pass
    if not ips:
        try:
            ips = [socket.gethostbyname(socket.gethostname())]
        except:
            ips = ["unavailable"]
    return ips


def get_hostname():
    try:
        return socket.gethostname()
    except:
        return "moode"


def api_get(url):
    """Fetch a Moode API URL and return parsed JSON dict, or {} on any error."""
    try:
        r = session.get(url, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        text = r.text.strip()
        if not text:
            return {}
        return r.json()
    except Exception:
        return {}


def values_of(d):
    """Return all string values from a numeric-keyed dict."""
    return list(d.values()) if isinstance(d, dict) else []


def find_prefixed(d, prefix):
    """Return the value after stripping prefix, or '' if not found."""
    for v in values_of(d):
        if isinstance(v, str) and v.startswith(prefix):
            return v[len(prefix):].strip()
    return ""


def truncate_text(draw, text, font, max_width):
    if not text:
        return ""
    bbox = font.getbbox(text)
    text_width = bbox[2] - bbox[0]
    if text_width <= max_width:
        return text
    ellipsis = "..."
    lo, hi = 0, len(text)
    best = ellipsis
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = text[:mid].rstrip() + ellipsis
        bbox = font.getbbox(candidate)
        candidate_width = bbox[2] - bbox[0]
        if candidate_width <= max_width:
            best = candidate
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def get_state():
    SONG_URL   = "http://localhost/command/?cmd=currentsong"
    STATUS_URL = "http://localhost/command/?cmd=status"
    RP_API_URL = "https://api.radioparadise.com/api/now_playing?chan=0"

    song_data   = api_get(SONG_URL)
    status_data = api_get(STATUS_URL)

    # Extract playback state
    status = find_prefixed(status_data, "state: ") or "stop"

    # Extract station name
    station = find_prefixed(song_data, "Name: ")

    # Radio Paradise live metadata
    if "radio paradise" in station.lower():
        try:
            rp_data = api_get(RP_API_URL)
            if rp_data:
                return {
                    "status": status,
                    "artist": rp_data.get("artist", ""),
                    "title":  rp_data.get("title", ""),
                    "album":  rp_data.get("album", ""),
                    "albumart": rp_data.get("cover", ""),
                }
        except:
            pass

    # Generic title parsing: "Artist - Track" or just "Track"
    raw_title = find_prefixed(song_data, "Title: ")
    if " - " in raw_title:
        artist, title = raw_title.split(" - ", 1)
    else:
        artist = ""
        title  = raw_title

    # Album (local files)
    album = find_prefixed(song_data, "Album: ")
    if not album:
        album = station  # fall back to station name for radio

    # Album art: local files use coverart.php; radio uses station logo
    if station:
        logo_url = "http://localhost/imagesw/radio-logos/" + urllib.parse.quote(station + ".jpg")
        albumart = logo_url
    else:
        albumart = DEFAULT_COVER_URL

    return {
        "status":   status,
        "artist":   artist.strip(),
        "title":    title.strip(),
        "album":    album.strip(),
        "albumart": albumart,
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

    if cover_img is None:
        cover = Image.new("RGB", (WIDTH, ART_H), (30, 30, 30))
        draw_cover = ImageDraw.Draw(cover)
        msg = "No Cover Art"
        bbox = FONT_INFO.getbbox(msg)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw_cover.text(
            ((WIDTH - tw) // 2, (ART_H - th) // 2),
            msg, font=FONT_INFO, fill=(180, 180, 180),
        )
    else:
        cover = ImageOps.fit(
            cover_img.convert("RGB"),
            (WIDTH, ART_H),
            method=Image.LANCZOS,
            centering=(0.5, 0.5),
        )

    canvas.paste(cover, (0, 0))
    draw = ImageDraw.Draw(canvas)

    artist = state.get("artist", "") or ""
    album  = "ALBUM: " + (state.get("album", "") or "").strip()
    track  = state.get("title", "") or ""

    artist = truncate_text(draw, artist, FONT_ARTIST, WIDTH - 12)
    album  = truncate_text(draw, album,  FONT_ALBUM,  WIDTH - 12)
    track  = truncate_text(draw, track,  FONT_TRACK,  WIDTH - 12)

    draw.text((6, 244), artist, font=FONT_ARTIST, fill="white")
    draw.text((6, 270), album,  font=FONT_ALBUM,  fill=(210, 210, 210))
    draw.text((6, 294), track,  font=FONT_TRACK,  fill="white")

    return canvas


def render_idle_screen():
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw   = ImageDraw.Draw(canvas)

    hostname = get_hostname()
    ips = get_ip_addresses()

    lines = [
        ("PIXIS LCD",            FONT_ARTIST, "white"),
        ("Waiting for playback", FONT_INFO,   (180, 180, 180)),
        ("",                     None,        None),
        ("Hostname: " + hostname, FONT_INFO,  (180, 180, 180)),
    ]
    for ip in ips:
        lines.append(("IP: " + ip, FONT_INFO, (140, 210, 140)))

    total_height = 0
    line_heights = []
    for text, font, color in lines:
        if font is None:
            line_heights.append(8)
            total_height += 8
        else:
            bbox = font.getbbox(text)
            h = bbox[3] - bbox[1]
            line_heights.append(h + 6)
            total_height += h + 6

    y = (HEIGHT - total_height) // 2
    for i, (text, font, color) in enumerate(lines):
        if font is None:
            y += line_heights[i]
            continue
        bbox = font.getbbox(text)
        w = bbox[2] - bbox[0]
        draw.text(((WIDTH - w) // 2, y), text, font=font, fill=color)
        y += line_heights[i]

    return canvas


def main():
    disp = LCD_2inch8()
    disp.ST7789_Init()
    disp.clear()

    last_signature = None

    while True:
        try:
            state  = get_state()
            status = state.get("status", "") or ""

            if status in ("play", "pause"):
                cover_img = fetch_cover_image(state)
                image     = render_cover_screen(state, cover_img)
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
                image     = render_idle_screen()
                signature = "idle"

            if signature != last_signature:
                disp.ShowImage(image)
                last_signature = signature

        except Exception:
            traceback.print_exc()

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
