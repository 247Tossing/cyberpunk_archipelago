"""
Package the end-user mod zip: CyberpunkArchipelagoMod_(version).zip.

The zip contains ONLY what a player extracts into their Cyberpunk 2077 root
folder. The payload lives under ``<mod-root>/Cyberpunk2077/`` and is whitelisted
to ``r6/``, ``bin/`` and ``red4ext/`` so dev-only files (``.redscript``,
``.vscode/``, etc.) never leak into a release.

``red4ext/plugins/CyberpunkAP/CyberpunkAP.dll`` is produced by the native CMake
build; this script fails fast if it is missing so we never ship a zip without
the plugin.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Iterable

MOD_ROOT = Path(__file__).resolve().parent.parent
OVERLAY_ROOT = MOD_ROOT / "Cyberpunk2077"
MANIFEST = MOD_ROOT / "worlds" / "cyberpunk2077" / "archipelago.json"
DEFAULT_OUTPUT_DIR = MOD_ROOT / "build"
DEBUG_LOG_PATH = MOD_ROOT / "debug-37257d.log"
DEBUG_SESSION_ID = "37257d"

# Top-level folders under Cyberpunk2077/ that belong in the game install.
PAYLOAD_DIRS = ("r6", "bin", "red4ext")

# Required artefact from the native build; absence means an incomplete release.
REQUIRED_NATIVE_DLL = OVERLAY_ROOT / "red4ext" / "plugins" / "CyberpunkAP" / "CyberpunkAP.dll"

# Names skipped anywhere in the tree, even if nested inside a payload dir.
EXCLUDED_NAMES = {".redscript", ".vscode", "__pycache__", ".DS_Store"}


def debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": DEBUG_SESSION_ID,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    with DEBUG_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


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
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    if not REQUIRED_NATIVE_DLL.is_file():
        raise FileNotFoundError(
            f"Missing {REQUIRED_NATIVE_DLL}.\n"
            "Build the native plugin first (cmake --build native/build --config "
            "Release) so CyberpunkAP.dll is present before packaging."
        )
    # region agent log
    debug_log(
        run_id,
        "H2",
        "tools/package_cyberpunk_mod_zip.py:build_zip:required_native",
        "Validated required native plugin exists",
        {
            "requiredNativePath": str(REQUIRED_NATIVE_DLL),
            "requiredNativeSize": REQUIRED_NATIVE_DLL.stat().st_size,
            "requiredNativeSha256": hashlib.sha256(REQUIRED_NATIVE_DLL.read_bytes()).hexdigest(),
        },
    )
    # endregion

    files = list(iter_payload_files())
    if not files:
        raise FileNotFoundError(
            f"No payload files found under {OVERLAY_ROOT}; expected {PAYLOAD_DIRS}."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / f"CyberpunkArchipelagoMod_({version}).zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            # Arcnames are relative to Cyberpunk2077/ so the zip extracts
            # directly into the game root (r6/, bin/, red4ext/ at the top).
            arcname = path.relative_to(OVERLAY_ROOT)
            zf.write(path, arcname.as_posix())

    dll_entries: list[dict[str, object]] = []
    for path in files:
        if path.suffix.lower() == ".dll":
            rel = path.relative_to(OVERLAY_ROOT).as_posix()
            dll_entries.append(
                {
                    "path": rel,
                    "size": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    # region agent log
    debug_log(
        run_id,
        "H5",
        "tools/package_cyberpunk_mod_zip.py:build_zip:after_write",
        "Packaged DLL manifest",
        {
            "zipPath": str(zip_path),
            "zipSize": zip_path.stat().st_size if zip_path.is_file() else 0,
            "dllEntries": dll_entries,
        },
    )
    # endregion

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
