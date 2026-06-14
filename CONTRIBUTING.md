# Contributing

This document covers building from source, deploying development builds, and
third-party credits. For end-user installation and usage, see [README.md](README.md).

## Getting the source

This repo uses git submodules for native dependencies. After cloning, run:

```cmd
git submodule update --init --recursive
```

## Native plugin (`CyberpunkAP.dll`)

The RED4ext native plugin embeds the Archipelago C++ client directly into the
game. Source lives under [`native/`](native/); see [`native/README.md`](native/README.md)
for project layout and build details.

### Build (Windows)

From the `native/` folder:

```cmd
cmake -S . -B build
cmake --build build --config Release
```

The output `CyberpunkAP.dll` is copied to
`Cyberpunk2077/red4ext/plugins/CyberpunkAP/` after a successful build.

### RedScript and native bindings

Archipelago exposes game functions through **native** bindings declared in
RedScript (for example `APNativeBindings.reds`). Those declarations must match
the **`CyberpunkAP.dll`** shipped under `red4ext/plugins/CyberpunkAP/` in your
game root.

If you update **only** `r6/scripts/...` (e.g. from git) but leave an **older**
`CyberpunkAP.dll` in place, RED4ext may report **invalid native definitions**
and refuse to start. After any change that adds or renames natives in
`APNativeBindings.reds`, rebuild the native plugin and copy **`CyberpunkAP.dll`**
(and `APCpp.dll` if present next to it) from the mod's
`Cyberpunk2077/red4ext/plugins/CyberpunkAP/` into the same path under your
Cyberpunk 2077 install—**always deploy scripts and the RED4ext plugin together**.

## Release and world build tooling

Python scripts under [`tools/`](tools/) build the apworld, PopTracker pack, and
mod zip. See [`tools/README.md`](tools/README.md) for the full pipeline,
versioning, and CI workflow.

Quick entry point for a full release build:

```cmd
python tools\build_release.py --archipelago-root <ARCHIPELAGO>
```

## Reporting issues

Open an [Issue](https://github.com/247Tossing/cyberpunk_archipelago/issues/new/choose).

### What to include

1. Your spoiler.txt (if generated locally you can find it in `{archipelago install dir}\output\(zip used in generation)\spoiler.txt`)
2. CET logs (you can find them in `{game dir}\bin\x64\plugins\cyber_engine_tweaks\scripting.log`)
3. Client Logs (you can find them in `{archipelago install dir}\logs\Cyperpunk2077Client(some stuff).log`)
4. Server Logs (if hosting locally they will be in `{archipelago install dir}\logs\Server(some stuff).log`)
5. A good description of what exactly the issue is. I can't help if i don't know what im looking for.

## Credits & Acknowledgements

### Mod Author

- **247Tossing** — Cyberpunk 2077 Archipelago Mod

### Third-Party Libraries (Native Plugin)

| Library | Author | Purpose |
|---------|--------|---------|
| [APCpp](https://github.com/N00byKing/APCpp) | N00byKing | Archipelago C++ client library (vendored + modified) |
| [RED4ext.SDK](https://github.com/WopsS/RED4ext.SDK) | WopsS | REDengine 4 plugin SDK headers |
| [RED4ext](https://github.com/WopsS/RED4ext) | WopsS | RED4ext loader framework (reference) |
| [Red4Ext-template](https://github.com/ssamjoel/Red4Ext-template) | ssamjoel | Plugin project scaffold |
| [jsoncpp](https://github.com/open-source-parsers/jsoncpp) | open-source-parsers | JSON parsing (APCpp dependency) |
| [IXWebSocket](https://github.com/machinezone/IXWebSocket) | Machine Zone | WebSocket client (APCpp dependency) |
| [zlib](https://github.com/madler/zlib) | Mark Adler | Compression (APCpp dependency) |

### Frameworks

- [Archipelago](https://archipelago.gg/) — multiworld randomizer framework
- [RedScript](https://github.com/jac3km4/redscript) — Cyberpunk 2077 scripting framework
- [Cyber Engine Tweaks](https://github.com/maximegmd/CyberEngineTweaks) — Cyberpunk 2077 mod engine
