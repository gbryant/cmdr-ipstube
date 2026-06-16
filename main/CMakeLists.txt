idf_component_register(
    SRCS "main.cpp"
    INCLUDE_DIRS ".."
    REQUIRES commander_runner esp_http_client esp-tls mbedtls   # weather (wttr.in) + news (newsapi) over HTTPS
             esp_littlefs pngle                                  # /storage FS: fonts + face PNGs
             nvs_flash esp_timer                                 # persisted look (NVS) + OTA-cue timing
    EMBED_FILES "fonts/Karla-Regular.ttf"   # fallback font — FS copy preferred (IpstubeModule::loadFont)
    EMBED_TXTFILES "certs/gts_root_r4.pem"  # newsapi.org root CA (null-terminated PEM string)
)
