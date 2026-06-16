"""
Build the Cyberpunk 2077 PopTracker pack zip.

The pack is generated from worlds/cyberpunk2077/locations.py and items.py, then
combined with the static files under poptracker/templates/.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable


MOD_ROOT = Path(__file__).resolve().parent.parent
WORLD_DIR = MOD_ROOT / "worlds" / "cyberpunk2077"
MANIFEST = WORLD_DIR / "archipelago.json"
TEMPLATE_DIR = MOD_ROOT / "poptracker" / "templates"
DEFAULT_OUTPUT_DIR = MOD_ROOT / "build"
WORLD_FOLDER_NAME = "cyberpunk2077"


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


def run_generator(ap_root: Path, staging_dir: Path, version: str) -> None:
    if not TEMPLATE_DIR.is_dir():
        raise FileNotFoundError(f"Missing PopTracker template directory: {TEMPLATE_DIR}")

    env = os.environ.copy()
    env["CYBERPUNK_MOD_ROOT"] = str(MOD_ROOT)
    env["ARCHIPELAGO_ROOT"] = str(ap_root)
    env["SKIP_REQUIREMENTS_UPDATE"] = "1"
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "worlds.cyberpunk2077.tools.generate_poptracker_pack",
            "--output-dir",
            str(staging_dir),
            "--template-dir",
            str(TEMPLATE_DIR),
            "--archipelago-root",
            str(ap_root),
            "--version",
            version,
        ],
        cwd=ap_root,
        env=env,
    )


def write_zip(staging_dir: Path, output_dir: Path, version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / f"cyberpunk2077_poptracker_({version}).zip"
    if dest.exists():
        dest.unlink()

    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(staging_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(staging_dir).as_posix())

    print(f"[poptracker] wrote {dest}")
    return dest


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the generated Cyberpunk 2077 PopTracker pack zip."
    )
    parser.add_argument(
        "--archipelago-root",
        type=Path,
        default=None,
        help="Path to the Archipelago source. Defaults to ../Archipelago or $ARCHIPELAGO_ROOT.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Where to write the PopTracker pack zip.",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Version for the output filename. Defaults to archipelago.json world_version.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    version = args.version or read_world_version()
    ap_root = find_archipelago_root(args.archipelago_root)
    ensure_world_visible(ap_root)

    with tempfile.TemporaryDirectory(prefix="cyberpunk-poptracker-") as tmp:
        staging_dir = Path(tmp) / "pack"
        run_generator(ap_root, staging_dir, version)
        write_zip(staging_dir, args.output_dir.resolve(), version)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
