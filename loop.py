#!/usr/bin/env python3

import telnetlib
import random
import time
import colorsys

HOST = "cmdr-ipstube.local"  # CHANGE ME
PORT = 23

LCD_COUNT = 6
MODE_DURATION = 60


# ----------------------------
# Telnet command handling
# ----------------------------

def _clean(text):
    """Strip a leading prompt ('> ') and surrounding whitespace."""
    return text.lstrip("> ").strip()


def send_cmd(tn, cmd, timeout=10):
    """
    Send command and wait for an 'ok' response before continuing.
    This prevents flooding the device.

    The device uses CRLF line endings and echoes back a prompt ('> ')
    and the command itself, so we scan all received text for the
    'ok'/'error' tokens instead of matching a single line exactly.
    """
    print(f"> {cmd}")
    tn.write((cmd + "\r\n").encode())

    start = time.time()
    buf = ""

    while time.time() - start <= timeout:
        try:
            chunk = tn.read_until(b"\n", timeout=1)
        except EOFError:
            raise RuntimeError(f"Connection closed waiting for OK: {cmd}")

        if not chunk:
            continue

        buf += chunk.decode(errors="replace")
        buf = buf.replace("\r\n", "\n").replace("\r", "\n")

        # Process complete lines; keep any trailing partial in buf.
        *lines, buf = buf.split("\n")

        for raw in lines:
            text = _clean(raw)
            if not text:
                continue
            print(text)
            low = text.lower()
            if low == cmd.lower():
                continue  # device echoing our command back
            if low == "ok":
                return
            if low.startswith("error"):
                raise RuntimeError(f"Device error: {text}")

        # Handle an 'ok' that arrives without a trailing newline
        # (e.g. when the device leaves us sitting at a prompt).
        pending = _clean(buf).lower()
        if pending == "ok":
            print(_clean(buf))
            return
        if pending.startswith("error"):
            raise RuntimeError(f"Device error: {_clean(buf)}")

    raise TimeoutError(f"Timeout waiting for OK: {cmd} (got: {buf!r})")


def connect():
    print(f"Connecting to {HOST}:{PORT}...")
    tn = telnetlib.Telnet(HOST, PORT, timeout=10)

    send_cmd(tn, "ipstube dim 25")

    print("Connected.")
    return tn


# ----------------------------
# Color helpers
# ----------------------------

def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def hsv565(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return rgb888_to_rgb565(
        int(r * 255),
        int(g * 255),
        int(b * 255),
    )


def fill_panel(tn, panel, color565):
    send_cmd(tn, f"ipstube fill {panel} {color565}")


# ----------------------------
# Modes
# ----------------------------

def random_mode(tn):
    colors = [random.randint(0, 0xFFFF) for _ in range(LCD_COUNT)]

    for i in range(LCD_COUNT):
        fill_panel(tn, i, colors[i])


def gradient_mode(tn):
    start = random.random()
    end = (start + random.uniform(0.2, 0.6)) % 1.0

    diff = end - start
    if abs(diff) > 0.5:
        diff += -1.0 if diff > 0 else 1.0

    for i in range(LCD_COUNT):
        t = i / (LCD_COUNT - 1)
        hue = (start + diff * t) % 1.0
        fill_panel(tn, i, hsv565(hue))


def rainbow_mode(tn, phase):
    for i in range(LCD_COUNT):
        hue = ((i / LCD_COUNT) + phase) % 1.0
        fill_panel(tn, i, hsv565(hue))


# ----------------------------
# Main loop
# ----------------------------

def run():
    tn = connect()

    modes = ["random", "gradient", "rainbow"]
    rainbow_phase = 0.0

    try:
        while True:
            mode = random.choice(modes)

            print("\n" + "=" * 40)
            print(f"MODE: {mode}")
            print("=" * 40)

            start = time.time()

            while time.time() - start < MODE_DURATION:

                if mode == "random":
                    random_mode(tn)

                elif mode == "gradient":
                    gradient_mode(tn)

                elif mode == "rainbow":
                    rainbow_mode(tn, rainbow_phase)
                    rainbow_phase = (rainbow_phase + 0.05) % 1.0

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        try:
            tn.close()
        except:
            pass


if __name__ == "__main__":
    run()