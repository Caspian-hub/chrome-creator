from __future__ import annotations

import json
import sys
from pathlib import Path

from core.constants import CONFIG_FILE
from core.platform_paths import default_profile_root
from core.utils import default_desktop


def _config_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / CONFIG_FILE
    return Path(__file__).resolve().parent / CONFIG_FILE


def load_config() -> dict[str, str]:
    defaults = {
        "profile_root": str(default_profile_root()),
        "desktop_dir": str(default_desktop()),
    }
    if not _config_path().is_file():
        return defaults

    try:
        data = json.loads(_config_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return defaults

    merged = defaults.copy()
    for key in defaults:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            merged[key] = value.strip()
    return merged


def save_config(profile_root: str, desktop_dir: str) -> None:
    payload = {
        "profile_root": profile_root.strip(),
        "desktop_dir": desktop_dir.strip(),
    }
    _config_path().write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
