# Thin IDF-component wrapper around the vendored pngle PNG decoder
# (cloned to ~/u-developer/pngle by u-developer/setup.sh). pngle.c pulls miniz in
# header-only mode; miniz.c is compiled here for the implementation.
set(PNGLE_SRC "$ENV{HOME}/u-developer/pngle/src")

idf_component_register(
    SRCS "${PNGLE_SRC}/pngle.c" "${PNGLE_SRC}/miniz.c"
    INCLUDE_DIRS "${PNGLE_SRC}"
)

# Third-party C — don't let its warnings fail our build.
target_compile_options(${COMPONENT_LIB} PRIVATE -w)
