"""
Build cyberpunk2077.apworld and refresh the RedScript ID mappings together.

This is the canonical build entrypoint for the mod-repo. It runs in three steps:

    1. Regenerate ``APArchipelagoIdMappings.reds`` from
       ``worlds/cyberpunk2077/locations.py`` and ``items.py``.
    2. Invoke Archipelago's official "Build APWorlds" launcher component to
       package ``worlds/cyberpunk2077/`` into ``cyberpunk2077.apworld``.
    3. Copy the resulting ``.apworld`` into ``<mod-root>/build/`` (or wherever
       ``--output-dir`` points).

The mod-repo expects an Archipelago checkout to sit next to it (``../Archipelago``)
or to be passed via ``--archipelago-root`` / ``$ARCHIPELAGO_ROOT``. The cyberpunk
world folder must already be visible inside ``<archipelago>/worlds/cyberpunk2077``
(via a directory junction, symlink, or copy). The accompanying README in this
folder spells out the one-time setup.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


MOD_ROOT = Path(__file__).resolve().parent.parent
WORLD_DIR = MOD_ROOT / "worlds" / "cyberpunk2077"
GENERATOR = WORLD_DIR / "tools" / "generate_redscript_ap_mappings.py"
DEFAULT_REDS_OUTPUT = (
    MOD_ROOT
    / "Cyberpunk2077"
    / "r6"
    / "scripts"
    / "CyberPunkArchipelago"
    / "Cyberpunk2077_Archipelago_Client"
    / "APArchipelagoIdMappings.reds"
)
DEFAULT_OUTPUT_DIR = MOD_ROOT / "build"
GAME_NAME = "Cyberpunk 2077"
WORLD_FOLDER_NAME = "cyberpunk2077"


def find_archipelago_root(explicit: Path | None) -> Path:
    if explicit:
        resolved = explicit.resolve()
        if not (resolved / "Launcher.py").is_file():
            raise FileNotFoundError(
                f"--archipelago-root {resolved} is not an Archipelago source checkout."
            )
        return resolved
    env_value = os.environ.get("ARCHIPELAGO_ROOT")
    if env_value:
        return find_archipelago_root(Path(env_value))
    sibling = MOD_ROOT.parent / "Archipelago"
    if (sibling / "Launcher.py").is_file():
        return sibling.resolve()
    raise FileNotFoundError(
        "Cannot locate Archipelago source.\n"
        "Pass --archipelago-root, set ARCHIPELAGO_ROOT, or place an Archipelago "
        "checkout at ../Archipelago relative to this mod-repo."
    )


def ensure_world_visible(ap_root: Path) -> None:
    target = ap_root / "worlds" / WORLD_FOLDER_NAME
    if target.is_dir():
        return
    raise FileNotFoundError(
        f"{target} is missing.\n"
        f"Create a directory junction (Windows) with:\n"
        f'  cmd /c mklink /J "{target}" "{WORLD_DIR}"\n'
        f"or a symlink on Linux/macOS:\n"
        f'  ln -s "{WORLD_DIR}" "{target}"'
    )


def run_generator(ap_root: Path, reds_output: Path) -> None:
    env = os.environ.copy()
    env["CYBERPUNK_MOD_ROOT"] = str(MOD_ROOT)
    env["ARCHIPELAGO_ROOT"] = str(ap_root)
    # Importing the worlds package triggers other worlds' module loaders, some
    # of which call ModuleUpdate.update() interactively. Block those prompts -
    # missing requirements for other worlds are surfaced as logged import
    # failures, which is fine since we only need cyberpunk2077 to import.
    env["SKIP_REQUIREMENTS_UPDATE"] = "1"
    cmd = [
        sys.executable,
        "-m",
        "worlds.cyberpunk2077.tools.generate_redscript_ap_mappings",
        "--output",
        str(reds_output),
    ]
    print(f"[build] regenerating {reds_output.name}")
    subprocess.check_call(cmd, env=env, cwd=ap_root)


def run_apworld_build(ap_root: Path) -> Path:
    print(f'[build] running Archipelago "Build APWorlds" -> {GAME_NAME}')
    env = os.environ.copy()
    # Avoid interactive prompts when pkg_resources / requirements drift. The
    # mod-repo README points users at `python ModuleUpdate.py -y` for the
    # one-time install instead.
    env["SKIP_REQUIREMENTS_UPDATE"] = "1"
    subprocess.check_call(
        [
            sys.executable,
            "Launcher.py",
            "Build APWorlds",
            "--",
            "--skip_open_folder",
            GAME_NAME,
        ],
        cwd=ap_root,
        env=env,
    )
    built = ap_root / "build" / "apworlds" / f"{WORLD_FOLDER_NAME}.apworld"
    if not built.is_file():
        raise FileNotFoundError(
            f"Expected {built} after Build APWorlds; check Archipelago output."
        )
    return built


def copy_apworld(built: Path, output_dir: Path | None) -> Path:
    if output_dir is None:
        return built
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / built.name
    shutil.copy2(built, dest)
    print(f"[build] copied {built} -> {dest}")
    return dest


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate APArchipelagoIdMappings.reds and build cyberpunk2077.apworld."
        )
    )
    parser.add_argument(
        "--archipelago-root",
        type=Path,
        default=None,
        help="Path to the Archipelago source. Defaults to ../Archipelago or $ARCHIPELAGO_ROOT.",
    )
    parser.add_argument(
        "--reds-output",
        type=Path,
        default=DEFAULT_REDS_OUTPUT,
        help="Where to write the generated APArchipelagoIdMappings.reds.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Copy the built .apworld into this folder (use --no-copy to skip).",
    )
    parser.add_argument(
        "--no-copy",
        action="store_true",
        help="Leave the built .apworld in Archipelago/build/apworlds and do not copy.",
    )
    parser.add_argument(
        "--skip-generator",
        action="store_true",
        help="Skip the RedScript mapping regeneration step (CI assertion mode).",
    )
    parser.add_argument(
        "--skip-apworld",
        action="store_true",
        help="Skip the Build APWorlds step (useful when only refreshing .reds).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    ap_root = find_archipelago_root(args.archipelago_root)
    ensure_world_visible(ap_root)

    if not args.skip_generator:
        run_generator(ap_root, args.reds_output.resolve())

    if args.skip_apworld:
        return 0

    built = run_apworld_build(ap_root)
    copy_apworld(built, None if args.no_copy else args.output_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
