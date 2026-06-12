cmake_minimum_required(VERSION 3.12...3.31)

project(
    zlib_find_package_test
    LANGUAGES C
    VERSION 1.4.1.1)

enable_testing()
option(ZLIB_BUILD_TESTING "" OFF)
option(ZLIB_BUILD_SHARED "" OFF)
option(ZLIB_BUILD_STATIC "" ON)

add_subdirectory(E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib ${CMAKE_CURRENT_BINARY_DIR}/zlib
                 EXCLUDE_FROM_ALL)

if(ZLIB_BUILD_SHARED)
    add_executable(test_example E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/test/example.c)
    target_link_libraries(test_example ZLIB::ZLIB)

    if(NOT ${CMAKE_SHARED_LIBRARY_SUFFIX} STREQUAL ".dll")
        add_test(NAME zlib_test_example_shared COMMAND test_example)
    endif(NOT ${CMAKE_SHARED_LIBRARY_SUFFIX} STREQUAL ".dll")
endif(ZLIB_BUILD_SHARED)

if(ZLIB_BUILD_STATIC)
    add_executable(test_example_static E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/test/example.c)
    target_link_libraries(test_example_static ZLIB::ZLIBSTATIC)
    add_test(NAME zlib_test_example_static COMMAND test_example_static)
endif(ZLIB_BUILD_STATIC)
