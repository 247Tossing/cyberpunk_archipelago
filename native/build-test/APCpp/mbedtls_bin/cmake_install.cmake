# Install script for directory: E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls-3.6.4

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

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for each subdirectory.
  include("E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls_bin/framework/cmake_install.cmake")
  include("E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls_bin/include/cmake_install.cmake")
  include("E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls_bin/3rdparty/cmake_install.cmake")
  include("E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls_bin/library/cmake_install.cmake")
  include("E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls_bin/pkgconfig/cmake_install.cmake")

endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/mbedtls_bin/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
