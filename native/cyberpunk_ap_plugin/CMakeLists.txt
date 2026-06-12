add_library(cyberpunk_ap_plugin SHARED
    src/plugin.cpp
    src/APBridge.cpp
    src/RedscriptAPI.cpp
)

target_include_directories(cyberpunk_ap_plugin PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/APCpp
    ${CMAKE_SOURCE_DIR}/RED4ext.SDK/include
)

target_link_libraries(cyberpunk_ap_plugin PRIVATE APCpp)

target_compile_definitions(cyberpunk_ap_plugin PRIVATE
    WIN32_LEAN_AND_MEAN
    NOMINMAX
)

set_target_properties(cyberpunk_ap_plugin PROPERTIES
    OUTPUT_NAME "CyberpunkAP"
)

set(CYBERPUNK_PLUGIN_DIR "${CMAKE_SOURCE_DIR}/../Cyberpunk2077/red4ext/plugins/CyberpunkAP")
add_custom_command(TARGET cyberpunk_ap_plugin POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CYBERPUNK_PLUGIN_DIR}"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "$<TARGET_FILE:cyberpunk_ap_plugin>"
        "${CYBERPUNK_PLUGIN_DIR}/$<TARGET_FILE_NAME:cyberpunk_ap_plugin>"
)
