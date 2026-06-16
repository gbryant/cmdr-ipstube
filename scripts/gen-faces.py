#!/usr/bin/env python3
"""Build the LittleFS image tree under storage/ for the IPSTube clock.

Populates:
  storage/faces/<set>/0.png .. 9.png   digit images, composited on black,
                                       resized to one IPSTube panel (135x240),
                                       saved as RGB PNG (no alpha) for on-device
                                       pngle decode -> IpstubeModule::drawBitmap
  storage/fonts/Karla-Regular.ttf      text-rendering font (also embedded as a
                                       firmware fallback)

The whole storage/ dir is packed into the `storage` partition by
littlefs_create_partition_image() and flashed with the app.

    pip install pillow
    scripts/gen-faces.py                       # default flip-clock asset dir
    scripts/gen-faces.py /path/to/pngs  myset  # a different digit set/name
"""
import shutil
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow not installed — run: pip install pillow")

W, H = 135, 240
DEFAULT_ASSETS = "/Users/gbryant/github/EleksTubeHAX/assets/other graphics/4 flip clock"
ROOT = Path(__file__).resolve().parent.parent
STORAGE = ROOT / "storage"
FONT_SRC = ROOT / "main" / "fonts" / "Karla-Regular.ttf"


def composite_resize(path):
    img = Image.open(path)
    if img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        img = Image.alpha_composite(Image.new("RGBA", img.size, (0, 0, 0, 255)), img)
    img = img.convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    return img


def main():
    assets = Path(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ASSETS)
    face = sys.argv[2] if len(sys.argv) > 2 else "flip"

    faces_dir = STORAGE / "faces" / face
    faces_dir.mkdir(parents=True, exist_ok=True)
    for n in range(10):
        src = assets / f"{n}.png"
        if not src.exists():
            sys.exit(f"missing {src}")
        composite_resize(src).save(faces_dir / f"{n}.png", optimize=True)

    fonts_dir = STORAGE / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)
    if FONT_SRC.exists():
        shutil.copy2(FONT_SRC, fonts_dir / FONT_SRC.name)

    total = sum(p.stat().st_size for p in STORAGE.rglob("*") if p.is_file())
    print(f"wrote {faces_dir}/0..9.png ({W}x{H}) + {fonts_dir.name}/  "
          f"— storage/ total ~{total // 1024} KB")


if __name__ == "__main__":
    main()
