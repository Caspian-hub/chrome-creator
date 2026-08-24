from __future__ import annotations

import os
import sys
from pathlib import Path


def is_windows() -> bool:
    return sys.platform == "win32"


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def chrome_candidate_paths() -> tuple[Path, ...]:
    home = Path.home()
    if is_windows():
        return (
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            home / "AppData" / "Local" / "Google" / "Chrome" / "Application" / "chrome.exe",
        )
    if is_macos():
        return (
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            home / "Applications" / "Google Chrome.app" / "Contents" / "MacOS" / "Google Chrome",
        )
    return (
        Path("/usr/bin/google-chrome"),
        Path("/usr/bin/google-chrome-stable"),
        Path("/usr/bin/chromium"),
        Path("/usr/bin/chromium-browser"),
        Path("/snap/bin/chromium"),
        Path("/snap/bin/google-chrome"),
    )


def default_profile_root() -> Path:
    if is_windows():
        return Path(r"C:\ChromeProfiles")
    return home_profile_dir("ChromeProfiles")


def default_user_data_dir() -> Path:
    home = Path.home()
    if is_windows():
        return home / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    if is_macos():
        return home / "Library" / "Application Support" / "Google" / "Chrome"
    return home / ".config" / "google-chrome"


def default_desktop_dir() -> Path:
    xdg_desktop = os.environ.get("XDG_DESKTOP_DIR")
    if xdg_desktop:
        return Path(xdg_desktop).expanduser()
    return Path.home() / "Desktop"


def shortcut_suffix() -> str:
    if is_windows():
        return ".lnk"
    if is_macos():
        return ".command"
    return ".desktop"


def launcher_label(name: str) -> str:
    return f"Chrome {name}"


def build_shortcut_path(desktop_dir: Path, label: str) -> Path:
    return desktop_dir / f"{label}{shortcut_suffix()}"


def pyinstaller_add_data_arg(source: Path, dest_folder: str = "assets") -> str:
    separator = ";" if is_windows() else ":"
    return f"{source}{separator}{dest_folder}"


def packaged_output_name() -> str:
    return "ChromeProfileTool"


def home_profile_dir(name: str) -> Path:
    return Path.home() / name
