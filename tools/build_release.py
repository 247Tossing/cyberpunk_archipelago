"""
End-to-end release build for the Cyberpunk 2077 Archipelago mod.

Runs the full pipeline that produces release artifacts:

    1. Fetch native submodules (skippable; CI uses ``actions/checkout`` instead).
    2. Build the RED4ext native plugin (CyberpunkAP.dll) with CMake (Release).
    3. Build the WolvenKit project payload and sync it into Cyberpunk2077/
       (with optional fallback to committed packed/ artifacts).
    4. Locate the Archipelago checkout and expose worlds/cyberpunk2077 inside it
       via a directory junction (Windows) or symlink (POSIX).
    5. Install Archipelago's runtime requirements non-interactively.
    6. Regenerate the RedScript ID mappings and build cyberpunk2077.apworld
       (delegates to build_cyberpunk2077_apworld.py).
    7. Generate and package cyberpunk2077_poptracker_(version).zip (delegates to
       build_poptracker_pack.py).
    8. Package CyberpunkArchipelagoMod_(version).zip (delegates to
       package_cyberpunk_mod_zip.py).

Final artifacts land in ``<mod-root>/build/``:
    - cyberpunk2077.apworld
    - cyberpunk2077_poptracker_(version).zip
    - CyberpunkArchipelagoMod_(version).zip
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Iterable

# Matches native/APCpp/CMakeLists.txt (APCPP_MBEDTLS_VER) — archive is gitignored.
_MBEDTLS_VER = "3.6.4"
_MBEDTLS_URL = (
    f"https://github.com/Mbed-TLS/mbedtls/releases/download/"
    f"mbedtls-{_MBEDTLS_VER}/mbedtls-{_MBEDTLS_VER}.tar.bz2"
)
_MBEDTLS_SHA256 = (
    "ec35b18a6c593cf98c3e30db8b98ff93e8940a8c4e690e66b41dfc011d678110"
)

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


def ensure_mbedtls_tarball() -> None:
    """mbedTLS source archive is gitignored; download it for CI / fresh clones."""
    dest = NATIVE_DIR / "APCpp" / f"mbedtls-{_MBEDTLS_VER}.tar.bz2"
    if dest.is_file():
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()
        if digest == _MBEDTLS_SHA256:
            return
        print(f"[release] replacing {dest.name} (sha256 mismatch)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[release] downloading {dest.name}")
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    try:
        req = urllib.request.Request(  # noqa: S310 — fixed HTTPS URL + checksum
            _MBEDTLS_URL,
            headers={"User-Agent": "CyberpunkArchipelago-build-release/1.0"},
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = resp.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != _MBEDTLS_SHA256:
            raise RuntimeError(
                f"mbedTLS archive sha256 mismatch: got {digest}, expected {_MBEDTLS_SHA256}"
            )
        tmp.write_bytes(data)
        tmp.replace(dest)
    finally:
        if tmp.is_file():
            tmp.unlink(missing_ok=True)


def build_native() -> None:
    configure = ["cmake", "-S", str(NATIVE_DIR), "-B", str(NATIVE_BUILD_DIR)]
    if os.name == "nt":
        # Release artifacts must be self-contained for end users.
        # Forcing mbedTLS avoids external OpenSSL runtime DLL dependencies on
        # target machines where OpenSSL may not be installed.
        configure += ["-DUSE_OPEN_SSL=OFF", "-DUSE_MBED_TLS=ON"]
    else:
        # Non-Windows builds may rely on the bundled mbedTLS fallback.
        ensure_mbedtls_tarball()
    # Do not hardcode a VS generator: runners may provide newer toolsets
    # (e.g. Visual Studio 18 2026). Respect CMAKE_GENERATOR if the caller
    # wants to pin one; otherwise let CMake select the available default.
    generator = os.environ.get("CMAKE_GENERATOR")
    if os.name == "nt" and generator:
        configure += ["-G", generator]
        arch = os.environ.get("CMAKE_GENERATOR_PLATFORM")
        if arch:
            configure += ["-A", arch]
    try:
        run(configure)
    except subprocess.CalledProcessError as exc:
        print("[release] CMake configure failed. Dumping CMake logs (if present):")
        cmake_logs = [
            NATIVE_BUILD_DIR / "CMakeFiles" / "CMakeError.log",
            NATIVE_BUILD_DIR / "CMakeFiles" / "CMakeOutput.log",
        ]
        for log in cmake_logs:
            if log.is_file():
                print(f"[release] --- {log} ---")
                try:
                    print(log.read_text(encoding="utf-8", errors="replace"))
                except OSError as log_exc:
                    print(f"[release] could not read {log}: {log_exc}")
        raise exc
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


def build_poptracker(ap_root: Path, version: str) -> None:
    run(
        [
            sys.executable,
            str(TOOLS_DIR / "build_poptracker_pack.py"),
            "--archipelago-root",
            str(ap_root),
            "--version",
            version,
        ]
    )


def build_wolvenkit(*, skip_build: bool, allow_fallback: bool, require_cli: bool) -> None:
    cmd = [sys.executable, str(TOOLS_DIR / "build_wolvenkit_project.py")]
    if skip_build:
        cmd.append("--skip-build")
    if allow_fallback:
        cmd.append("--allow-fallback")
    if require_cli:
        cmd.append("--require-cli")
    run(cmd)


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
        description="Build the full release: cyberpunk2077.apworld + PopTracker pack + mod zip."
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
        "--skip-wolvenkit",
        action="store_true",
        help="Skip WolvenKit CLI build+sync (use existing overlay payload as-is).",
    )
    parser.add_argument(
        "--allow-wolvenkit-fallback",
        action="store_true",
        help="If WolvenKit CLI build fails, fall back to committed packed/ artifacts.",
    )
    parser.add_argument(
        "--require-wolvenkit-cli",
        action="store_true",
        help="Fail immediately if WolvenKit CLI command is not available.",
    )
    parser.add_argument(
        "--skip-requirements",
        action="store_true",
        help="Skip installing Archipelago's Python requirements.",
    )
    parser.add_argument(
        "--skip-poptracker",
        action="store_true",
        help="Skip building the PopTracker pack zip.",
    )
    parser.add_argument(
        "--require-tag-version",
        default=None,
        help=(
            "A git tag/ref (e.g. 'v0.7.0' or 'refs/tags/v0.7.0'); fail unless it "
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

    build_wolvenkit(
        skip_build=args.skip_wolvenkit,
        allow_fallback=args.allow_wolvenkit_fallback,
        require_cli=args.require_wolvenkit_cli,
    )

    ap_root = find_archipelago_root(args.archipelago_root)
    ensure_world_visible(ap_root)

    if not args.skip_requirements:
        install_archipelago_requirements(ap_root)

    build_apworld(ap_root)
    if not args.skip_poptracker:
        build_poptracker(ap_root, version)
    package_zip(version)

    print(f"[release] done. Artifacts in {MOD_ROOT / 'build'}:")
    print(f"[release]   - cyberpunk2077.apworld")
    if not args.skip_poptracker:
        print(f"[release]   - cyberpunk2077_poptracker_({version}).zip")
    print(f"[release]   - CyberpunkArchipelagoMod_({version}).zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
