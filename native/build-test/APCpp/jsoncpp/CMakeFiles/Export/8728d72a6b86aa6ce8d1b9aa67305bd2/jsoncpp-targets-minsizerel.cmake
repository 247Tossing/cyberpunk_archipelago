#----------------------------------------------------------------
# Generated CMake target import file for configuration "MinSizeRel".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "jsoncpp_static" for configuration "MinSizeRel"
set_property(TARGET jsoncpp_static APPEND PROPERTY IMPORTED_CONFIGURATIONS MINSIZEREL)
set_target_properties(jsoncpp_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_MINSIZEREL "CXX"
  IMPORTED_LOCATION_MINSIZEREL "${_IMPORT_PREFIX}/lib/jsoncpp.lib"
  )

list(APPEND _cmake_import_check_targets jsoncpp_static )
list(APPEND _cmake_import_check_files_for_jsoncpp_static "${_IMPORT_PREFIX}/lib/jsoncpp.lib" )

# Import target "jsoncpp_object" for configuration "MinSizeRel"
set_property(TARGET jsoncpp_object APPEND PROPERTY IMPORTED_CONFIGURATIONS MINSIZEREL)
set_target_properties(jsoncpp_object PROPERTIES
  IMPORTED_COMMON_LANGUAGE_RUNTIME_MINSIZEREL ""
  IMPORTED_OBJECTS_MINSIZEREL "${_IMPORT_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object/json_reader.obj;${_IMPORT_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object/json_value.obj;${_IMPORT_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object/json_writer.obj"
  )

list(APPEND _cmake_import_check_targets jsoncpp_object )
list(APPEND _cmake_import_check_files_for_jsoncpp_object "${_IMPORT_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object/json_reader.obj;${_IMPORT_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object/json_value.obj;${_IMPORT_PREFIX}/lib/objects-MinSizeRel/jsoncpp_object/json_writer.obj" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
