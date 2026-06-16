cmake_minimum_required(VERSION 3.20)

if(NOT DEFINED ENV{IDF_PATH})
    message(FATAL_ERROR "IDF_PATH not set — run 'esp' to load the ESP-IDF environment")
endif()

# Download commander source before IDF initializes (FetchContent_Populate
# does download only — does not process commander's CMakeLists.txt).
include(FetchContent)
FetchContent_Declare(commander
    GIT_REPOSITORY https://github.com/gbryant/commander.git
    GIT_TAG        main
)
FetchContent_Populate(commander)

set(COMMANDER_ROOT ${commander_SOURCE_DIR})
list(APPEND EXTRA_COMPONENT_DIRS ${commander_SOURCE_DIR}/runners/esp32)

set(COMMANDER_ENABLE_IPSTUBE ON CACHE BOOL "" FORCE)  # commander ipstube (esp_lcd)
set(COMMANDER_ENABLE_WS2812 ON CACHE BOOL "" FORCE)  # commander ws2812 (RMT)
set(COMMANDER_ENABLE_OTA ON CACHE BOOL "" FORCE)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(cmdr-ipstube)

# Stamp the project name + build number into the firmware so `version` reports the
# running build (and bum-ota can confirm an OTA took). Provided by the commander
# runner's project_include.cmake; must be called after project().
commander_stamp_version()

# Build the LittleFS image from storage/ and flash it to the `storage` partition
# alongside the app (idf.py flash / ./upload). Holds the font + face PNGs.
littlefs_create_partition_image(storage ${CMAKE_SOURCE_DIR}/storage FLASH_IN_PROJECT)
