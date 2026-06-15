
# Cyberpunk 2077 Archipelago Mod

A mod and client for Cyberpunk 2077 for [Archipelago](https://archipelago.gg/)

## ⚠️ WARNING: Experimental Release
**This current release is NOT recommended for use in large community async environments.**
It is currently prone to **generation issues**. Thar be dragons!
## ⚠️ WARNING: Other Mod Support
I do not support adding other mods on top of this one, nor will i assist if this mod does not work with other mods installed. Only the mods listed in the Requirements are supported.
---

## What does this do?
If enabled, you will be restricted by District and be unable to travel to those districts until you aquire the access token from the multiworld.
You can get extra items suchs as Eddies, Quckhacks, Burrito from the multi-world.
More will come in due time.
***Have Patience***

# Installation

## Requirements

You will need the following mods for this to work:
| Mod          | Github Link | Nexusmods Link |
| ----------------- | ------------------------------------------------------------------ | ------------------------------------------- |
| RedScript 0.5.31 | [Github Link](https://github.com/jac3km4/redscript)| [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/1511)
| TweakXL | [Github Link](https://github.com/psiberx/cp2077-tweak-xl) | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/4197)
| ArchiveXL | [Github Link](https://github.com/psiberx/cp2077-archive-xl) | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/4198)
| Cyber Engine Tweaks | [Github Link](https://github.com/maximegmd/CyberEngineTweaks) | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/107)
| Codeware | [Github Link](https://github.com/psiberx/cp2077-codeware) | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/7780)
| Red4Ext | [Github Link](https://github.com/wopss/RED4ext) | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/2380)
| RedSocket | [Github Link](https://github.com/rayshader/cp2077-red-socket) |
| Phone Extension | Unknown | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/24949)

## Mod Installation
Download both the ```cyberpunk2077.apworld``` and ```CyberpunkArchipelagoMod.zip``` from [Releases](https://github.com/247Tossing/cyberpunk_archipelago/releases/tag/Latest)

take the ```CyberpunkArchipelagoMod.zip``` and extract to your Cyberpunk 2077 Root folder. This should contain the ```r6``` and ```bin``` folders.

### Native plugin (`CyberpunkAP.dll`) and RedScript

Archipelago exposes game functions through **native** bindings declared in RedScript (for example `APNativeBindings.reds`). Those declarations must match the **`CyberpunkAP.dll`** shipped under `red4ext/plugins/CyberpunkAP/` in your game root.

If you update **only** `r6/scripts/...` (e.g. from git) but leave an **older** `CyberpunkAP.dll` in place, RED4ext may report **invalid native definitions** and refuse to start. After any change that adds or renames natives in `APNativeBindings.reds`, rebuild the native plugin and copy **`CyberpunkAP.dll`** (and `APCpp.dll` if present next to it) from the mod’s `Cyberpunk2077/red4ext/plugins/CyberpunkAP/` into the same path under your Cyberpunk 2077 install—**always deploy scripts and the RED4ext plugin together**.

Next, open the Archipelago Launcher and drag the ```cyberpunk2077.apworld``` file onto the launcher.

You ***MUST*** restart the launcher before it will show up.
# Usage

## Using the Mod
1. After you restart the launcher, launch the Cyberpunk 2077 Client.
2. Connect to the AP Server and enter your save slot.
3. The client will provide the ```localhost:port``` for the local TCP socket
4. Start up Cyberpunk 2077
5. If you havent already, set a keybind for the CET overlay, if you have, skip this step. If need to reset it. Refer to the Cyber Engine Tweaks documentation on how to fix that.
6. From the CET overlay, put in either ```locahost``` or ```127.0.0.1``` in the Server IP field, and the Port you got from the AP Client into the ```Port``` field.
7. Profit. Have Fun.

## Linux Users (like me!)

Before anything follow this guide: [Cyber Engine Tweaks Linux Instructions](https://wiki.redmodding.org/cyber-engine-tweaks/getting-started/installing/linux-proton)

### For Heroic:
1. Open the game settings
2. Go to Advanced
3. Scroll down to Environment Variables
4. in the ```Variable Name```, put ```WINEDLLOVERRIDES```
5. in the ```Value```, put ```"version,winmm=n,b"```

### For Steam:
1. Rightclick the game in Steam
2. Select ```Properties```
3. Under ```Launch Options```, ```put in WINEDLLOVERRIDES="version,winmm=n,b" %command%```

---

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

---

## What if something is broken?
Open an [Issue](https://github.com/247Tossing/cyberpunk_archipelago/issues/new/choose)

### What to include in your issue:
1. Your spoiler.txt (if generated locally you can find it in ```{archipelago install dir}\output\(zip used in generation)\spoiler.txt```
2. CET logs (you can find them in ```{game dir}\bin\x64\plugins\cyber_engine_tweaks\scripting.log```
3. Client Logs (you can find them in ```{archipelago install dir}\logs\Cyperpunk2077Client(some stuff).log```
4. Server Logs (if hosting locally they will be in ```{archipelago install dir}\logs\Server(some stuff).log```
5. A good description of what exactly the issue is. I can't help if i don't know what im looking for.
