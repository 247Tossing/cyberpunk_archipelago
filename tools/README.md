# Mod build tooling

## `build_cyberpunk2077_apworld.py`

Single entrypoint for producing a release-ready `cyberpunk2077.apworld` that is
guaranteed to be in sync with the RedScript ID resolver shipped in the mod.

It performs two steps:

1. Runs `worlds/cyberpunk2077/tools/generate_redscript_ap_mappings.py` to emit
   `Cyberpunk2077/r6/scripts/CyberPunkArchipelago/Cyberpunk2077_Archipelago_Client/APArchipelagoIdMappings.reds`
   from the latest `locations.py` / `items.py`.
2. Invokes the upstream Archipelago `Build APWorlds` launcher component to
   package `worlds/cyberpunk2077/` into a `.apworld` zip, then copies the
   result into `build/` at the mod root.

### One-time setup

The Archipelago source must be available next to this repo (the wrapper looks
for `../Archipelago` by default), and the cyberpunk world folder must be
visible inside `Archipelago/worlds/cyberpunk2077`. On Windows use a directory
junction so edits flow in both directions:

```cmd
mklink /J "<ARCHIPELAGO>\worlds\cyberpunk2077" "<MOD>\worlds\cyberpunk2077"
```

On Linux/macOS use a regular symlink:

```bash
ln -s "<MOD>/worlds/cyberpunk2077" "<ARCHIPELAGO>/worlds/cyberpunk2077"
```

Install Archipelago's runtime requirements (`pip install -r requirements.txt`
in the Archipelago checkout) before running the wrapper for the first time.

### Usage

```cmd
python tools\build_cyberpunk2077_apworld.py
```

Useful flags:

- `--archipelago-root <path>` - override Archipelago location.
- `--skip-apworld` - only regenerate the RedScript file.
- `--skip-generator` - only repackage the apworld (CI sanity mode after
  asserting `git diff` is clean).
- `--no-copy` - leave the built apworld in `Archipelago/build/apworlds/`.

### When to run it

Any time `worlds/cyberpunk2077/locations.py` or `items.py` changes (especially
insertion order of `location_table` or `item_table`), so the RedScript wire-id
resolver and the apworld stay aligned.
