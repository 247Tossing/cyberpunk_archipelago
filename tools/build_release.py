"""
End-to-end release build for the Cyberpunk 2077 Archipelago mod.

Runs the full pipeline that produces both release artifacts:

    1. Fetch native submodules (skippable; CI uses ``actions/checkout`` instead).
    2. Build the RED4ext native plugin (CyberpunkAP.dll) with CMake (Release).
    3. Locate the Archipelago checkout and expose worlds/cyberpunk2077 inside it
       via a directory junction (Windows) or symlink (POSIX).
    4. Install Archipelago's runtime requirements non-interactively.
    5. Regenerate the RedScript ID mappings and build cyberpunk2077.apworld
       (delegates to build_cyberpunk2077_apworld.py).
    6. Package CyberpunkArchipelagoMod_(version).zip (delegates to
       package_cyberpunk_mod_zip.py).

Final artifacts land in ``<mod-root>/build/``:
    - cyberpunk2077.apworld
    - CyberpunkArchipelagoMod_(version).zip
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

MOD_ROOT = Path(__file__).resolve().parent.parent
NATIVE_DIR = MOD_ROOT / "native"
NATIVE_BUILD_DIR = NATIVE_DIR / "build"
WORLD_DIR = MOD_ROOT / "worlds" / "cyberpunk2077"
MANIFEST = WORLD_DIR / "archipelago.json"
TOOLS_DIR = MOD_ROOT / "tools"
WORLD_FOLDER_NAME = "cyberpunk2077"


def run(cmd: list[str], *, cwd: Path | None = None, env: dict | None = None) -> None:
    printable = " ".join(str(part) for part in cmd)
    print(f"[release] $ {printable}" + (f"  (cwd={cwd})" if cwd else ""))
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None, env=env)


def read_world_version() -> str:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    version = manifest.get("world_version")
    if not version:
        raise ValueError(f"{MANIFEST} does not define a non-empty 'world_version'.")
    return str(version)


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


def assert_tag_matches_version(tag: str, version: str) -> None:
    normalized = tag.removeprefix("refs/tags/").removeprefix("v")
    if normalized != version:
        raise SystemExit(
            f"Tag '{tag}' (normalized '{normalized}') does not match "
            f"archipelago.json world_version '{version}'. Bump the manifest or "
            "retag before releasing."
        )
    print(f"[release] tag '{tag}' matches world_version '{version}'.")


def fetch_submodules() -> None:
    run(["git", "submodule", "update", "--init", "--recursive"], cwd=MOD_ROOT)


def build_native() -> None:
    run(["cmake", "-S", str(NATIVE_DIR), "-B", str(NATIVE_BUILD_DIR)])
    run(["cmake", "--build", str(NATIVE_BUILD_DIR), "--config", "Release"])


def ensure_world_visible(ap_root: Path) -> None:
    target = ap_root / "worlds" / WORLD_FOLDER_NAME
    if target.exists():
        return
    print(f"[release] linking {target} -> {WORLD_DIR}")
    if os.name == "nt":
        run(["cmd", "/c", "mklink", "/J", str(target), str(WORLD_DIR)])
    else:
        target.symlink_to(WORLD_DIR, target_is_directory=True)


def install_archipelago_requirements(ap_root: Path) -> None:
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=ap_root)
    run([sys.executable, "ModuleUpdate.py", "-y"], cwd=ap_root)


def build_apworld(ap_root: Path) -> None:
    run(
        [
            sys.executable,
            str(TOOLS_DIR / "build_cyberpunk2077_apworld.py"),
            "--archipelago-root",
            str(ap_root),
        ]
    )


def package_zip(version: str) -> None:
    run(
        [
            sys.executable,
            str(TOOLS_DIR / "package_cyberpunk_mod_zip.py"),
            "--version",
            version,
        ]
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the full release: cyberpunk2077.apworld + mod zip."
    )
    parser.add_argument(
        "--archipelago-root",
        type=Path,
        default=None,
        help="Path to the Archipelago source. Defaults to $ARCHIPELAGO_ROOT or ../Archipelago.",
    )
    parser.add_argument(
        "--skip-submodules",
        action="store_true",
        help="Skip 'git submodule update' (use when CI already checked out submodules).",
    )
    parser.add_argument(
        "--skip-native",
        action="store_true",
        help="Skip the CMake native build (use only if CyberpunkAP.dll is already built).",
    )
    parser.add_argument(
        "--skip-requirements",
        action="store_true",
        help="Skip installing Archipelago's Python requirements.",
    )
    parser.add_argument(
        "--require-tag-version",
        default=None,
        help=(
            "A git tag/ref (e.g. 'v0.6-rc1' or 'refs/tags/v0.6-rc1'); fail unless it "
            "matches archipelago.json world_version. Intended for tag-triggered CI."
        ),
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    version = read_world_version()
    if args.require_tag_version:
        assert_tag_matches_version(args.require_tag_version, version)

    if not args.skip_submodules:
        fetch_submodules()

    if not args.skip_native:
        build_native()

    ap_root = find_archipelago_root(args.archipelago_root)
    ensure_world_visible(ap_root)

    if not args.skip_requirements:
        install_archipelago_requirements(ap_root)

    build_apworld(ap_root)
    package_zip(version)

    print(f"[release] done. Artifacts in {MOD_ROOT / 'build'}:")
    print(f"[release]   - cyberpunk2077.apworld")
    print(f"[release]   - CyberpunkArchipelagoMod_({version}).zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
