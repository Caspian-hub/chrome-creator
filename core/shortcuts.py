from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

from core.platform_paths import is_macos, is_windows


def create_launcher(
    shortcut_path: Path,
    chrome_exe: Path,
    profile_dir: Path,
    description: str,
) -> None:
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)
    if is_windows():
        _create_windows_shortcut(shortcut_path, chrome_exe, profile_dir, description)
    elif is_macos():
        _create_macos_launcher(shortcut_path, chrome_exe, profile_dir, description)
    else:
        _create_linux_desktop_entry(shortcut_path, chrome_exe, profile_dir, description)


def _create_windows_shortcut(
    shortcut_path: Path,
    chrome_exe: Path,
    profile_dir: Path,
    description: str,
) -> None:
    exe = _ps_quote(str(chrome_exe))
    work_dir = _ps_quote(str(chrome_exe.parent))
    profile = _ps_quote(str(profile_dir))
    link = _ps_quote(str(shortcut_path))
    desc = _ps_quote(description)

    ps_script = (
        f"$ws=New-Object -ComObject WScript.Shell;"
        f"$s=$ws.CreateShortcut('{link}');"
        f"$s.TargetPath='{exe}';"
        f"$s.Arguments='--user-data-dir=\"{profile}\"';"
        f"$s.WorkingDirectory='{work_dir}';"
        f"$s.Description='Chrome Profile: {desc}';"
        f"$s.IconLocation='{exe},0';"
        f"$s.Save()"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not shortcut_path.is_file():
        detail = (result.stderr or result.stdout or "未知错误").strip()
        raise RuntimeError(f"创建快捷方式失败: {detail}")


def _create_macos_launcher(
    shortcut_path: Path,
    chrome_exe: Path,
    profile_dir: Path,
    description: str,
) -> None:
    content = "\n".join(
        [
            "#!/bin/bash",
            f"# {description}",
            f"exec {_shell_quote(str(chrome_exe))} --user-data-dir={_shell_quote(str(profile_dir))} \"$@\"",
            "",
        ]
    )
    shortcut_path.write_text(content, encoding="utf-8")
    mode = shortcut_path.stat().st_mode
    shortcut_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if not shortcut_path.is_file():
        raise RuntimeError("创建启动脚本失败")


def _create_linux_desktop_entry(
    shortcut_path: Path,
    chrome_exe: Path,
    profile_dir: Path,
    description: str,
) -> None:
    exec_line = f"{_shell_quote(str(chrome_exe))} --user-data-dir={_shell_quote(str(profile_dir))} %U"
    content = "\n".join(
        [
            "[Desktop Entry]",
            "Version=1.0",
            "Type=Application",
            f"Name={description}",
            f"Comment=Chrome Profile: {description}",
            f"Exec={exec_line}",
            "Terminal=false",
            "Categories=Network;WebBrowser;",
            "",
        ]
    )
    shortcut_path.write_text(content, encoding="utf-8")
    mode = shortcut_path.stat().st_mode
    shortcut_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if not os.access(shortcut_path, os.X_OK):
        raise RuntimeError("创建桌面启动项失败")


def _ps_quote(value: str) -> str:
    return value.replace("'", "''")


def _shell_quote(value: str) -> str:
    if not value:
        return "''"
    if all(ch not in value for ch in " \t\"'$\\"):
        return value
    return "'" + value.replace("'", "'\"'\"'") + "'"
