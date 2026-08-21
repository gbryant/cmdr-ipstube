# Thin IDF-component wrapper around the external pngle PNG decoder (MIT, kikuchan).
# Cloned to ~/u-developer/pngle by commander's scripts/setup-sdks.sh; override with
# $PNGLE_PATH. pngle.c pulls miniz in header-only mode; miniz.c is compiled here.
if(DEFINED ENV{PNGLE_PATH})
    set(PNGLE_SRC "$ENV{PNGLE_PATH}/src")
else()
    set(PNGLE_SRC "$ENV{HOME}/u-developer/pngle/src")
endif()

idf_component_register(
    SRCS "${PNGLE_SRC}/pngle.c" "${PNGLE_SRC}/miniz.c"
    INCLUDE_DIRS "${PNGLE_SRC}"
)

# Third-party C — don't let its warnings fail our build.
target_compile_options(${COMPONENT_LIB} PRIVATE -w)
