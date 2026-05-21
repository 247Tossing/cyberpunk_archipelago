cmake_minimum_required(VERSION 3.21)

project(CyberpunkArchipelagoPlugin VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ---------------------------------------------------------------------------
# Platform guard – Cyberpunk 2077 / RED4ext only runs on Windows x64.
# ---------------------------------------------------------------------------
if(NOT WIN32)
    message(FATAL_ERROR "This plugin targets Windows x64 only (Cyberpunk 2077).")
endif()

# ---------------------------------------------------------------------------
# Dependencies via FetchContent
# ---------------------------------------------------------------------------
include(FetchContent)

# --- RED4ext.SDK ---
FetchContent_Declare(
    red4ext_sdk
    GIT_REPOSITORY https://github.com/WopsS/RED4ext.SDK.git
    GIT_TAG        master          # pin to a release tag for reproducible builds
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(red4ext_sdk)

# --- RedLib (optional, simplifies RTTI registration significantly) ---
FetchContent_Declare(
    redlib
    GIT_REPOSITORY https://github.com/psiberx/cp2077-red-lib.git
    GIT_TAG        master
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(redlib)

# --- APCpp ---
# Clone recursively: git submodule add https://github.com/N00byKing/APCpp vendor/APCpp
# OR let CMake fetch it:
FetchContent_Declare(
    apcpp
    GIT_REPOSITORY https://github.com/N00byKing/APCpp.git
    GIT_TAG        main
    GIT_SUBMODULES "IXWebSocket" "jsoncpp" "zlib"
    # APCpp ships with IXWebSocket, jsoncpp, and zlib as submodules.
    GIT_SHALLOW    FALSE            # needs submodules so can't be shallow
)
FetchContent_MakeAvailable(apcpp)

# APCpp doesn't expose a modern CMake target by default.
# Build it from sources alongside our plugin.
set(APCPP_SRC_DIR ${apcpp_SOURCE_DIR})

# IXWebSocket needs mbedtls or openssl. APCpp bundles mbedtls as a tarball;
# the CMakeLists in IXWebSocket can find it automatically if USE_TLS is set.
set(USE_TLS          ON  CACHE BOOL "" FORCE)
set(USE_OPEN_SSL     OFF CACHE BOOL "" FORCE)
set(USE_MBED_TLS     ON  CACHE BOOL "" FORCE)
set(USE_MBEDTLS_STATIC_LIBS ON CACHE BOOL "" FORCE)

# Build IXWebSocket as a library target
add_subdirectory(${APCPP_SRC_DIR}/IXWebSocket ixwebsocket_build EXCLUDE_FROM_ALL)

# jsoncpp
add_subdirectory(${APCPP_SRC_DIR}/jsoncpp jsoncpp_build EXCLUDE_FROM_ALL)

# zlib (needed by IXWebSocket for compression)
add_subdirectory(${APCPP_SRC_DIR}/zlib zlib_build EXCLUDE_FROM_ALL)

# APCpp itself (static library built from its two source files + Gifting)
add_library(apcpp_lib STATIC
    ${APCPP_SRC_DIR}/Archipelago.cpp
    ${APCPP_SRC_DIR}/Archipelago_Gifting.cpp
    ${APCPP_SRC_DIR}/Archipelago_DataStorageSim.cpp
)
target_include_directories(apcpp_lib PUBLIC ${APCPP_SRC_DIR})
target_compile_definitions(apcpp_lib PUBLIC WIN32=1)
target_link_libraries(apcpp_lib PUBLIC ixwebsocket jsoncpp_lib zlibstatic)

# ---------------------------------------------------------------------------
# Re-generate mapping tables before every build (requires Python 3)
# ---------------------------------------------------------------------------
find_program(PYTHON_EXECUTABLE NAMES python3 python REQUIRED)
add_custom_command(
    OUTPUT
        ${CMAKE_CURRENT_SOURCE_DIR}/src/ItemMapping.hpp
        ${CMAKE_CURRENT_SOURCE_DIR}/src/LocationMapping.hpp
        ${CMAKE_CURRENT_SOURCE_DIR}/src/DisplayNameMapping.hpp
    COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/generate_tables.py
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/..
    COMMENT "Generating C++ item/location mapping tables from Python world data..."
    DEPENDS
        ${CMAKE_CURRENT_SOURCE_DIR}/generate_tables.py
        ${CMAKE_CURRENT_SOURCE_DIR}/../worlds/cyberpunk2077/items.py
        ${CMAKE_CURRENT_SOURCE_DIR}/../worlds/cyberpunk2077/locations.py
)
add_custom_target(generate_mappings DEPENDS
    ${CMAKE_CURRENT_SOURCE_DIR}/src/ItemMapping.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/LocationMapping.hpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/DisplayNameMapping.hpp
)

# ---------------------------------------------------------------------------
# Plugin DLL
# ---------------------------------------------------------------------------
add_library(CyberpunkArchipelagoPlugin SHARED
    src/main.cpp
    src/APBridge.cpp
)

add_dependencies(CyberpunkArchipelagoPlugin generate_mappings)

target_include_directories(CyberpunkArchipelagoPlugin PRIVATE
    src
    ${red4ext_sdk_SOURCE_DIR}/include
    ${redlib_SOURCE_DIR}/include
)

target_link_libraries(CyberpunkArchipelagoPlugin PRIVATE
    apcpp_lib
)

# RED4ext plugins must be plain DLLs – no default lib, no CRT as DLL.
target_compile_options(CyberpunkArchipelagoPlugin PRIVATE
    /W4
    /permissive-
)

# Plugin naming: Cyberpunk expects the DLL at:
#   <game_root>\red4ext\plugins\CyberpunkArchipelagoPlugin\CyberpunkArchipelagoPlugin.dll
set_target_properties(CyberpunkArchipelagoPlugin PROPERTIES
    OUTPUT_NAME "CyberpunkArchipelagoPlugin"
    PREFIX ""
    SUFFIX ".dll"
)

# ---------------------------------------------------------------------------
# Install helper – copies DLL to a staging folder for manual deployment
# ---------------------------------------------------------------------------
install(TARGETS CyberpunkArchipelagoPlugin
    RUNTIME DESTINATION "red4ext/plugins/CyberpunkArchipelagoPlugin"
)
