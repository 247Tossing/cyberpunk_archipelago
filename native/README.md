# Native Plugin (`CyberpunkAP.dll`)

This folder contains the RED4ext native plugin that embeds the Archipelago C++ client
directly into the game, allowing Cyberpunk 2077 to connect to an Archipelago server
without any separate Python client process.

## Structure

| Path | Purpose |
|------|---------|
| `APCpp/` | Vendored Archipelago C++ client library (see credits) |
| `cyberpunk_ap_plugin/` | RED4ext plugin — produces `CyberpunkAP.dll` |
| `RED4ext.SDK/` | REDengine 4 extension SDK headers (submodule) |
| `RED4ext/` | RED4ext loader source — reference only (submodule) |
| `Red4Ext-template/` | RED4ext plugin scaffold used to bootstrap this plugin (submodule) |

## Build (Windows)

From this `native/` folder:

```cmd
cmake -S . -B build
cmake --build build --config Release
```

The output `CyberpunkAP.dll` is automatically copied to
`../Cyberpunk2077/red4ext/plugins/CyberpunkAP/` after a successful build.

After building, deploy **both** `CyberpunkAP.dll` and your updated RedScript files
to your Cyberpunk 2077 install — they must stay in sync.

## After Cloning

This repo uses git submodules. Run the following to fetch all native dependencies:

```cmd
git submodule update --init --recursive
```

## Credits & Third-Party Libraries

### APCpp — Archipelago C++ Client
- **Author:** N00byKing  
- **Source:** https://github.com/N00byKing/APCpp  
- **License:** See `APCpp/LICENSE`  
- **Notes:** Vendored and modified for this project. Additions include:
  - `AP_GetLastConnectionError()` — exposes connection error details to RedScript
  - `AP_ConnectionStatus::Negotiating` — new intermediate connection state
  - Built as a **static** library (linked into `CyberpunkAP.dll`) instead of shared

#### APCpp Dependencies (submodules)
| Library | Author | Source |
|---------|--------|--------|
| jsoncpp | open-source-parsers | https://github.com/open-source-parsers/jsoncpp |
| IXWebSocket | Machine Zone | https://github.com/machinezone/IXWebSocket |
| zlib | Mark Adler | https://github.com/madler/zlib |

### RED4ext SDK
- **Author:** WopsS  
- **Source:** https://github.com/WopsS/RED4ext.SDK  
- **Purpose:** C++ headers for the REDengine 4 plugin API

### RED4ext (reference)
- **Author:** WopsS  
- **Source:** https://github.com/WopsS/RED4ext  
- **Purpose:** Reference source for the RED4ext loader framework

### Red4Ext-template (scaffold)
- **Author:** ssamjoel  
- **Source:** https://github.com/ssamjoel/Red4Ext-template  
- **Purpose:** Starter template used to bootstrap the plugin project structure
