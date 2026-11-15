# Cyberpunk 2077 Multiworld Setup Guide

## Required game mods

Install these in your Cyberpunk 2077 2.5 folder before the Archipelago mod:

| Mod | Version |
|-----|---------|
| RedScript | 0.5.32 |
| TweakXL | 1.12.0 |
| ArchiveXL | 1.28.0 |
| Cyber Engine Tweaks | 1.38.0 |
| Codeware | 1.21.0 |
| RED4ext | 1.31.0 |
| Phone Extension | 0.9 |

## Install the Archipelago mod

1. Download the `.apworld` and `CyberpunkArchipelagoMod` zip from the latest GitHub release.
2. Extract `CyberpunkArchipelagoMod.zip` into the Cyberpunk 2077 root (the folder that contains `r6`, `bin`, and `red4ext`).
3. Open the Archipelago Launcher and drag `cyberpunk2077.apworld` onto it.
4. Restart the launcher so the world shows up.

## Connect

1. Start Cyberpunk 2077.
2. Open the Cyber Engine Tweaks overlay.
3. Enter the server address (for example `archipelago.gg`), port, slot name, and password if the slot has one.
4. Click **Connect to Archipelago**.

## YAML notes

Vendor Sanity is off by default. Turning a vendor category on adds that many checks:

| Option | Checks |
|--------|--------|
| Include Ripperdocs | 54 |
| Include Weapon Vendors | 42 |
| Include Clothing Vendors | 42 |
| Include Melee Vendors | 18 |
| Include Netrunners | 21 |

Each of those requires Vendor Sanity. Enabling every vendor category adds a large number of checks. Smaller multiworlds should leave some categories off.

Linux and Proton users need `WINEDLLOVERRIDES=version,winmm=n,b` so Cyber Engine Tweaks can load. The project README has the Heroic and Steam steps.
