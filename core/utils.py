from __future__ import annotations

import re
from pathlib import Path

from core.constants import MAIN_BROWSER_NAMES
from core.models import ProfileRecord
from core.platform_paths import (
    build_shortcut_path,
    chrome_candidate_paths,
    default_desktop_dir,
    default_profile_root,
    default_user_data_dir,
    launcher_label,
)


def detect_chrome_exe() -> Path | None:
    for path in chrome_candidate_paths():
        if path.is_file():
            return path
    return None


def sanitize_name(name: str) -> str:
    cleaned = name.strip()
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", cleaned)
    return cleaned


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def default_desktop() -> Path:
    return default_desktop_dir()


def is_main_browser(record: ProfileRecord) -> bool:
    try:
        if record.profile_dir.resolve() == default_user_data_dir().resolve():
            return True
    except OSError:
        pass
    if record.name.strip() in MAIN_BROWSER_NAMES:
        return True
    if "主浏览器" in record.shortcut_path.stem:
        return True
    return False


def guess_shortcut_path(desktop_dir: Path, profile_name: str) -> Path:
    return build_shortcut_path(desktop_dir, launcher_label(profile_name))
