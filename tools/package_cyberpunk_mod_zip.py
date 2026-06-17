"""
Package the end-user mod zip: CyberpunkArchipelagoMod_(version).zip.

The zip contains ONLY what a player extracts into their Cyberpunk 2077 root
folder. The payload lives under ``<mod-root>/Cyberpunk2077/`` and is whitelisted
to ``r6/``, ``bin/``, ``red4ext/`` and ``archive/`` so dev-only files (``.redscript``,
``.vscode/``, etc.) never leak into a release.

``red4ext/plugins/CyberpunkAP/CyberpunkAP.dll`` is produced by the native CMake
build; this script fails fast if it is missing so we never ship a zip without
the plugin.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import zipfile
from pathlib import Path
from typing import Iterable

MOD_ROOT = Path(__file__).resolve().parent.parent
OVERLAY_ROOT = MOD_ROOT / "Cyberpunk2077"
MANIFEST = MOD_ROOT / "worlds" / "cyberpunk2077" / "archipelago.json"
DEFAULT_OUTPUT_DIR = MOD_ROOT / "build"

# Top-level folders under Cyberpunk2077/ that belong in the game install.
PAYLOAD_DIRS = ("r6", "bin", "red4ext", "archive")

# Required artefact from the native build; absence means an incomplete release.
REQUIRED_NATIVE_DLL = OVERLAY_ROOT / "red4ext" / "plugins" / "CyberpunkAP" / "CyberpunkAP.dll"
REQUIRED_WOLVENKIT_ARCHIVE = (
    OVERLAY_ROOT / "archive" / "pc" / "mod" / "cyberpunk_archipelago-wolvenkitproj.archive"
)
REQUIRED_WOLVENKIT_VENDOR_YAML = (
    OVERLAY_ROOT
    / "r6"
    / "tweaks"
    / "cyberpunk_archipelago-wolvenkitproj"
    / "vendor_checks_0_common.yaml"
)

# Names skipped anywhere in the tree, even if nested inside a payload dir.
EXCLUDED_NAMES = {".redscript", ".vscode", "__pycache__", ".DS_Store"}


def read_world_version() -> str:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    version = manifest.get("world_version")
    if not version:
        raise ValueError(f"{MANIFEST} does not define a non-empty 'world_version'.")
    return str(version)


def iter_payload_files() -> Iterable[Path]:
    for name in PAYLOAD_DIRS:
        root = OVERLAY_ROOT / name
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_dir():
                continue
            if any(part in EXCLUDED_NAMES for part in path.relative_to(OVERLAY_ROOT).parts):
                continue
            yield path


def build_zip(version: str, output_dir: Path) -> Path:
    if not REQUIRED_NATIVE_DLL.is_file():
        raise FileNotFoundError(
            f"Missing {REQUIRED_NATIVE_DLL}.\n"
            "Build the native plugin first (cmake --build native/build --config "
            "Release) so CyberpunkAP.dll is present before packaging."
        )
    if not REQUIRED_WOLVENKIT_ARCHIVE.is_file():
        raise FileNotFoundError(
            f"Missing {REQUIRED_WOLVENKIT_ARCHIVE}.\n"
            "Run tools/build_wolvenkit_project.py (or tools/build_release.py) so "
            "archive payload files are synced into Cyberpunk2077/archive first."
        )
    if not REQUIRED_WOLVENKIT_VENDOR_YAML.is_file():
        raise FileNotFoundError(
            f"Missing {REQUIRED_WOLVENKIT_VENDOR_YAML}.\n"
            "Run tools/build_wolvenkit_project.py (or tools/build_release.py) so "
            "vendor tweak YAML files are synced into Cyberpunk2077/r6/tweaks first."
        )

    files = list(iter_payload_files())
    if not files:
        raise FileNotFoundError(
            f"No payload files found under {OVERLAY_ROOT}; expected {PAYLOAD_DIRS}."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"CyberpunkArchipelagoMod_({version}).zip"
    staging_path = zip_path.with_name(f"{zip_path.name}.part")
    if staging_path.exists():
        staging_path.unlink()

    with zipfile.ZipFile(staging_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            # Arcnames are relative to Cyberpunk2077/ so the zip extracts
            # directly into the game root (r6/, bin/, red4ext/ at the top).
            arcname = path.relative_to(OVERLAY_ROOT)
            zf.write(path, arcname.as_posix())

    try:
        if zip_path.exists():
            zip_path.unlink()
        os.replace(staging_path, zip_path)
    except PermissionError:
        fallback = zip_path.with_name(f"{zip_path.stem}.new.zip")
        if fallback.exists():
            fallback.unlink()
        os.replace(staging_path, fallback)
        print(
            f"[package] warning: could not overwrite locked {zip_path} "
            f"(close Explorer/7-Zip if open); wrote {fallback}"
        )
        zip_path = fallback

    print(f"[package] wrote {zip_path} ({len(files)} files)")
    return zip_path


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Package CyberpunkArchipelagoMod_(version).zip from Cyberpunk2077/."
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Override the version string (defaults to archipelago.json world_version).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write the zip into (default: <mod-root>/build).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    version = args.version or read_world_version()
    build_zip(version, args.output_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
