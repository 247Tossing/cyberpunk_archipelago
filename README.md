# Cyberpunk 2077 Archipelago Mod

An [Archipelago](https://archipelago.gg/) mod for Cyberpunk 2077

> [!WARNING]
> ⚠️ **Experimental Release**
> 
> While most generation issues have been resolved, there is a possibility that certain quirks exist in the new features being added.

## What does this mod do?

First, familiarize yourself with Archipelago by reading [The Archipelago FAQ](https://archipelago.gg/faq/en/).

**Checks (Locations)** include story and DLC quest beats, gigs, tarot paintings, cyberpsycho sightings, NCPD hustles, minor quests, and optional **vendor sanity** purchases at ripperdocs and weapon vendors.

**Items** include progression and utility gear, filler rewards, optional **trap** items, **eddies**, and **quickhacks as items**. Optional **district access tokens** can require you to unlock specific regions in Night City.

**Weapon Restrictions** let you hard-block selected weapon classes or require matching **weapon pass** items from the multiworld before you can use those weapon types.

**Extras** include:
- **Death Link** — share deaths with the multiworld when enabled
- **Oops! All Traps!** — replaces useful and filler items with traps

---

## Installation

### Requirements

You'll need these mods for the archipelago mod to work:

| Mod | Version | GitHub | Nexus |
|-----|---------|--------|-------|
| RedScript | 0.5.31+ | [Link](https://github.com/jac3km4/redscript) | [Link](https://www.nexusmods.com/cyberpunk2077/mods/1511) |
| TweakXL | — | [Link](https://github.com/psiberx/cp2077-tweak-xl) | [Link](https://www.nexusmods.com/cyberpunk2077/mods/4197) |
| ArchiveXL | — | [Link](https://github.com/psiberx/cp2077-archive-xl) | [Link](https://www.nexusmods.com/cyberpunk2077/mods/4198) |
| Cyber Engine Tweaks | — | [Link](https://github.com/maximegmd/CyberEngineTweaks) | [Link](https://www.nexusmods.com/cyberpunk2077/mods/107) |
| Codeware | — | [Link](https://github.com/psiberx/cp2077-codeware) | [Link](https://www.nexusmods.com/cyberpunk2077/mods/7780) |
| Red4Ext | — | [Link](https://github.com/wopss/RED4ext) | [Link](https://www.nexusmods.com/cyberpunk2077/mods/2380) |
| Phone Extension | — | N/A | [Link](https://www.nexusmods.com/cyberpunk2077/mods/24949) |

### Optional Recommended Mods

These mods are **not** required but have been tested for compatibility and enhance the experience:

| Mod | Links | Notes |
|-----|-------|-------|
| New Game Plus - Native | [GitHub](https://github.com/alphanin9/CyberpunkNewGamePlus) · [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/15043) | When installed, this AP mod can auto-release skip flags |
| Randomizer2077 | [Nexus](https://www.nexusmods.com/cyberpunk2077/mods/19884) | **If you use Vendor Sanity**, you **MUST** disable Randomize Vendors in mod options or this **WILL** cause softlocks |

### Mod Installation Steps

1. Download the latest release from [Releases](https://github.com/247Tossing/cyberpunk_archipelago/releases/tag/Latest)
2. Extract `CyberpunkArchipelagoMod.zip` to your Cyberpunk 2077 root folder (should contain `r6`, `bin`, and `Red4EXT` folders)
3. Open the Archipelago Launcher and drag the `cyberpunk2077.apworld` file onto it
4. **You MUST restart the launcher** before it will show up

---

## Usage

### Using the Mod

1. Start Cyberpunk 2077
2. Set a keybind for the CET overlay (if you haven't already). Refer to [Cyber Engine Tweaks documentation](https://github.com/maximegmd/CyberEngineTweaks) if needed
3. From the CET overlay, enter your:
   - Archipelago IP/URL
   - Port
   - Slot Name
   
   Then click **Connect to Archipelago**
4. Enjoy!

### Setting up your YAML

There are many options available because of the mod's extensive content. Depending on your group size, you may want to tune these differently.

Below is a list of options that add location checks and their counts:

| Option | Number of Checks |
|--------|------------------|
| Completion Goal — Complete Any Ending W/ All Side Quests | 45 (base) / 46 (with Phantom Liberty DLC) |
| Completion Goal — Complete Only Phantom Liberty Questline | 17 |
| Include Phantom Liberty DLC | Up to 57 |
| Include Gigs | 81 |
| Include Tarot | 26 |
| Include Cyber Psycho Sighting | 18 |
| Include NCPD Hustles | 37 |
| Include Minor Quests | 62 |
| Include Ripperdocs | 54 (requires Vendor Sanity) |
| Include Weapon Vendors | 42 (requires Vendor Sanity) |
| Include Clothing Vendors | 42 (requires Vendor Sanity) |
| Include Melee Vendors | 21 (requires Vendor Sanity) |
| Include Netrunners | 21 (requires Vendor Sanity) |

### Linux Users

Before anything else, follow this guide: [Cyber Engine Tweaks Linux Instructions](https://wiki.redmodding.org/cyber-engine-tweaks/getting-started/installing/linux-proton)

#### For Heroic:
1. Open the game settings
2. Go to **Advanced**
3. Scroll down to **Environment Variables**
4. Set `Variable Name` to `WINEDLLOVERRIDES`
5. Set `Value` to `"version,winmm=n,b"`

#### For Steam:
1. Right-click the game in Steam
2. Select **Properties**
3. Under **Launch Options**, add: `WINEDLLOVERRIDES="version,winmm=n,b" %command%`

---

## Troubleshooting

### Something's broken?

[Open an issue](https://github.com/247Tossing/cyberpunk_archipelago/issues/new/choose) and include:

1. **spoiler.txt** — found in `{archipelago install dir}\output\(zip used in generation)\spoiler.txt`
2. **CET logs** — found in `{game dir}\bin\x64\plugins\cyber_engine_tweaks\scripting.log`
3. **Client Logs** — found in `{archipelago install dir}\logs\Cyperpunk2077Client*.log`
4. **Server Logs** — if hosting locally, found in `{archipelago install dir}\logs\Server*.log`
5. **Clear description** of the issue — I can't help if I don't know what to look for

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
- [Archipelago](https://archipelago.gg/) — Multiworld randomizer framework
- [RedScript](https://github.com/jac3km4/redscript) — Cyberpunk 2077 scripting framework
- [Cyber Engine Tweaks](https://github.com/maximegmd/CyberEngineTweaks) — Cyberpunk 2077 mod engine
