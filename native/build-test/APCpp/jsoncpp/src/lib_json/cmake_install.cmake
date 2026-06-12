# Install script for directory: E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/APCpp/jsoncpp/src/lib_json

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

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/Debug/jsoncpp.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/Release/jsoncpp.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/MinSizeRel/jsoncpp.lib")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/RelWithDebInfo/jsoncpp.lib")
  endif()
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-Debug/jsoncpp_object" TYPE FILE RENAME "json_reader.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/Debug//json_reader.obj")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-Debug/jsoncpp_object" TYPE FILE RENAME "json_value.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/Debug//json_value.obj")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-Debug/jsoncpp_object" TYPE FILE RENAME "json_writer.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/Debug//json_writer.obj")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-Release/jsoncpp_object" TYPE FILE RENAME "json_reader.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/Release//json_reader.obj")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-Release/jsoncpp_object" TYPE FILE RENAME "json_value.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/Release//json_value.obj")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-Release/jsoncpp_object" TYPE FILE RENAME "json_writer.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/Release//json_writer.obj")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object" TYPE FILE RENAME "json_reader.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/MinSizeRel//json_reader.obj")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object" TYPE FILE RENAME "json_value.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/MinSizeRel//json_value.obj")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object" TYPE FILE RENAME "json_writer.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/MinSizeRel//json_writer.obj")
  elseif(CMAKE_INSTALL_CONFIG_NAME MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-RelWithDebInfo/jsoncpp_object" TYPE FILE RENAME "json_reader.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/RelWithDebInfo//json_reader.obj")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-RelWithDebInfo/jsoncpp_object" TYPE FILE RENAME "json_value.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/RelWithDebInfo//json_value.obj")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/objects-RelWithDebInfo/jsoncpp_object" TYPE FILE RENAME "json_writer.obj" FILES "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/jsoncpp_object.dir/RelWithDebInfo//json_writer.obj")
  endif()
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "E:/CyperpunkArchipelago/Cyberpunk_Archipelago_Mod/native/build-test/APCpp/jsoncpp/src/lib_json/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
