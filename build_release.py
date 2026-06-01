from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Final


PROJECT_ROOT: Final = Path(__file__).resolve().parent
GAME_FILE: Final = PROJECT_ROOT / "game-max.py"
DIST_DIR: Final = PROJECT_ROOT / "dist"
BUILD_DIR: Final = PROJECT_ROOT / "build"
ASSETS_DIR: Final = PROJECT_ROOT / "assets"
PYINSTALLER_CACHE_DIR: Final = PROJECT_ROOT / ".pyinstaller-cache"


def _data_separator() -> str:
    return ";" if sys.platform.startswith("win") else ":"


def _pyinstaller_base_args(bundle_name: str, *, mac_bundle: bool = False) -> list[str]:
    args = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        bundle_name,
    ]
    if not mac_bundle:
        args.insert(3, "--onefile")
    else:
        args.insert(3, "--onedir")
    if ASSETS_DIR.exists():
        args.extend(["--add-data", f"{ASSETS_DIR}{_data_separator()}assets"])
    args.append(str(GAME_FILE))
    return args


def _run_pyinstaller(bundle_name: str, *, mac_bundle: bool = False) -> None:
    if shutil.which("pyinstaller") is None:
        raise SystemExit(
            "PyInstaller is not installed. Install it with `pip install pyinstaller` and try again."
        )

    env = os.environ.copy()
    PYINSTALLER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    env["PYINSTALLER_CONFIG_DIR"] = str(PYINSTALLER_CACHE_DIR)

    subprocess.run(
        _pyinstaller_base_args(bundle_name, mac_bundle=mac_bundle),
        check=True,
        cwd=PROJECT_ROOT,
        env=env,
    )


def _bundle_name(target: str) -> str:
    if target == "windows":
        return "NeighborhoodCleanup-Windows"
    if target == "mac":
        return "NeighborhoodCleanup-Mac"
    return "NeighborhoodCleanup"


def _bundle_path(target: str) -> Path:
    if target == "windows":
        return DIST_DIR / f"{_bundle_name(target)}.exe"
    if target == "mac":
        return DIST_DIR / f"{_bundle_name(target)}.app"
    if target == "mac-dmg":
        return DIST_DIR / "NeighborhoodCleanup-Mac.dmg"
    return DIST_DIR / _bundle_name(target)


def _create_dmg(app_path: Path, dmg_path: Path) -> None:
    if shutil.which("hdiutil") is None:
        raise SystemExit("hdiutil is not available. This build must run on macOS.")

    if dmg_path.exists():
        dmg_path.unlink()

    subprocess.run(
        [
            "hdiutil",
            "create",
            "-volname",
            app_path.stem,
            "-srcfolder",
            str(app_path),
            "-ov",
            "-format",
            "UDZO",
            str(dmg_path),
        ],
        check=True,
        cwd=PROJECT_ROOT,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build public release bundles for Neighborhood Cleanup: South Block."
    )
    parser.add_argument(
        "target",
        choices=("windows", "mac", "mac-dmg"),
        help="The release bundle to create.",
    )
    args = parser.parse_args()

    if args.target == "windows" and not sys.platform.startswith("win"):
        raise SystemExit("The Windows bundle can only be built on Windows.")
    if args.target in {"mac", "mac-dmg"} and not sys.platform.startswith("darwin"):
        raise SystemExit("The Mac bundle can only be built on macOS.")

    if args.target == "mac-dmg":
        _run_pyinstaller(_bundle_name("mac"), mac_bundle=True)
        app_path = _bundle_path("mac")
        dmg_path = _bundle_path("mac-dmg")
        if not app_path.exists():
            raise SystemExit(f"Expected build output at {app_path}, but it was not found.")
        _create_dmg(app_path, dmg_path)
        bundle_path = dmg_path
    else:
        _run_pyinstaller(_bundle_name(args.target))
        bundle_path = _bundle_path(args.target)

    if not bundle_path.exists():
        raise SystemExit(f"Expected build output at {bundle_path}, but it was not found.")

    print(f"Created {bundle_path}")


if __name__ == "__main__":
    main()
