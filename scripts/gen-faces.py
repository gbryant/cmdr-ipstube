#!/usr/bin/env python3
"""Build the LittleFS image tree under storage/ for the IPSTube clock.

Populates:
  storage/faces/<set>/0.png .. 9.png   digit images, one per IPSTube panel
                                       (135x240), RGB PNG with no alpha for
                                       on-device pngle decode -> drawBitmap
  storage/fonts/*.ttf                  text-rendering fonts for the font clock

The whole storage/ dir is packed into the `storage` partition by
littlefs_create_partition_image() and flashed with the app.

Two ways to make a digit set:

    pip install pillow

    # 1. render a split-flap face from one of the bundled OFL fonts (default)
    scripts/gen-faces.py
    scripts/gen-faces.py --font Karla-Regular --set karla

    # 2. convert your own 10 digit images (any size; letterboxed to 135x240)
    scripts/gen-faces.py --from-dir /path/to/pngs --set myset

Bring-your-own images are yours to license — this repo ships only faces it
renders from its own OFL fonts.
"""
import argparse
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow not installed — run: pip install pillow")

W, H = 135, 240                    # one IPSTube panel
ROOT = Path(__file__).resolve().parent.parent
STORAGE = ROOT / "storage"
FONT_DIR = ROOT / "main" / "fonts"

# Split-flap look: two stacked cards, a dark gap where the flap hinges, and a
# digit big enough to be cut by it. Tuned for a 135x240 panel viewed in a tube.
BG, CARD, CARD_LO = (0, 0, 0), (26, 26, 30), (20, 20, 23)
DIGIT, SEAM, EDGE = (240, 240, 244), (0, 0, 0), (48, 48, 54)
MARGIN, RADIUS, SEAM_H = 5, 13, 3
DIGIT_H, DIGIT_PAD = 0.52, 26      # of panel height / horizontal breathing room


def fit_font(path, target_h, max_w):
    """Largest point size whose digits fit the card in both axes."""
    lo, hi, best = 8, 400, None
    while lo <= hi:
        mid = (lo + hi) // 2
        f = ImageFont.truetype(str(path), mid)
        boxes = [f.getbbox(c) for c in "0123456789"]
        if (max(b[3] - b[1] for b in boxes) <= target_h
                and max(b[2] - b[0] for b in boxes) <= max_w):
            best, lo = f, mid + 1
        else:
            hi = mid - 1
    if best is None:
        sys.exit(f"could not fit any digit size from {path}")
    return best


def render_digit(font, digit):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = MARGIN, MARGIN, W - MARGIN - 1, H - MARGIN - 1
    mid = H // 2

    # two cards; the lower one slightly darker, as a real split-flap reads
    d.rounded_rectangle([x0, y0, x1, mid - 1], radius=RADIUS, fill=CARD)
    d.rounded_rectangle([x0, mid + SEAM_H, x1, y1], radius=RADIUS, fill=CARD_LO)
    # square off the inner corners so the halves read as one card
    d.rectangle([x0, mid - RADIUS, x1, mid - 1], fill=CARD)
    d.rectangle([x0, mid + SEAM_H, x1, mid + SEAM_H + RADIUS], fill=CARD_LO)

    box = font.getbbox(digit)
    d.text(((W - (box[2] - box[0])) // 2 - box[0],
            (H - (box[3] - box[1])) // 2 - box[1]), digit, font=font, fill=DIGIT)

    # the flap gap, cutting across the digit
    d.rectangle([x0, mid, x1, mid + SEAM_H - 1], fill=SEAM)
    d.line([(x0, mid + SEAM_H), (x1, mid + SEAM_H)], fill=EDGE)
    # the pegs the flap pivots on
    d.rectangle([x0, mid - 2, x0 + 1, mid + SEAM_H + 1], fill=EDGE)
    d.rectangle([x1 - 1, mid - 2, x1, mid + SEAM_H + 1], fill=EDGE)
    return img


def convert_image(path):
    """Flatten onto black and letterbox to panel size, preserving aspect."""
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        img = Image.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, 255)), img)
    img = img.convert("RGB")
    if img.size == (W, H):
        return img
    scale = min(W / img.width, H / img.height)
    img = img.resize((max(1, round(img.width * scale)),
                      max(1, round(img.height * scale))), Image.LANCZOS)
    out = Image.new("RGB", (W, H), BG)
    out.paste(img, ((W - img.width) // 2, (H - img.height) // 2))
    return out


def main():
    ap = argparse.ArgumentParser(description="Build storage/ for the IPSTube clock.")
    ap.add_argument("--font", default="OpenSauceOne-Regular",
                    help="bundled font in main/fonts to render digits from "
                         "(default: OpenSauceOne-Regular), or a path to a .ttf")
    ap.add_argument("--from-dir", metavar="DIR",
                    help="convert 0.png..9.png from DIR instead of rendering")
    ap.add_argument("--set", default="flip", help="digit set name (default: flip)")
    args = ap.parse_args()

    faces_dir = STORAGE / "faces" / args.set
    faces_dir.mkdir(parents=True, exist_ok=True)

    if args.from_dir:
        src_dir = Path(args.from_dir)
        for n in range(10):
            src = src_dir / f"{n}.png"
            if not src.exists():
                sys.exit(f"missing {src}")
            convert_image(src).save(faces_dir / f"{n}.png", optimize=True)
        source = f"{src_dir}/0..9.png"
    else:
        font_path = Path(args.font)
        if not font_path.exists():
            font_path = FONT_DIR / f"{args.font}.ttf"
        if not font_path.exists():
            sys.exit(f"no such font: {args.font} (looked in {FONT_DIR})")
        font = fit_font(font_path, int(H * DIGIT_H), W - 2 * MARGIN - DIGIT_PAD)
        for n in range(10):
            render_digit(font, str(n)).save(faces_dir / f"{n}.png", optimize=True)
        source = font_path.name

    # The font clock reads its TTFs from the same partition. Copy the OFL notices
    # across with them — the licence requires the fonts to travel with it, and this
    # tree is flashed to the device as a filesystem in its own right.
    fonts_dir = STORAGE / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    for f in sorted(list(FONT_DIR.glob("*.ttf")) + list(FONT_DIR.glob("*OFL*.txt"))):
        shutil.copy2(f, fonts_dir / f.name)

    total = sum(p.stat().st_size for p in STORAGE.rglob("*") if p.is_file())
    print(f"wrote faces/{args.set}/0..9.png ({W}x{H}) from {source} "
          f"+ fonts/ — storage/ total ~{total // 1024} KB")


if __name__ == "__main__":
    main()
