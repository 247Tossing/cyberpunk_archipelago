# Contributing

End-user install and usage: [README.md](README.md).

## How the repo is organized

This project has three main pieces that must stay in sync:

| Path | Role |
|------|------|
| `worlds/cyberpunk2077/` | Archipelago apworld — generation logic, locations, items, options |
| `Cyberpunk2077/` | Game mod overlay copied into the Cyberpunk 2077 install (`r6/`, `bin/`, `red4ext/`) |
| `native/` | RED4ext plugin that builds `CyberpunkAP.dll` (Archipelago connection via vendored APCpp) |

At runtime the game connects **directly** to an Archipelago server — there is no separate Python client in this repo.

```
CET UI (init.lua)
  → RedScript (TCPClient.reds, APGameSystem.reds, …)
    → native bindings (APNativeBindings.reds)
      → CyberpunkAP.dll (APCpp WebSocket client)
        → Archipelago server
```

**ID sync:** `locations.py` and `items.py` are the source of truth for Archipelago IDs. The build regenerates `Cyberpunk2077/r6/scripts/.../APArchipelagoIdMappings.reds` from them and packages the matching `.apworld`. If those drift, location checks and item delivery break silently.

**Native sync:** `APNativeBindings.reds` declares the C++ functions exported by `CyberpunkAP.dll`. If you change one without rebuilding/redeploying the other, RED4ext reports invalid native definitions and the game will not start.

## Prerequisites

- **Windows** — native plugin builds and CI both target Windows (Visual Studio + CMake).
- **Python ~3.12** — world/apworld tooling.
- **[Archipelago](https://github.com/ArchipelagoMW/Archipelago) source checkout** — sibling folder `../Archipelago`, or set `ARCHIPELAGO_ROOT`.
- **Cyberpunk 2077** with the dependency mods listed in the README (RedScript, CET, Codeware, Red4Ext, RedSocket, Phone Extension).

## Dev environment setup

```cmd
git clone --recurse-submodules https://github.com/247Tossing/cyberpunk_archipelago.git
cd cyberpunk_archipelago
```

If you already cloned without submodules:

```cmd
git submodule update --init --recursive
```

Clone Archipelago next to this repo (or anywhere — pass `--archipelago-root`):

```cmd
cd ..
git clone https://github.com/ArchipelagoMW/Archipelago.git
```

The build scripts auto-link `worlds/cyberpunk2077` into the Archipelago checkout (junction on Windows, symlink elsewhere). You can also create that link manually if you prefer to work inside Archipelago directly:

```cmd
mklink /J "..\Archipelago\worlds\cyberpunk2077" "%CD%\worlds\cyberpunk2077"
```

Install Archipelago's Python deps once:

```cmd
cd ..\Archipelago
python -m pip install -r requirements.txt
python ModuleUpdate.py -y
```

## Building

### Full release (recommended first build)

Produces everything in `build/`:

- `cyberpunk2077.apworld`
- `CyberpunkArchipelagoMod_(<version>).zip`
- `cyberpunk2077_poptracker_(<version>).zip`

```cmd
python tools\build_release.py --archipelago-root ..\Archipelago
```

This runs, in order: submodule fetch → CMake Release build of `CyberpunkAP.dll` → Archipelago world link → apworld build (including RedScript ID regeneration) → PopTracker pack → mod zip.

Version comes from `world_version` in `worlds/cyberpunk2077/archipelago.json` (must be three integers, e.g. `0.6.0`). Git release tags use a matching `v` prefix (`v0.6.0`).

Useful flags when iterating:

| Flag | When |
|------|------|
| `--skip-native` | RedScript/world-only changes; DLL already built |
| `--skip-requirements` | Archipelago deps already installed |
| `--skip-poptracker` | Skip PopTracker pack |

On Windows, release builds configure CMake with OpenSSL (`-DUSE_OPEN_SSL=ON`). CI installs OpenSSL via Chocolatey; for local native builds you need OpenSSL available to CMake or the configure step may fail.

### Targeted builds

| You changed | Run |
|-------------|-----|
| `locations.py` / `items.py` | `python tools\build_cyberpunk2077_apworld.py --archipelago-root ..\Archipelago` |
| `native/` or `APNativeBindings.reds` | `cmake -S native -B native/build` then `cmake --build native/build --config Release` |
| RedScript / CET Lua only | No build step — deploy overlay (below) |
| PopTracker templates or location/item tables | `python tools\build_poptracker_pack.py --archipelago-root ..\Archipelago` |

Native-only build output lands in `Cyberpunk2077/red4ext/plugins/CyberpunkAP/CyberpunkAP.dll`.

More detail on individual scripts: [`tools/README.md`](tools/README.md). Native project layout: [`native/README.md`](native/README.md).

## Testing in-game

Copy the contents of `Cyberpunk2077/` into your Cyberpunk 2077 root (same layout as extracting the release zip: `r6/`, `bin/`, `red4ext/`).

After native or RedScript binding changes, deploy **both** updated scripts and `CyberpunkAP.dll` together.

Drop a freshly built `cyberpunk2077.apworld` into the Archipelago launcher (restart the launcher if it was already open). Host or join a multiworld, then in-game open the CET overlay (~), enter server IP/port/slot name, and connect.

Logs: `{game dir}\bin\x64\plugins\cyber_engine_tweaks\scripting.log`

## Reporting issues

Open an [issue](https://github.com/247Tossing/cyberpunk_archipelago/issues/new/choose) with:

1. `spoiler.txt` from generation
2. CET log (`scripting.log`)
3. Archipelago server log (if local)
4. Steps to reproduce

## Credits

### Third-party libraries (native plugin)

| Library | Author | Purpose |
|---------|--------|---------|
| [APCpp](https://github.com/N00byKing/APCpp) | N00byKing | Archipelago C++ client (vendored + modified) |
| [RED4ext.SDK](https://github.com/WopsS/RED4ext.SDK) | WopsS | RED4ext plugin SDK |
| [jsoncpp](https://github.com/open-source-parsers/jsoncpp) | open-source-parsers | APCpp dependency |
| [IXWebSocket](https://github.com/machinezone/IXWebSocket) | Machine Zone | APCpp dependency |
| [zlib](https://github.com/madler/zlib) | Mark Adler | APCpp dependency |
