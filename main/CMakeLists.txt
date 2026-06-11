idf_component_register(
    SRCS "main.cpp"
    INCLUDE_DIRS ".."
    REQUIRES commander_runner esp_http_client esp-tls mbedtls   # weather (wttr.in) + news (newsapi) over HTTPS
    EMBED_FILES "fonts/Karla-Regular.ttf"   # text rendering — handed to IpstubeModule::loadFont
    EMBED_TXTFILES "certs/gts_root_r4.pem"  # newsapi.org root CA (null-terminated PEM string)
)
