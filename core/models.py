from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ProfileRecord:
    name: str
    profile_dir: Path
    shortcut_path: Path
    created_at: datetime | None = None

    @property
    def display_line(self) -> str:
        ts = self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else "-"
        return f"{self.name}  |  {self.profile_dir}  |  {ts}"
