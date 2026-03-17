
# Cyberpunk 2077 Archipelago Mod

A mod and client for Cyberpunk 2077 for Archipelago

## ⚠️ WARNING: Experimental Release
**This current release is NOT recommended for use in large community async environments.**
It is currently prone to **generation issues**. Thar be dragons!
## ⚠️ WARNING: Other Mod Support
I do not support adding other mods on top of this one, nor will i assist if this mod does not work with other mods installed. Only the mods listed in the Requirements are supported.
---

## What does this do?
At the moment, not much.
There are checks for every major story quests and most side quests as well the cyber psychos. There is one blocker in place for "The Ride". More quests will get blockers over time.
***Have Patience***

# Installation

## Requirements

You will need the following mods for this to work:
| Mod          | Link |
| ----------------- | ------------------------------------------------------------------ |
| RedScript 0.5.31 | [Github Link](https://github.com/jac3km4/redscript)|
| Cyber Engine Tweaks | [Github Link](https://github.com/maximegmd/CyberEngineTweaks) |
| RedSocket | [Github Link](https://github.com/rayshader/cp2077-red-socket) |
| Codeware | [Github Link](https://github.com/psiberx/cp2077-codeware) |
| Red4Ext | [Github Link](https://github.com/wopss/RED4ext) |

## Mod Installation
take the ```CyberpunkArchipelagoMod.zip``` and extract to your Cyberpunk 2077 Root folder. This should contain the ```r6``` and ```bin``` folders.

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

## What if something is broken?
Open an [Issue](https://github.com/247Tossing/cyberpunk_archipelago/issues/new/choose)

### What to include in your issue:
1. Your spoiler.txt (if generated locally you can find it in ```{archipelago install dir}\output\(zip used in generation)\spoiler.txt```
2. CET logs (you can find them in ```{game dir}\bin\x64\plugins\cyber_engine_tweaks\scripting.log```
3. Client Logs (you can find them in ```{archipelago install dir}\logs\Cyperpunk2077Client(some stuff).log```
4. Server Logs (if hosting locally they will be in ```{archipelago install dir}\logs\Server(some stuff).log```
5. A good description of what exactly the issue is. I can't help if i don't know what im looking for.
