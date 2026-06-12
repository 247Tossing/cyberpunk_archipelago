#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "ZLIB::ZLIBSTATIC" for configuration "RelWithDebInfo"
set_property(TARGET ZLIB::ZLIBSTATIC APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(ZLIB::ZLIBSTATIC PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELWITHDEBINFO "C"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/zs.lib"
  )

list(APPEND _cmake_import_check_targets ZLIB::ZLIBSTATIC )
list(APPEND _cmake_import_check_files_for_ZLIB::ZLIBSTATIC "${_IMPORT_PREFIX}/lib/zs.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
