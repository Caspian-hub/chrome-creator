from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from core.constants import PROFILE_LOG
from core.models import ProfileRecord
from core.platform_paths import build_shortcut_path, launcher_label
from core.shortcuts import create_launcher
from core.utils import ensure_dir, guess_shortcut_path, is_main_browser, sanitize_name


class ChromeProfileService:
    def __init__(self, chrome_exe: Path, profile_root: Path, desktop_dir: Path) -> None:
        self.chrome_exe = chrome_exe
        self.profile_root = profile_root
        self.desktop_dir = desktop_dir

    def create_profile(
        self,
        profile_name: str,
        shortcut_name: str | None = None,
    ) -> ProfileRecord:
        if not self.chrome_exe.is_file():
            raise FileNotFoundError(f"找不到 Chrome 程序: {self.chrome_exe}")

        name = sanitize_name(profile_name)
        if not name:
            raise ValueError("配置名称不能为空")

        profile_dir = self.profile_root / name
        ensure_dir(self.profile_root)
        ensure_dir(profile_dir)

        shortcut_label = sanitize_name(shortcut_name or launcher_label(name))
        if not shortcut_label:
            shortcut_label = launcher_label(name)

        shortcut_path = build_shortcut_path(self.desktop_dir, shortcut_label)
        create_launcher(shortcut_path, self.chrome_exe, profile_dir, shortcut_label)

        record = ProfileRecord(
            name=name,
            profile_dir=profile_dir,
            shortcut_path=shortcut_path,
            created_at=datetime.now(),
        )
        self._append_log(record)
        return record

    def list_profiles(self) -> list[ProfileRecord]:
        records: list[ProfileRecord] = []
        log_file = self.profile_root / PROFILE_LOG
        if log_file.is_file():
            for line in log_file.read_text(encoding="utf-8").splitlines():
                record = self._parse_log_line(line.strip())
                if record:
                    records.append(record)

        if self.profile_root.is_dir():
            known_dirs = {r.profile_dir.resolve() for r in records}
            for item in sorted(self.profile_root.iterdir()):
                if not item.is_dir() or item.name.startswith("_"):
                    continue
                resolved = item.resolve()
                if resolved in known_dirs:
                    continue
                records.append(
                    ProfileRecord(
                        name=item.name,
                        profile_dir=item,
                        shortcut_path=guess_shortcut_path(self.desktop_dir, item.name),
                    )
                )
        return [record for record in records if not is_main_browser(record)]

    def delete_profile(
        self,
        record: ProfileRecord,
        *,
        delete_data: bool = True,
        delete_shortcut: bool = True,
    ) -> None:
        if is_main_browser(record):
            raise ValueError("主浏览器不可删除")

        if delete_shortcut and record.shortcut_path.is_file():
            record.shortcut_path.unlink()

        if delete_data and record.profile_dir.exists():
            self._validate_profile_dir(record.profile_dir)
            shutil.rmtree(record.profile_dir)

        self._remove_from_log(record)

    def _validate_profile_dir(self, profile_dir: Path) -> None:
        root = self.profile_root.resolve()
        target = profile_dir.resolve()
        if target == root:
            raise ValueError("不能删除配置根目录")
        if root not in target.parents:
            raise ValueError("数据目录不在配置根目录内，拒绝删除")

    def _remove_from_log(self, record: ProfileRecord) -> None:
        log_file = self.profile_root / PROFILE_LOG
        if not log_file.is_file():
            return

        kept: list[str] = []
        target_dir = record.profile_dir.resolve()
        for line in log_file.read_text(encoding="utf-8").splitlines():
            parsed = self._parse_log_line(line.strip())
            if parsed and parsed.profile_dir.resolve() == target_dir:
                continue
            if line.strip():
                kept.append(line)
        log_file.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")

    def _append_log(self, record: ProfileRecord) -> None:
        log_file = self.profile_root / PROFILE_LOG
        ensure_dir(self.profile_root)
        ts = record.created_at.strftime("%Y-%m-%d %H:%M:%S") if record.created_at else "-"
        line = f"[{ts}] {record.name} | {record.profile_dir} | {record.shortcut_path}\n"
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(line)

    @staticmethod
    def _parse_log_line(line: str) -> ProfileRecord | None:
        if not line.startswith("["):
            return None
        try:
            end = line.index("]")
            ts_text = line[1:end]
            rest = line[end + 1 :].strip()
            parts = [part.strip() for part in rest.split("|")]
            if len(parts) < 3:
                return None
            created_at = datetime.strptime(ts_text, "%Y-%m-%d %H:%M:%S")
            return ProfileRecord(
                name=parts[0],
                profile_dir=Path(parts[1]),
                shortcut_path=Path(parts[2]),
                created_at=created_at,
            )
        except (ValueError, IndexError):
            return None
