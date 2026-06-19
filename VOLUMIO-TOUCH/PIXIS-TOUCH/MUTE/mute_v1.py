#!/usr/bin/env python3
import subprocess, time, os, re, signal, sys
from datetime import datetime
from PIL import Image, ImageOps

TOUCH_CAPTURE_SCRIPT = "/home/volumio/waveshare-2.8/Python/touch_capture_final.py"
ALBUM_ART_PATH = "/tmp/volumio_album_art.jpg"
BACKUP_ART_PATH = "/tmp/volumio_album_art.orig.jpg"
ATTACHED_MUTE_IMAGE = "/Users/peter/Documents/PIXISREPO/PIXIS-PROJECTS/VOLUMIO-TOUCH/PIXIS-TOUCH/MUTE/mute_transparent_50px.png"
MUTE_ICON_SIZE = 50
MUTE_ZONES = {"A1","A2","A3","A4"}
DEBOUNCE_SEC = 0.5
_is_muted = False
_last_zone = None
_last_time = 0
_running = True

def log(s):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {s}", flush=True)

def signal_handler(sig, frame):
    global _running
    _running = False
    sys.exit(0)

def parse_touch_event(line):
    m = re.search(r"zone=(A[1-4]|B[1-3])\s+x=(\d+)\s+y=(\d+)\s+points=(\d+)", line)
    if not m:
        return None
    return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))

def ensure_backup():
    if not os.path.exists(ALBUM_ART_PATH):
        return False
    if not os.path.exists(BACKUP_ART_PATH):
        subprocess.run(["cp", ALBUM_ART_PATH, BACKUP_ART_PATH], check=True)
    return True

def apply_mute_overlay():
    if not ensure_backup():
        return False
    base = Image.open(BACKUP_ART_PATH).convert("RGBA")
    icon = Image.open(ATTACHED_MUTE_IMAGE).convert("RGBA")
    icon = ImageOps.contain(icon, (MUTE_ICON_SIZE, MUTE_ICON_SIZE))
    pos = ((base.width - icon.width)//2, (base.height - icon.height)//2)
    base.paste(icon, pos, icon)
    base.convert("RGB").save(ALBUM_ART_PATH, "JPEG", quality=95)
    return True

def remove_mute_overlay():
    if os.path.exists(BACKUP_ART_PATH):
        subprocess.run(["cp", BACKUP_ART_PATH, ALBUM_ART_PATH], check=True)
        return True
    return False

def mpc_mute():
    global _is_muted
    subprocess.run(["mpc", "mute"], check=True, timeout=2)
    _is_muted = True
    return True

def mpc_unmute():
    global _is_muted
    subprocess.run(["mpc", "unmute"], check=True, timeout=2)
    _is_muted = False
    return True

def toggle_mute_and_overlay():
    if _is_muted:
        if mpc_unmute():
            remove_mute_overlay()
    else:
        if mpc_mute():
            apply_mute_overlay()

def main():
    global _last_zone, _last_time, _running
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    proc = subprocess.Popen(["sudo","python3",TOUCH_CAPTURE_SCRIPT], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    while _running and proc.poll() is None:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.01)
            continue
        p = parse_touch_event(line.strip())
        if not p:
            continue
        zone, x, y, pts = p
        if zone in MUTE_ZONES:
            now = time.time()
            if _last_zone == zone and (now - _last_time) < DEBOUNCE_SEC:
                continue
            _last_zone = zone
            _last_time = now
            toggle_mute_and_overlay()
    try:
        proc.terminate()
    except:
        pass

if __name__ == '__main__':
    main()

