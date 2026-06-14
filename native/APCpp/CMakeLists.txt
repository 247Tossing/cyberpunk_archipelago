cmake_minimum_required(VERSION 3.24)

project(APCpp)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_library(APCpp STATIC Archipelago.cpp Archipelago_DataStorageSim.cpp Archipelago_Gifting.cpp)

# Allows users to use APCpp as a dependency
target_include_directories(APCpp PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

set_target_properties(APCpp PROPERTIES PUBLIC_HEADER Archipelago.h)

set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(ENABLE_TESTING OFF CACHE BOOL "" FORCE)
set(ENABLE_PROGRAMS OFF CACHE BOOL "" FORCE)

# Enable TLS. On Windows, build mbedTLS
set(USE_TLS ON CACHE BOOL "Enable TLS support" FORCE)
# OpenSSL backend is intentionally disabled for release stability.
# Always force IXWebSocket/APCpp onto bundled mbedTLS so produced binaries
# do not rely on external OpenSSL runtime installs.
set(USE_MBED_TLS ON)
set(USE_MBED_TLS ON CACHE BOOL "" FORCE)
set(USE_OPEN_SSL OFF)
set(USE_OPEN_SSL OFF CACHE BOOL "" FORCE)

if (USE_MBED_TLS)
    set(APCPP_MBEDTLS_VER 3.6.4)
    set(MBEDTLS_TARBALL_URL "https://github.com/Mbed-TLS/mbedtls/releases/download/mbedtls-${APCPP_MBEDTLS_VER}/mbedtls-${APCPP_MBEDTLS_VER}.tar.bz2")
    set(MBEDTLS_TARBALL "${CMAKE_CURRENT_BINARY_DIR}/mbedtls-${APCPP_MBEDTLS_VER}.tar.bz2")
    
    if(NOT EXISTS "${MBEDTLS_TARBALL}")
        message(STATUS "Downloading mbedTLS ${APCPP_MBEDTLS_VER}...")
        file(DOWNLOAD "${MBEDTLS_TARBALL_URL}" "${MBEDTLS_TARBALL}")
    endif()
    
    execute_process(COMMAND ${CMAKE_COMMAND} -E remove -f mbedtls-${APCPP_MBEDTLS_VER})
    execute_process(
      COMMAND ${CMAKE_COMMAND} -E tar xjf ${MBEDTLS_TARBALL}
      WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    )
    set(USE_STATIC_MBEDTLS_LIBRARY ON CACHE BOOL "" FORCE)
    set(MBEDTLS_INCLUDE_DIRS ${CMAKE_CURRENT_BINARY_DIR}/mbedtls-${APCPP_MBEDTLS_VER}/include CACHE PATH "" FORCE)
    set(MBEDTLS_VERSION_GREATER_THAN_3 ${MBEDTLS_INCLUDE_DIRS} CACHE PATH "" FORCE)
    set(MBEDTLS_LIBRARY mbedtls CACHE STRING "" FORCE)
    set(MBEDX509_LIBRARY mbedx509 CACHE STRING "" FORCE)
    set(MBEDCRYPTO_LIBRARY mbedcrypto CACHE STRING "" FORCE)
    add_subdirectory(${CMAKE_CURRENT_BINARY_DIR}/mbedtls-${APCPP_MBEDTLS_VER} mbedtls_bin)
endif (USE_MBED_TLS)

# Attempt finding system version of zlib
if (NOT MINGW)
    find_package(ZLIB QUIET)
    if (ZLIB_FOUND)
        message("Using system zlib installation.")
    else()
        message("Using bundled zlib.")
    endif(ZLIB_FOUND)
endif (NOT MINGW)
if (MINGW OR NOT ZLIB_FOUND)
    # Force static build for zlib if not in system, and alias static to shared for IXWebsocket
    set(ZLIB_BUILD_SHARED OFF)
    include(FetchContent)
    FetchContent_Declare(
        zlib
        SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/zlib"
        OVERRIDE_FIND_PACKAGE
    )
    FetchContent_MakeAvailable(zlib)
    add_library(ZLIB::ZLIB ALIAS zlibstatic)
endif (MINGW OR NOT ZLIB_FOUND)

set(IXWEBSOCKET_INSTALL OFF CACHE BOOL "" FORCE)
add_subdirectory(IXWebSocket)
include_directories(IXWebSocket)
target_link_libraries(APCpp ixwebsocket)

if (MINGW)
    target_link_libraries(APCpp -static -static-libstdc++ -static-libgcc)
endif(MINGW)

# Attempt finding system version of JsonCpp
find_package(PkgConfig)
if (PKGCONFIG_FOUND AND (NOT MINGW) AND (NOT BUNDLED_JSONCPP))
    pkg_check_modules(JSONCPP jsoncpp)
    if (JSONCPP_FOUND)
        include_directories(${JSONCPP_INCLUDE_DIRS})
        target_link_libraries(APCpp ${JSONCPP_LDFLAGS})
    endif(JSONCPP_FOUND)
endif(PKGCONFIG_FOUND AND (NOT MINGW) AND (NOT BUNDLED_JSONCPP))

# No system version: Enable bundled
if((NOT JSONCPP_FOUND) OR BUNDLED_JSONCPP)
    set(JSONCPP_WITH_TESTS OFF CACHE BOOL "" FORCE)
    set(JSONCPP_WITH_POST_BUILD_UNITTEST OFF CACHE BOOL "" FORCE)
    add_subdirectory(jsoncpp)
    set_property(TARGET jsoncpp_static PROPERTY POSITION_INDEPENDENT_CODE ON)
    include_directories(jsoncpp/include)
    target_link_libraries(APCpp jsoncpp_static)
endif((NOT JSONCPP_FOUND) OR BUNDLED_JSONCPP)

if (WIN32)
    target_link_libraries(APCpp ws2_32)
endif(WIN32)

install(TARGETS APCpp PUBLIC_HEADER)
