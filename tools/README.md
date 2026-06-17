# Mod build tooling

## `build_release.py` (full release)

One command produces end-user artifacts in `build/`:

- `cyberpunk2077.apworld`
- `cyberpunk2077_poptracker_(<version>).zip`
- `CyberpunkArchipelagoMod_(<version>).zip`

```cmd
python tools\build_release.py --archipelago-root <ARCHIPELAGO>
```

It runs the whole pipeline in order: fetch native submodules, build the RED4ext
plugin (`CyberpunkAP.dll`) with CMake in `Release`, build/sync the WolvenKit
project payload (`archive/` + `r6/tweaks/`) into `Cyberpunk2077/`, link
`worlds/cyberpunk2077` into the Archipelago checkout, install Archipelago's
Python requirements non-interactively (`ModuleUpdate.py -y`), build the
apworld, generate the PopTracker pack, then package the mod zip.

The mbedTLS source tarball (`native/APCpp/mbedtls-3.6.4.tar.bz2`) is gitignored;
`build_release.py` downloads and verifies it automatically when missing (CI and
fresh clones).

The Archipelago checkout is resolved from `--archipelago-root`, then
`$ARCHIPELAGO_ROOT`, then `../Archipelago`.

Useful flags:

- `--skip-submodules` - CI already checked out submodules (`actions/checkout`).
- `--skip-native` - reuse an already-built `CyberpunkAP.dll`.
- `--skip-wolvenkit` - skip WolvenKit CLI build/sync (uses overlay as-is).
- `--allow-wolvenkit-fallback` - if WolvenKit CLI build fails, fall back to
  committed `cyberpunk_archipelago-wolvenkitproj/packed/` artifacts.
- `--require-wolvenkit-cli` - fail fast if WolvenKit CLI command is missing (build may still fall back when combined with `--allow-wolvenkit-fallback`).
- `--skip-requirements` - Archipelago deps already installed.
- `--skip-poptracker` - skip the generated PopTracker pack.
- `--require-tag-version <tag>` - fail unless the tag (e.g. `v0.7.0`) matches
  `world_version`; used for tag-triggered CI.

On Windows, the script intentionally does **not** hardcode a Visual Studio
generator. It lets CMake choose the installed default toolset (for example,
VS 17/2022 or VS 18/2026). To pin a generator in CI, set environment
variables before running:

- `CMAKE_GENERATOR` (example: `Visual Studio 18 2026`)
- optional `CMAKE_GENERATOR_PLATFORM` (example: `x64`)

Windows release builds pass `-DUSE_OPEN_SSL=OFF -DUSE_MBED_TLS=ON` to native
CMake configure so release artifacts do not depend on external OpenSSL runtime
DLLs.

### WolvenKit in release builds

The release pipeline uses `tools/build_wolvenkit_project.py` to run:

```cmd
wolvenkit.cli build cyberpunk_archipelago-wolvenkitproj
```

The script auto-detects either `wolvenkit.cli` or `cp77tools` (the default
command exposed by `dotnet tool install -g wolvenkit.cli`).

Then it validates `cyberpunk_archipelago-wolvenkitproj/packed/` and syncs:

- `packed/archive/` -> `Cyberpunk2077/archive/`
- `packed/r6/tweaks/` -> `Cyberpunk2077/r6/tweaks/`

so `package_cyberpunk_mod_zip.py` includes ArchiveXL + TweakXL payloads.

Local prerequisites:

- .NET 8 SDK
- `dotnet tool install -g wolvenkit.cli` (8.17.0+ for `build`; CI installs latest)

Notes:

- WolvenKit CLI remains Windows-only in practice for this project workflow.
- Linux/macOS developers should use `--skip-wolvenkit` and rely on committed
  `cyberpunk_archipelago-wolvenkitproj/packed/` artifacts.
- Optional future setup: provide `CP2077_GAME_EXE` to preconfigure CLI game path
  in environments that need full headless WolvenKit builds.

### Versioning (RC then stable)

The single source of truth is `world_version` in
`worlds/cyberpunk2077/archipelago.json`. It feeds the apworld manifest, the
PopTracker pack version, and the mod zip filename, so all three stay one-to-one.

Archipelago parses `world_version` with `Utils.tuplize_version`: it must be
**exactly three dot-separated non-negative integers** (e.g. `0.7.0`). Semver
prerelease strings such as `0.6-rc1` or two-part `0.6` will crash world import.

| Git tag | `world_version` | Mod zip |
|---------|-----------------|---------|
| `v0.7.0` | `0.7.0` | `CyberpunkArchipelagoMod_(0.7.0).zip` |
| `v0.7.1` | `0.7.1` | `CyberpunkArchipelagoMod_(0.7.1).zip` |

Release checklist:

1. Set `world_version` to the upcoming value (e.g. `0.7.0`), commit.
2. Tag `v0.7.0` and run the pipeline (or push the tag if CI is tag-triggered).
3. For the next line: bump `world_version` (e.g. to `0.7.1`), commit, tag `v0.7.1`, release again.

### GitHub Actions

Workflow: [`.github/workflows/release-artifacts.yml`](../.github/workflows/release-artifacts.yml).

- **Manual run:** GitHub → *Actions* → *Release artifacts* → *Run workflow*. Pick the Archipelago fork/ref (defaults: `ArchipelagoMW/Archipelago` @ `main`). Downloads appear under the run as artifact **`cyberpunk-archipelago-release`** (`cyberpunk2077.apworld` + `cyberpunk2077_poptracker_(…).zip` + `CyberpunkArchipelagoMod_(…).zip`).
- **Tag push:** Pushing a tag matching `v*` runs the same build and asserts the tag matches `world_version` in `archipelago.json` (e.g. tag `v0.7.0` requires `world_version` `0.7.0`). Tag builds use Archipelago `ArchipelagoMW/Archipelago` @ `main`; use *Run workflow* to pin another ref.

## `build_poptracker_pack.py`

Generates a basic list-based PopTracker pack from
`worlds/cyberpunk2077/locations.py` and `items.py`, combines it with static
templates from `poptracker/templates/`, and writes
`cyberpunk2077_poptracker_(<version>).zip` into `build/`.

```cmd
python tools\build_poptracker_pack.py --archipelago-root <ARCHIPELAGO>
```

The pack supports PopTracker's Archipelago connection (`"ap"` variant flag). It
tracks received items and checked locations from the AP server. It does not
include Night City map pins, access logic, hint highlighting, or manual location
sending.

Install the zip by placing it in PopTracker's `packs/` folder, then open the
pack, click **AP**, and connect with the Cyberpunk 2077 slot name.

Rebuild this pack any time `locations.py` or `items.py` changes so the generated
PopTracker IDs stay aligned with the apworld and RedScript ID resolver.

## `package_cyberpunk_mod_zip.py`

Packages only the game-install overlay from `Cyberpunk2077/` (whitelisted to
`r6/`, `bin/`, `red4ext/`, `archive/`) into
`CyberpunkArchipelagoMod_(<version>).zip`. The
zip extracts directly into the Cyberpunk 2077 root. It fails fast if
`red4ext/plugins/CyberpunkAP/CyberpunkAP.dll` is missing, or if required
WolvenKit payload files (`archive/pc/mod/*.archive` and vendor tweak YAMLs) are
missing, so run the release pipeline (or the WolvenKit sync script) first.

```cmd
python tools\package_cyberpunk_mod_zip.py
```

The version defaults to `archipelago.json` `world_version`; override with
`--version` for local experiments only.

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
