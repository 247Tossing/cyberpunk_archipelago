# Install script for directory: E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files (x86)/CyberpunkArchipelagoNative")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Development" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/Debug/zsd.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/Release/zs.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/MinSizeRel/zs.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/RelWithDebInfo/zs.lib")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib/ZLIB-static.cmake")
    file(DIFFERENT _cmake_export_file_changed FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib/ZLIB-static.cmake"
         "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/CMakeFiles/Export/93f1ef598f1f2f8b07b376ab081bbce6/ZLIB-static.cmake")
    if(_cmake_export_file_changed)
      file(GLOB _cmake_old_config_files "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib/ZLIB-static-*.cmake")
      if(_cmake_old_config_files)
        string(REPLACE ";" ", " _cmake_old_config_files_text "${_cmake_old_config_files}")
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib/ZLIB-static.cmake\" will be replaced.  Removing files [${_cmake_old_config_files_text}].")
        unset(_cmake_old_config_files_text)
        file(REMOVE ${_cmake_old_config_files})
      endif()
      unset(_cmake_old_config_files)
    endif()
    unset(_cmake_export_file_changed)
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib" TYPE FILE FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/CMakeFiles/Export/93f1ef598f1f2f8b07b376ab081bbce6/ZLIB-static.cmake")
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib" TYPE FILE FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/CMakeFiles/Export/93f1ef598f1f2f8b07b376ab081bbce6/ZLIB-static-debug.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib" TYPE FILE FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/CMakeFiles/Export/93f1ef598f1f2f8b07b376ab081bbce6/ZLIB-static-minsizerel.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib" TYPE FILE FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/CMakeFiles/Export/93f1ef598f1f2f8b07b376ab081bbce6/ZLIB-static-relwithdebinfo.cmake")
  endif()
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib" TYPE FILE FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/CMakeFiles/Export/93f1ef598f1f2f8b07b376ab081bbce6/ZLIB-static-release.cmake")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/zlib" TYPE FILE FILES
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/ZLIBConfig.cmake"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/ZLIBConfigVersion.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Development" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/zconf.h"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/zlib.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Docs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/man/man3" TYPE FILE FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/zlib.3")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Docs" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/zlib/zlib" TYPE FILE FILES
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/LICENSE"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/doc/algorithm.txt"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/doc/crc-doc.1.0.pdf"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/doc/rfc1950.txt"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/doc/rfc1951.txt"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/doc/rfc1952.txt"
    "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/zlib/doc/txtvsbin.txt"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Development" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/zlib.pc")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/test/cmake_install.cmake")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/_deps/zlib-build/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
