# cmdr-ipstube

A smart clock firmware for the **IPSTube** (classic ESP32 + six ST7789 135×240 IPS
displays + WS2812 ambient LEDs + DS1302 RTC), built on the
[commander](https://github.com/gbryant/commander) embedded shell framework.

## What it does

- **Font clock** — `HH:MM` rendered from a TTF (Karla) with a dot colon, a
  day/date panel, and a live weather panel. `face png` switches to the original
  baked flip-clock digits.
- **Weather** (panel 5) — current temp + condition + forecast low/high from
  forecast.weather.gov (NWS), refreshed every 30 min.
- **News** — top headlines from newsapi.org, hourly. Show as a full-strip marquee
  (`news`), or vertically scroll them on panel 5 (`panel5 news`).
- **Display scenes** — a single scene runner drives the active view: `clock`,
  `marquee <text>`, `read <d|all> <text>` (vertical reader), `hscroll`, `news`,
  and `hold` (yield the displays so an external host can push content). `rotate
  on` cycles clock ↔ news on a timer.
- **Live tuning** — `tune` (clock layout), `mspeed`/`msize` (marquee),
  `news speed` (news scroll). Type a command bare for usage.

## Build

ESP-IDF v5+. Copy `secrets.h.example` → `secrets.h` and fill in WiFi + newsapi key.

```bash
./build      # idf.py build into build-esp32/
./upload     # flash
./monitor    # serial console
./bum        # build + upload + monitor
```

The commander framework is pulled via FetchContent (see `CMakeLists.txt`); update
it with the normal cmdr flow. Display/text features live in commander's `ipstube`
module; the clock/weather/news app logic is in `main/main.cpp`.
