"""
Build and stage WolvenKit project outputs for release packaging.

This script optionally runs ``wolvenkit.cli import`` then ``wolvenkit.cli pack`` for the project's
``.cpmodproj``, validates the generated ``packed/`` payload, and syncs
WolvenKit-managed files into ``Cyberpunk2077/`` so zip packaging includes:

    - archive/pc/mod/*.archive
    - archive/pc/mod/*.archive.xl
    - r6/tweaks/cyberpunk_archipelago-wolvenkitproj/vendor_checks_*.yaml
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import os
from pathlib import Path
from typing import Iterable

MOD_ROOT = Path(__file__).resolve().parent.parent
PROJECT_DIR = MOD_ROOT / "cyberpunk_archipelago-wolvenkitproj"
PACKED_DIR = PROJECT_DIR / "packed"
OVERLAY_ROOT = MOD_ROOT / "Cyberpunk2077"

# First release with `wolvenkit.cli build` parity.
WOLVENKIT_CLI_MIN_VERSION = "8.17.0"

REQUIRED_PACKED_FILES = (
    PACKED_DIR / "archive" / "pc" / "mod" / "cyberpunk_archipelago-wolvenkitproj.archive",
    PACKED_DIR / "archive" / "pc" / "mod" / "cyberpunk_archipelago-wolvenkitproj.archive.xl",
)
REQUIRED_TWEAK_GLOB = "r6/tweaks/cyberpunk_archipelago-wolvenkitproj/vendor_checks_*.yaml"
REQUIRED_ARCHIVE_DEPOT_PATHS = (
    r"base\gameplay\gui\fullscreen\main_menu\menu_background.xbm",
    r"archipelago\ap-icons.inkatlas",
    r"localization\en-us\ap-strings.json",
)


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    printable = " ".join(str(part) for part in cmd)
    print(f"[wolvenkit] $ {printable}" + (f"  (cwd={cwd})" if cwd else ""))
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)


def run_import(cmd: list[str], *, cwd: Path | None = None) -> None:
    printable = " ".join(str(part) for part in cmd)
    print(f"[wolvenkit] $ {printable}" + (f"  (cwd={cwd})" if cwd else ""))
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")
    if result.returncode == 0:
        return

    output = f"{result.stdout}\n{result.stderr}"
    no_redfile = "No existing redfile found to rebuild for" in output
    imported_summary = "Imported " in output
    hard_error = ": Error" in output or "Unhandled exception" in output
    if imported_summary and not hard_error:
        if no_redfile:
            print(
                "[wolvenkit] warning: import reported unmapped raw files (no matching redfile); "
                "continuing with successfully imported files."
            )
        else:
            print(
                "[wolvenkit] warning: import returned a non-zero code despite reporting imported files; "
                "continuing."
            )
        return

    if no_redfile and not hard_error:
        print(
            "[wolvenkit] warning: import reported unmapped raw files (no matching redfile); "
            "continuing with successfully imported files."
        )
        return

    raise subprocess.CalledProcessError(
        result.returncode,
        cmd,
        output=result.stdout,
        stderr=result.stderr,
    )


def _dotnet_tools_dir() -> Path:
    return Path(os.environ.get("USERPROFILE", "")) / ".dotnet" / "tools"


def _cli_candidates() -> list[str]:
    """Ordered WolvenKit CLI locations; cp77tools is the dotnet global-tool shim name."""
    candidates: list[str] = []
    explicit = os.environ.get("WOLVENKIT_CLI")
    if explicit:
        candidates.append(explicit)

    dotnet_tools = _dotnet_tools_dir()
    for name in ("cp77tools.exe", "cp77tools", "wolvenkit.cli.exe", "wolvenkit.cli"):
        candidates.append(str(dotnet_tools / name))

    for name in ("cp77tools", "wolvenkit.cli"):
        found = shutil.which(name)
        if found:
            candidates.append(found)

    # Preserve order while dropping duplicates.
    seen: set[str] = set()
    unique: list[str] = []
    for item in candidates:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def resolve_cli_command(*, required: bool = False) -> list[str]:
    for candidate in _cli_candidates():
        path = Path(candidate)
        if path.is_file():
            return [str(path)]
        resolved = shutil.which(candidate)
        if resolved and Path(resolved).is_file():
            return [resolved]
    if required:
        raise FileNotFoundError(
            "Could not find WolvenKit CLI command (tried cp77tools, wolvenkit.cli, and "
            f"{_dotnet_tools_dir()}). Install it with "
            f"'dotnet tool install -g wolvenkit.cli' (minimum {WOLVENKIT_CLI_MIN_VERSION}) "
            "then reopen your shell, or set WOLVENKIT_CLI to an explicit executable path."
        )
    return ["cp77tools"]


def run_wolvenkit_build(project_dir: Path, *, require_cli: bool) -> None:
    if project_dir.is_file():
        raise NotADirectoryError(
            f"--project-dir expects a directory containing a .cpmodproj, got file: {project_dir}"
        )
    if not project_dir.is_dir():
        raise FileNotFoundError(f"WolvenKit project directory does not exist: {project_dir}")
    cpmodproj = sorted(project_dir.glob("*.cpmodproj"))
    if not cpmodproj:
        raise FileNotFoundError(f"No .cpmodproj found in {project_dir}")

    cli = resolve_cli_command(required=require_cli)
    raw_dir = project_dir / "source" / "raw"
    archive_dir = project_dir / "source" / "archive"
    resources_dir = project_dir / "source" / "resources"
    if not raw_dir.is_dir():
        raise FileNotFoundError(f"WolvenKit raw source directory does not exist: {raw_dir}")
    if not archive_dir.is_dir():
        raise FileNotFoundError(f"WolvenKit archive source directory does not exist: {archive_dir}")
    if not resources_dir.is_dir():
        raise FileNotFoundError(f"WolvenKit resources directory does not exist: {resources_dir}")
    run_import([*cli, "import", "-p", "source/raw", "-o", "source/archive", "-k"], cwd=project_dir)
    packed_archive_dir = project_dir / "packed" / "archive" / "pc" / "mod"
    packed_archive_dir.mkdir(parents=True, exist_ok=True)
    run([*cli, "pack", "-p", "source/archive", "-o", "packed/archive/pc/mod"], cwd=project_dir)
    generated_archive = packed_archive_dir / "archive.archive"
    target_archive = packed_archive_dir / "cyberpunk_archipelago-wolvenkitproj.archive"
    if generated_archive.is_file():
        if target_archive.is_file():
            target_archive.unlink()
        generated_archive.rename(target_archive)
    if not target_archive.is_file():
        raise FileNotFoundError(f"Expected packed archive not found after pack step: {target_archive}")
    tweaks_src = resources_dir / "r6" / "tweaks"
    if not tweaks_src.is_dir():
        raise FileNotFoundError(f"WolvenKit tweak resources directory does not exist: {tweaks_src}")
    copy_tree(tweaks_src, project_dir / "packed" / "r6" / "tweaks")

    xl_src = resources_dir / "cyberpunk_archipelago-wolvenkitproj.archive.xl"
    xl_dst = packed_archive_dir / "cyberpunk_archipelago-wolvenkitproj.archive.xl"
    if not xl_src.is_file():
        raise FileNotFoundError(f"WolvenKit archive.xl resource is missing: {xl_src}")
    xl_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(xl_src, xl_dst)


def validate_packed_payload(packed_dir: Path) -> None:
    for required in REQUIRED_PACKED_FILES:
        candidate = packed_dir / required.relative_to(PACKED_DIR)
        if not candidate.is_file():
            raise FileNotFoundError(f"Missing required WolvenKit packed artifact: {candidate}")

    tweak_matches = list(packed_dir.glob(REQUIRED_TWEAK_GLOB))
    if not tweak_matches:
        raise FileNotFoundError(
            f"Missing vendor tweak YAMLs in {packed_dir / 'r6/tweaks/cyberpunk_archipelago-wolvenkitproj'}"
        )


def list_archive_entries(cli: list[str], archive_path: Path) -> list[str]:
    cmd = [*cli, "archive", str(archive_path), "--list"]
    printable = " ".join(str(part) for part in cmd)
    print(f"[wolvenkit] $ {printable}")
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            cmd,
            output=result.stdout,
            stderr=result.stderr,
        )
    lines = (line.strip() for line in result.stdout.splitlines())
    return [line.replace("/", "\\") for line in lines if line and not line.startswith("[")]


def validate_archive_internal_paths(packed_dir: Path, *, require_cli: bool) -> None:
    archive_path = packed_dir / "archive" / "pc" / "mod" / "cyberpunk_archipelago-wolvenkitproj.archive"
    if not archive_path.is_file():
        raise FileNotFoundError(f"Expected packed archive not found: {archive_path}")
    cli = resolve_cli_command(required=require_cli)
    entries = list_archive_entries(cli, archive_path)
    lowered = [entry.lower() for entry in entries]

    prefixed = [
        entry
        for entry in entries
        if entry.lower().startswith("source\\archive\\") or entry.lower().startswith(".projectfiles\\")
    ]
    if prefixed:
        sample = ", ".join(prefixed[:3])
        raise ValueError(
            "Packed archive contains invalid internal paths (expected depot paths relative to source/archive): "
            f"{sample}"
        )

    missing = [
        depot_path
        for depot_path in REQUIRED_ARCHIVE_DEPOT_PATHS
        if depot_path.lower() not in lowered
    ]
    if missing:
        raise FileNotFoundError(
            "Packed archive is missing required depot paths: " + ", ".join(missing)
        )


def copy_tree(src: Path, dst: Path) -> int:
    copied = 0
    for item in sorted(src.rglob("*")):
        if item.is_dir():
            continue
        rel = item.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        copied += 1
    return copied


def sync_packed_to_overlay(packed_dir: Path) -> None:
    archive_src = packed_dir / "archive"
    tweaks_src = packed_dir / "r6" / "tweaks"
    if not archive_src.is_dir():
        raise FileNotFoundError(f"Expected packed archive directory not found: {archive_src}")
    if not tweaks_src.is_dir():
        raise FileNotFoundError(f"Expected packed tweaks directory not found: {tweaks_src}")

    archive_dst = OVERLAY_ROOT / "archive"
    tweaks_dst = OVERLAY_ROOT / "r6" / "tweaks"
    archive_count = copy_tree(archive_src, archive_dst)
    tweaks_count = copy_tree(tweaks_src, tweaks_dst)
    print(
        "[wolvenkit] synced packed payload into overlay: "
        f"{archive_count} archive files, {tweaks_count} tweak/resource files"
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build WolvenKit project and sync packed outputs into Cyberpunk2077 overlay."
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=PROJECT_DIR,
        help="Directory that contains the WolvenKit .cpmodproj file.",
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip wolvenkit.cli build and only validate+sync packed artifacts.",
    )
    parser.add_argument(
        "--allow-fallback",
        action="store_true",
        help="If build fails, continue with committed packed artifacts if valid.",
    )
    parser.add_argument(
        "--require-cli",
        action="store_true",
        help="Fail immediately if WolvenKit CLI is not resolvable before build (does not disable --allow-fallback on build errors).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.skip_build:
        print("[wolvenkit] skipping CLI build; using existing packed artifacts.")
    else:
        try:
            run_wolvenkit_build(args.project_dir.resolve(), require_cli=args.require_cli)
        except subprocess.CalledProcessError as exc:
            if not args.allow_fallback:
                raise
            print(
                "[wolvenkit] warning: WolvenKit CLI build failed; using committed "
                f"packed/ artifacts for fallback ({exc})."
            )
        except (FileNotFoundError, NotADirectoryError):
            raise

    packed_dir = args.project_dir.resolve() / "packed"
    validate_packed_payload(packed_dir)
    validate_archive_internal_paths(packed_dir, require_cli=args.require_cli)
    sync_packed_to_overlay(packed_dir)
    print(f"[wolvenkit] done (minimum recommended CLI version: {WOLVENKIT_CLI_MIN_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
