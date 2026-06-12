# Native plugin bootstrap

This folder now contains:

- `APCpp/`: cloned Archipelago C++ client library (with submodules)
- `cyberpunk_ap_plugin/`: initial DLL wrapper target around APCpp

## Configure and build (Windows)

From this `native` folder:

1. Configure:
   - `cmake -S . -B build`
2. Build:
   - `cmake --build build --config Release`

Output DLL target:

- `CyberpunkArchipelagoPlugin.dll`

## Current status

This is a first scaffold to begin plugin DLL work. It currently exports:

- `APPlugin_Initialize`
- `APPlugin_Start`
- `APPlugin_Shutdown`
- `APPlugin_SendLocationCheck`
- `APPlugin_SendDeathLink`
- `APPlugin_StoryComplete`
- `APPlugin_GetConnectionStatus`

Next step is binding these exports into your in-game native hook layer (for example, RED4ext plugin entry points) and routing real game events into the callbacks.
