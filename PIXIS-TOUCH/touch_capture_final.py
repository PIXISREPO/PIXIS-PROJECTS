#!/usr/bin/env python3
import time
import smbus
import RPi.GPIO as GPIO

CST328_ADDRESS = 0x1A
TP_INT = 4
TP_RST = 17

IRQ_SAMPLES = 6
IRQ_REQUIRED_HIGH = 5
D005_SAMPLES = 3
D005_REQUIRED_NONZERO = 2
D005_POLL_DELAY = 0.002
D005_TIMEOUT_SEC = 0.030
XY_STABLE_REQUIRED = 3
XY_POLL_DELAY = 0.002
XY_TIMEOUT_SEC = 0.030
XY_DRIFT_DELTA = 8

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TP_INT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TP_RST, GPIO.OUT)

bus = smbus.SMBus(1)

def ts():
    return time.strftime('%Y-%m-%d %H:%M:%S')

def log(msg):
    print(f'[{ts()}] {msg}', flush=True)

def reset_touch():
    GPIO.output(TP_RST, 0)
    time.sleep(0.001)
    GPIO.output(TP_RST, 1)
    time.sleep(0.05)

def read_nbyte(reg, num_bytes):
    bus.write_byte_data(CST328_ADDRESS, (reg >> 8) & 0xFF, reg & 0xFF)
    return [bus.read_byte(CST328_ADDRESS) for _ in range(num_bytes)]

def write_nbyte(reg, val):
    bus.write_byte_data(CST328_ADDRESS, (reg >> 8) & 0xFF, ((reg & 0xFF) << 8) | (val & 0xFF))

def irq_valid():
    samples = []
    highs = 0
    for _ in range(IRQ_SAMPLES):
        v = int(GPIO.input(TP_INT))
        samples.append(v)
        highs += (v == 1)
        time.sleep(0.001)
    log(f'irq={"".join(map(str, samples))}')
    return highs >= IRQ_REQUIRED_HIGH

def read_d005():
    return read_nbyte(0xD005, 1)[0] & 0x0F

def wait_touch_ready():
    start = time.monotonic()
    seen = []
    while (time.monotonic() - start) < D005_TIMEOUT_SEC:
        v = read_d005()
        seen.append(v)
        log(f'd005={v}')
        if len(seen) >= D005_SAMPLES and sum(x > 0 for x in seen[-D005_SAMPLES:]) >= D005_REQUIRED_NONZERO:
            return True
        time.sleep(D005_POLL_DELAY)
    return False

def read_xy_packet():
    buf = read_nbyte(0xD000, 27)
    x = ((buf[1] << 4) + ((buf[3] & 0xF0) >> 4))
    y = ((buf[2] << 4) + (buf[3] & 0x0F))
    points = read_d005()
    return x, y, points

def coord_close(a, b, delta):
    return abs(a[0] - b[0]) <= delta and abs(a[1] - b[1]) <= delta and a[2] == b[2]

def read_stable_xy():
    start = time.monotonic()
    samples = []
    while (time.monotonic() - start) < XY_TIMEOUT_SEC:
        s = read_xy_packet()
        samples.append(s)
        log(f'xy={s[0]},{s[1]},{s[2]}')
        if len(samples) >= XY_STABLE_REQUIRED:
            tail = samples[-XY_STABLE_REQUIRED:]
            base = tail[0]
            if all(coord_close(base, s, XY_DRIFT_DELTA) for s in tail[1:]):
                xs = [s[0] for s in tail]
                ys = [s[1] for s in tail]
                ps = [s[2] for s in tail]
                return sorted(xs)[len(xs)//2], sorted(ys)[len(ys)//2], max(set(ps), key=ps.count)
        time.sleep(XY_POLL_DELAY)
    return None

def zone_for_xy(x, y):
    if y < 120:
        return 'A1' if x < 120 else 'A2'
    if y < 240:
        return 'A3' if x < 120 else 'A4'
    if x < 80:
        return 'B1'
    if x < 160:
        return 'B2'
    return 'B3'

try:
    reset_touch()
    log('ready')
    last_state = int(GPIO.input(TP_INT))
    while True:
        state = int(GPIO.input(TP_INT))
        if state == 1 and last_state == 0:
            if irq_valid() and wait_touch_ready():
                xy = read_stable_xy()
                if xy is not None:
                    x, y, points = xy
                    zone = zone_for_xy(x, y)
                    log(f'zone={zone} x={x} y={y} points={points}')
                    write_nbyte(0xD005, 0)
                else:
                    log('xy=unstable')
            else:
                log('d005=timeout')
        last_state = state
        time.sleep(0.001)
except KeyboardInterrupt:
    pass
finally:
    try:
        bus.close()
    except Exception:
        pass
    GPIO.cleanup()
