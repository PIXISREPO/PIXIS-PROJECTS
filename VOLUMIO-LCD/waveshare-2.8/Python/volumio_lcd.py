#!/usr/bin/env python3
import io
import os
import time
import json
import traceback
from urllib.parse import urljoin

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

from LCD_2inch8 import LCD_2inch8

MOODE_BASE = "http://localhost"
STATE_URL = f"{MOODE_BASE}/command/?cmd=status"
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


def truncate_text(draw, text, font, max_width):
    if not text:
        return ""

    bbox = font.getbbox(text); text_width = bbox[2] - bbox[0]
    if text_width <= max_width:
        return text

    ellipsis = "..."
    lo, hi = 0, len(text)
    best = ellipsis

    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = text[:mid].rstrip() + ellipsis
        bbox = font.getbbox(candidate); candidate_width = bbox[2] - bbox[0]
        if candidate_width <= max_width:
            best = candidate
            lo = mid + 1
        else:
            hi = mid - 1

    return best


def get_state():
    SONG_URL = "http://localhost/command/?cmd=currentsong"
    STATUS_URL = "http://localhost/command/?cmd=status"
    RP_API_URL = "https://api.radioparadise.com/api/now_playing?chan=0"

    song_r = session.get(SONG_URL, timeout=HTTP_TIMEOUT)
    song_r.raise_for_status()
    song_data = song_r.json()

    status_r = session.get(STATUS_URL, timeout=HTTP_TIMEOUT)
    status_r.raise_for_status()
    status_data = status_r.json()

    # Extract state: play/pause/stop
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

    # Radio Paradise — use their API for rich metadata + art
    if "radio paradise" in station.lower():
        try:
            rp = session.get(RP_API_URL, timeout=HTTP_TIMEOUT)
            rp.raise_for_status()
            rp_data = rp.json()
            return {
                "status": status,
                "artist": rp_data.get("artist", ""),
                "title": rp_data.get("title", ""),
                "album": rp_data.get("album", ""),
                "albumart": rp_data.get("cover", ""),
            }
        except:
            pass

    # Generic internet radio — parse Title field
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

    # Try moOde radio logo as art
    import urllib.parse
    logo_url = "http://localhost/imagesw/radio-logos/" + urllib.parse.quote(station + ".jpg")

    return {
        "status": status,
        "artist": artist.strip(),
        "title": title.strip(),
        "album": station,
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

    if cover_img is None:
        cover = Image.new("RGB", (WIDTH, ART_H), (30, 30, 30))
        draw_cover = ImageDraw.Draw(cover)
        msg = "No Cover Art"
        bbox = FONT_INFO.getbbox(msg); tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw_cover.text(
            ((WIDTH - tw) // 2, (ART_H - th) // 2),
            msg,
            font=FONT_INFO,
            fill=(180, 180, 180),
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
    album = "ALBUM: " + ((state.get("album", "") or "").strip())
    track = state.get("title", "") or ""

    artist = truncate_text(draw, artist, FONT_ARTIST, WIDTH - 12)
    album = truncate_text(draw, album, FONT_ALBUM, WIDTH - 12)
    track = truncate_text(draw, track, FONT_TRACK, WIDTH - 12)

    draw.text((6, 244), artist, font=FONT_ARTIST, fill="white")
    draw.text((6, 270), album, font=FONT_ALBUM, fill=(210, 210, 210))
    draw.text((6, 294), track, font=FONT_TRACK, fill="white")

    return canvas


def render_idle_screen():
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(canvas)

    line1 = "PIXIS LCD"
    line2 = "Waiting for playback"

    bbox1 = FONT_ARTIST.getbbox(line1); w1, h1 = bbox1[2] - bbox1[0], bbox1[3] - bbox1[1]
    bbox2 = FONT_INFO.getbbox(line2); w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]

    y = 130
    draw.text(((WIDTH - w1) // 2, y), line1, font=FONT_ARTIST, fill="white")
    draw.text(((WIDTH - w2) // 2, y + h1 + 12), line2, font=FONT_INFO, fill=(180, 180, 180))

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
                        "status": status,
                        "artist": state.get("artist", ""),
                        "album": state.get("album", ""),
                        "title": state.get("title", ""),
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
