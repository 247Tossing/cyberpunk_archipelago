
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
| Cyber Engine Tweaks | [Github Link](https://github.com/maximegmd/CyberEngineTweaks) | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/107)
| Codeware | [Github Link](https://github.com/psiberx/cp2077-codeware) | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/7780)
| Red4Ext | [Github Link](https://github.com/wopss/RED4ext) | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/2380)
| RedSocket | [Github Link](https://github.com/rayshader/cp2077-red-socket) |
| Phone Extension | Unknown | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/24949)

## Mod Installation
Download the ```cyberpunk-archipelago-release-vXX.zip``` from [Releases](https://github.com/247Tossing/cyberpunk_archipelago/releases/tag/Latest)

The zip contains:
 - The AP World
 - The Mod Itself
 - The PopTracker

take the ```CyberpunkArchipelagoMod_(X_X_X).zip``` and extract to your Cyberpunk 2077 Root folder. This should contain the ```r6```, ```bin```, and ```Red4EXT``` folders.

Next, open the Archipelago Launcher and drag the ```cyberpunk2077.apworld``` file onto the launcher.

You ***MUST*** restart the launcher before it will show up.
# Usage

## Using the Mod
## This assumes that you already have an AP world hosted somewhere
1. Launch the Cyberpunk 2077 Client.
2. Start up Cyberpunk 2077
3. If you havent already, set a keybind for the CET overlay, if you have, skip this step. If need to reset it. Refer to the Cyber Engine Tweaks documentation on how to fix that.
4. From the CET overlay, fill out the fields with your ```Archipelago Server IP/URL```, ```Archipelago Server Port```, and ```Save Slot Name```
5. Profit. Have Fun.

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

## Credits

- **247Tossing** — Cyberpunk 2077 Archipelago Mod
- Built with [Archipelago](https://archipelago.gg/), [RedScript](https://github.com/jac3km4/redscript), and [Cyber Engine Tweaks](https://github.com/maximegmd/CyberEngineTweaks)

Developers: see [CONTRIBUTING.md](CONTRIBUTING.md) for build instructions, issue reporting, and third-party library credits.

---

## What if something is broken?
Open an [Issue](https://github.com/247Tossing/cyberpunk_archipelago/issues/new/choose). See [CONTRIBUTING.md](CONTRIBUTING.md#reporting-issues) for what to include in your report.
