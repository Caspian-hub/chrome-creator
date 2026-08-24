#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from core.platform_paths import is_windows, packaged_output_name, pyinstaller_add_data_arg

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR_NAME = packaged_output_name()
OUTPUT_DIR = PROJECT_ROOT / OUTPUT_DIR_NAME


def cleanup_artifacts() -> None:
    build_dir = PROJECT_ROOT / "build"
    if build_dir.is_dir():
        shutil.rmtree(build_dir)
        print("Removed: build/")

    skip_dirs = {OUTPUT_DIR_NAME, "dist", "Chrome配置工具"}
    for cache in PROJECT_ROOT.rglob("__pycache__"):
        if any(part in skip_dirs for part in cache.parts):
            continue
        if cache.is_dir():
            shutil.rmtree(cache)
            print(f"Removed: {cache.relative_to(PROJECT_ROOT)}/")


def main() -> int:
    icon_script = PROJECT_ROOT / "assets" / "generate_icon.py"
    if icon_script.is_file():
        print("Generating application icon...")
        subprocess.run([sys.executable, str(icon_script)], check=True)

    icon_ico = PROJECT_ROOT / "assets" / "icon.ico"
    icon_png = PROJECT_ROOT / "assets" / "icon.png"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "-w",
        "--distpath",
        ".",
        "--workpath",
        "build",
        "--specpath",
        "build",
        "--name",
        OUTPUT_DIR_NAME,
        "--collect-all",
        "customtkinter",
    ]
    if is_windows() and icon_ico.is_file():
        cmd.extend(["--icon", str(icon_ico)])
    if icon_ico.is_file():
        cmd.extend(["--add-data", pyinstaller_add_data_arg(icon_ico)])
    if icon_png.is_file():
        cmd.extend(["--add-data", pyinstaller_add_data_arg(icon_png)])
    cmd.append("main.py")

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    print("\nCleaning up build artifacts...")
    cleanup_artifacts()

    if is_windows():
        print(f"\nBuild complete: {OUTPUT_DIR_NAME}\\{OUTPUT_DIR_NAME}.exe")
    else:
        print(f"\nBuild complete: {OUTPUT_DIR_NAME}/{OUTPUT_DIR_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
