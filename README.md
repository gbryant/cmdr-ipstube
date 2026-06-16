# cmdr-ipstube

A smart clock firmware for the **IPSTube** (classic ESP32 + six ST7789 135×240 IPS
displays + WS2812 ambient LEDs + DS1302 RTC), built on the
[commander](https://github.com/gbryant/commander) embedded shell framework.

## What it does

- **Font clock** — `HH:MM` rendered from a TTF (Karla) with a dot colon, a
  weekday/date panel, and a live weather panel.
- **PNG flip-clock face** — `face png` shows `HHMMSS` from digit images. The
  images live on a LittleFS partition (not baked into firmware), so digit sets can
  be swapped or added without reflashing. `face font` returns to the font clock.
- **Weather** (panel 5) — current temp + condition + today's forecast low/high
  from forecast.weather.gov (NWS), refreshed every 30 min. The high/low stays on
  *today* until local midnight rather than rolling to tomorrow in the evening.
- **News** — top headlines from newsapi.org, hourly. Show as a full-strip marquee
  (`news`), or vertically scroll them on panel 5 (`panel5 news`).
- **Display scenes** — a single scene runner drives the active view: `clock`,
  `marquee <text>`, `read <d|all> <text>` (vertical reader), `hscroll`, `news`,
  and `hold` (yield the displays so an external host can push content). `rotate
  on` cycles clock ↔ news on a timer.
- **Live tuning** — `tune` (clock layout), `mspeed`/`msize` (marquee),
  `news speed` (news scroll). Type a command bare for usage.

## Faces & fonts (LittleFS)

The `storage` partition holds the swappable assets, mounted at `/storage`:

```
storage/faces/<set>/0.png … 9.png   # 135×240 digit images (PNG flip-clock)
storage/fonts/<name>.ttf            # text-rendering fonts
```

Runtime commands (the selection persists across reboots via NVS):

```
face                 # show mode (font/png) + active set
face font | png      # switch render mode
face set             # list digit sets under /storage/faces
face set <name>      # use that set (and switch to the png face)
font                 # show current font + list /storage/fonts
font <name>          # load /storage/fonts/<name>.ttf and re-fit all text
```

Build/refresh the asset tree with `scripts/gen-faces.py` (needs Pillow); it is
packed into the partition image and flashed with the app. The embedded Karla is a
fallback if the filesystem is empty or unmountable.

## Build & flash

ESP-IDF v5+. Copy `secrets.h.example` → `secrets.h` and fill in WiFi + newsapi key.

```bash
./build      # idf.py build into build-esp32/
./upload     # USB flash (writes app, partition table, otadata, and the storage FS)
./monitor    # serial console
./bum        # build + upload + monitor
```

**OTA (over WiFi):** flash layout is dual 2 MB app slots + a ~3.9 MB `storage`
filesystem (`partitions.csv`). The **first** flash must be over USB (it lays down
the new partition table); after that, `./bum-ota` builds and pushes firmware to the
device. During an update the tubes fill left→right as the image lands. OTA carries
the **app only** — face/font assets are reflashed over USB when `storage/` changes.

The commander framework is pulled via FetchContent (see `CMakeLists.txt`). Pin the
version with `cmdr pin` / `unpin`, or build against a local checkout with `cmdr
link` / `unlink`. Display/text features live in commander's `ipstube` module; the
clock/weather/news app logic is in `main/main.cpp`.

## Credits

Bundled UI fonts, each licensed under the SIL Open Font License 1.1:

- [Karla](https://github.com/googlefonts/karla) — © The Karla Project Authors
  ([OFL](main/fonts/Karla-Regular-OFL.txt))
- [Open Sauce One](https://github.com/marcologous/Open-Sauce-Fonts) — © The Open
  Sauce One Authors ([OFL](main/fonts/Open%20Sauce%20One%20OFL.txt))
