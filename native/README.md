# CyberpunkArchipelagoPlugin — Red4EXT Native Plugin

This directory contains the C++ Red4EXT plugin that replaces the Python bridge
architecture with a direct Archipelago server connection powered by
[APCpp](https://github.com/N00byKing/APCpp).

## Architecture

```
Cyberpunk 2077
  └── Red4EXT loader
        └── CyberpunkArchipelagoPlugin.dll          ← this project
              ├── APBridge  (native class, RedLib RTTI)
              │     └── APCpp library  ─────────────────── Archipelago server
              └── Exposes APNativeClient to RedScript
                    └── TCPClient.reds calls APNativeClient
                          └── APGameSystem / APGameState (unchanged)
```

No Python bridge or separate launcher process is required.

---

## Prerequisites

| Tool | Notes |
|------|-------|
| **Visual Studio 2022** (or Build Tools) | MSVC v143, Windows SDK 10.0 |
| **CMake ≥ 3.21** | In PATH |
| **Python 3** | For `generate_tables.py` |
| **Git** | For FetchContent submodules |
| **CLion** or **Rider** | JetBrains IDE (optional but recommended) |

---

## Building

### CLion / Rider (recommended)

1. Open the repository root in CLion/Rider.
2. CLion will detect `native/CMakeLists.txt` — add it as a CMake project
   (`File → Open → Select folder`, or `File → CMake → Add CMake project`).
3. Set the **CMake profile** to `Release | x64` (MSVC toolchain).
4. Build → the DLL lands in `build/CyberpunkArchipelagoPlugin.dll`.

### Command line

```bat
cd native
cmake -B build -A x64 -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

The first build downloads RED4ext.SDK, RedLib, and APCpp via FetchContent —
allow several minutes on a cold start.

---

## Deployment

After building, copy the DLL to your Cyberpunk 2077 installation:

```
<game root>\red4ext\plugins\CyberpunkArchipelagoPlugin\CyberpunkArchipelagoPlugin.dll
```

Then install the RedScript files as usual (inside `r6\scripts\`).

---

## Regenerating mapping tables

`src/ItemMapping.hpp`, `src/LocationMapping.hpp`, and `src/DisplayNameMapping.hpp`
are auto-generated from the Python world data.  Whenever you add new items or
locations to `worlds/cyberpunk2077/items.py` or `locations.py`, re-run:

```bash
python3 native/generate_tables.py      # from the repo root
```

CMake also runs this script automatically during configuration.

---

## Connection details

With the native plugin the CET overlay fields change:

| Field | Old (Python bridge) | New (APCpp direct) |
|-------|---------------------|--------------------|
| Host  | `127.0.0.1`         | e.g. `archipelago.gg` |
| Port  | `51234`             | e.g. `38281` |
| Slot Name | not used      | your AP slot name |
| Password | not used       | room password (if any) |

The Python `client.py` and the Archipelago Launcher are **not needed** for
in-game connectivity; you only need them if you want to host your own
Archipelago server locally.
