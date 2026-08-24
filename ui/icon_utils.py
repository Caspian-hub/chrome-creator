from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def asset_path(name: str) -> Path:
    if getattr(sys, "frozen", False):
        bundled = Path(sys._MEIPASS) / "assets" / name
        if bundled.is_file():
            return bundled
    return project_root() / "assets" / name


def apply_window_icon(root) -> None:
    ico = asset_path("icon.ico")
    png = asset_path("icon.png")

    if sys.platform == "win32" and ico.is_file():
        try:
            root.iconbitmap(str(ico))
            return
        except Exception:
            pass

    if png.is_file():
        try:
            image = tk.PhotoImage(file=str(png))
            root.iconphoto(True, image)
            root._app_icon_ref = image
        except Exception:
            pass
