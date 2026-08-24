#!/usr/bin/env python3
from __future__ import annotations

import threading
import tkinter.messagebox as messagebox
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from config import load_config, save_config
from core.chrome_service import ChromeProfileService
from core.models import ProfileRecord
from core.utils import detect_chrome_exe, is_main_browser
from ui.components import btn, card, entry, label, show_centered
from ui.defaults import APP_TITLE
from ui.icon_utils import apply_window_icon
from ui.theme import (
    UI_BG,
    UI_FONT_BOLD,
    UI_FONT_SMALL,
    UI_LINE,
    UI_PRIMARY,
    UI_PRIMARY_LIGHT,
    UI_TEXT_MUTED,
)


class ChromeProfileApp:
    def __init__(self) -> None:
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk(fg_color=UI_BG)
        self.root.title(APP_TITLE)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self._busy = False
        self._status_var = ctk.StringVar(value="就绪")
        self._config = load_config()
        self._records: list[ProfileRecord] = []
        self._chrome_override: Path | None = None

        self._build_ui()
        self._load_fields()
        self._refresh_profile_list()
        apply_window_icon(self.root)
        show_centered(self.root)

    def _build_ui(self) -> None:
        settings = card(self.root)
        settings.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))
        settings.grid_columnconfigure(1, weight=1)

        label(settings, text="默认设置", font=UI_FONT_BOLD).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 6)
        )

        self._chrome_row = self._chrome_path_row(settings, 1)
        self._root_entry = self._path_row(settings, 2, "配置根目录", self._browse_root)
        self._desktop_entry = self._path_row(settings, 3, "启动项目录", self._browse_desktop)

        save_row = ctk.CTkFrame(settings, fg_color=UI_BG)
        save_row.grid(row=4, column=0, columnspan=3, sticky="ew", padx=12, pady=(4, 10))
        btn(save_row, text="保存默认设置", width=120, command=self._save_settings).pack(side="left")
        label(
            save_row,
            text="Chrome 路径每次自动检测；仅保存配置根目录与启动项目录",
            font=UI_FONT_SMALL,
            text_color=UI_TEXT_MUTED,
        ).pack(side="left", padx=(12, 0))

        create = card(self.root)
        create.grid(row=1, column=0, sticky="ew", padx=16, pady=4)
        create.grid_columnconfigure(1, weight=1)

        label(create, text="创建独立浏览器", font=UI_FONT_BOLD).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 6)
        )

        label(create, text="文件夹名称").grid(row=1, column=0, sticky="w", padx=12, pady=4)
        self._profile_name_entry = entry(create, placeholder_text="例如：工作、个人、Chrome-B")
        self._profile_name_entry.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=4)

        label(create, text="启动项名称").grid(row=2, column=0, sticky="w", padx=12, pady=4)
        self._shortcut_name_entry = entry(create, placeholder_text="留空则自动命名（Windows .lnk / macOS .command / Linux .desktop）")
        self._shortcut_name_entry.grid(row=2, column=1, sticky="ew", padx=(0, 8), pady=4)

        action_row = ctk.CTkFrame(create, fg_color=UI_BG)
        action_row.grid(row=3, column=0, columnspan=3, sticky="ew", padx=12, pady=(6, 10))
        self._create_btn = btn(
            action_row,
            text="创建并生成启动项",
            primary=True,
            width=160,
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_create,
        )
        self._create_btn.pack(side="left")
        btn(action_row, text="刷新列表", width=88, command=self._refresh_profile_list).pack(
            side="left", padx=(8, 0)
        )

        list_card = card(self.root)
        list_card.grid(row=2, column=0, sticky="nsew", padx=16, pady=(4, 6))
        list_card.grid_rowconfigure(1, weight=1)
        list_card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(list_card, fg_color=UI_BG)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        label(header, text="已有配置", font=UI_FONT_BOLD).pack(side="left")
        label(
            header,
            text="点击右侧删除按钮可移除配置（含数据目录与启动项）",
            font=UI_FONT_SMALL,
            text_color=UI_TEXT_MUTED,
        ).pack(side="left", padx=(12, 0))

        self._profile_list = ctk.CTkScrollableFrame(
            list_card,
            fg_color=UI_BG,
            border_color="#D6E4F0",
            border_width=1,
            corner_radius=6,
        )
        self._profile_list.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        self._profile_list.grid_columnconfigure(0, weight=1)

        self._empty_label = label(
            self._profile_list,
            text="暂无记录。填写上方信息后点击「创建并生成快捷方式」。",
            font=UI_FONT_SMALL,
            text_color=UI_TEXT_MUTED,
            anchor="w",
            justify="left",
        )

        status = ctk.CTkFrame(self.root, fg_color=UI_PRIMARY_LIGHT, corner_radius=0, height=32)
        status.grid(row=3, column=0, sticky="ew")
        ctk.CTkLabel(
            status,
            textvariable=self._status_var,
            anchor="w",
            text_color=UI_PRIMARY,
            font=UI_FONT_SMALL,
        ).pack(fill="x", padx=12, pady=6)

    def _chrome_path_row(self, parent, row: int):
        label(parent, text="Chrome 程序路径").grid(row=row, column=0, sticky="w", padx=12, pady=4)
        row_frame = ctk.CTkFrame(parent, fg_color=UI_BG)
        row_frame.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(0, 12), pady=4)
        row_frame.grid_columnconfigure(0, weight=1)

        self._chrome_entry = entry(row_frame)
        self._chrome_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self._chrome_entry.configure(state="disabled")

        btn(row_frame, text="重新检测", width=80, command=self._redetect_chrome).grid(row=0, column=1, padx=(0, 6))
        btn(row_frame, text="浏览", width=72, command=self._browse_chrome).grid(row=0, column=2)
        return row_frame

    def _path_row(self, parent, row: int, title: str, browse_cmd):
        label(parent, text=title).grid(row=row, column=0, sticky="w", padx=12, pady=4)
        row_frame = ctk.CTkFrame(parent, fg_color=UI_BG)
        row_frame.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(0, 12), pady=4)
        row_frame.grid_columnconfigure(0, weight=1)
        field = entry(row_frame)
        field.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        btn(row_frame, text="浏览", width=72, command=browse_cmd).grid(row=0, column=1)
        return field

    def _load_fields(self) -> None:
        self._refresh_chrome_path()
        self._set_entry(self._root_entry, self._config.get("profile_root", ""))
        self._set_entry(self._desktop_entry, self._config.get("desktop_dir", ""))

    def _refresh_chrome_path(self) -> None:
        if self._chrome_override and self._chrome_override.is_file():
            self._set_readonly_entry(self._chrome_entry, str(self._chrome_override))
            return
        self._chrome_override = None
        detected = detect_chrome_exe()
        if detected:
            self._set_readonly_entry(self._chrome_entry, str(detected))
        else:
            self._set_readonly_entry(self._chrome_entry, "未检测到 Chrome，请点击浏览手动选择")

    def _redetect_chrome(self) -> None:
        self._chrome_override = None
        self._refresh_chrome_path()
        self._set_status("已重新检测 Chrome 路径")

    def _current_chrome_exe(self) -> Path:
        if self._chrome_override and self._chrome_override.is_file():
            return self._chrome_override
        detected = detect_chrome_exe()
        if detected:
            return detected
        raise FileNotFoundError("未检测到 Chrome 程序，请点击浏览选择 chrome.exe")

    @staticmethod
    def _set_entry(widget: ctk.CTkEntry, value: str) -> None:
        widget.delete(0, "end")
        widget.insert(0, value)

    @staticmethod
    def _set_readonly_entry(widget: ctk.CTkEntry, value: str) -> None:
        widget.configure(state="normal")
        widget.delete(0, "end")
        widget.insert(0, value)
        widget.configure(state="disabled")

    def _service(self) -> ChromeProfileService:
        return ChromeProfileService(
            chrome_exe=self._current_chrome_exe(),
            profile_root=Path(self._root_entry.get().strip()),
            desktop_dir=Path(self._desktop_entry.get().strip()),
        )

    def _save_settings(self) -> None:
        root = self._root_entry.get().strip()
        desktop = self._desktop_entry.get().strip()
        if not root or not desktop:
            messagebox.showerror("错误", "请填写配置根目录和启动项目录。")
            return
        try:
            self._current_chrome_exe()
        except FileNotFoundError as exc:
            messagebox.showerror("错误", str(exc))
            return
        save_config(root, desktop)
        self._set_status("默认设置已保存")

    def _browse_chrome(self) -> None:
        path = filedialog.askopenfilename(
            title="选择 Chrome 程序",
            filetypes=[("Chrome", "chrome.exe"), ("可执行文件", "*.exe")],
        )
        if path:
            self._chrome_override = Path(path)
            self._refresh_chrome_path()
            self._set_status("已手动选择 Chrome 路径（本次运行有效）")

    def _browse_root(self) -> None:
        path = filedialog.askdirectory(title="选择配置根目录")
        if path:
            self._set_entry(self._root_entry, path)

    def _browse_desktop(self) -> None:
        path = filedialog.askdirectory(title="选择启动项保存目录")
        if path:
            self._set_entry(self._desktop_entry, path)

    def _on_create(self) -> None:
        if self._busy:
            return

        profile_name = self._profile_name_entry.get().strip()
        shortcut_name = self._shortcut_name_entry.get().strip() or None
        if not profile_name:
            messagebox.showerror("错误", "请填写文件夹名称。")
            return

        try:
            service = self._service()
        except Exception as exc:
            messagebox.showerror("错误", str(exc))
            return

        self._set_busy(True)
        self._set_status("正在创建...")

        def worker() -> None:
            try:
                record = service.create_profile(profile_name, shortcut_name)
                save_config(
                    self._root_entry.get().strip(),
                    self._desktop_entry.get().strip(),
                )
                self.root.after(0, lambda: self._on_create_success(record))
            except Exception as exc:
                self.root.after(0, lambda: self._on_create_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_create_success(self, record) -> None:
        self._set_busy(False)
        self._profile_name_entry.delete(0, "end")
        self._shortcut_name_entry.delete(0, "end")
        self._refresh_profile_list()
        self._set_status(f"已创建：{record.name}")
        messagebox.showinfo(
            "创建成功",
            f"数据目录：\n{record.profile_dir}\n\n快捷方式：\n{record.shortcut_path}",
        )

    def _on_create_error(self, message: str) -> None:
        self._set_busy(False)
        self._set_status("创建失败")
        messagebox.showerror("创建失败", message)

    def _on_delete(self, record: ProfileRecord) -> None:
        if self._busy:
            return

        if is_main_browser(record):
            messagebox.showwarning("无法删除", "主浏览器不可删除。")
            return

        confirmed = messagebox.askyesno(
            "确认删除",
            f"确定删除「{record.name}」吗？\n\n"
            f"数据目录：\n{record.profile_dir}\n\n"
            f"快捷方式：\n{record.shortcut_path}\n\n"
            "将同时删除数据目录和快捷方式，此操作不可恢复。\n"
            "若该浏览器正在运行，请先关闭后再删除。",
        )
        if not confirmed:
            return

        try:
            service = self._service()
        except Exception as exc:
            messagebox.showerror("错误", str(exc))
            return

        self._set_busy(True)
        self._set_status(f"正在删除：{record.name}...")

        def worker() -> None:
            try:
                service.delete_profile(record)
                self.root.after(0, lambda: self._on_delete_success(record.name))
            except Exception as exc:
                self.root.after(0, lambda: self._on_delete_error(str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_delete_success(self, name: str) -> None:
        self._set_busy(False)
        self._refresh_profile_list()
        self._set_status(f"已删除：{name}")

    def _on_delete_error(self, message: str) -> None:
        self._set_busy(False)
        self._set_status("删除失败")
        messagebox.showerror(
            "删除失败",
            f"{message}\n\n若提示文件被占用，请先关闭对应的 Chrome 浏览器后再试。",
        )

    def _refresh_profile_list(self) -> None:
        for widget in self._profile_list.winfo_children():
            widget.destroy()

        try:
            self._records = self._service().list_profiles()
        except Exception as exc:
            self._records = []
            label(
                self._profile_list,
                text=f"无法读取配置列表：{exc}",
                font=UI_FONT_SMALL,
                text_color=UI_TEXT_MUTED,
                anchor="w",
                justify="left",
            ).grid(row=0, column=0, sticky="ew", padx=8, pady=8)
            return

        if not self._records:
            self._empty_label = label(
                self._profile_list,
                text="暂无记录。填写上方信息后点击「创建并生成快捷方式」。",
                font=UI_FONT_SMALL,
                text_color=UI_TEXT_MUTED,
                anchor="w",
                justify="left",
            )
            self._empty_label.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
            self._set_status("就绪")
            return

        for idx, record in enumerate(self._records):
            if idx > 0:
                sep = ctk.CTkFrame(self._profile_list, height=1, fg_color=UI_LINE, corner_radius=0)
                sep.grid(row=idx * 2 - 1, column=0, sticky="ew", padx=8)

            row_idx = idx * 2
            row = ctk.CTkFrame(self._profile_list, fg_color=UI_BG, border_width=0, height=72)
            row.grid(row=row_idx, column=0, sticky="ew", padx=4, pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.pack_propagate(False)

            title = label(
                row,
                text=f"{idx + 1:02d}. {record.name}",
                font=UI_FONT_BOLD,
                anchor="w",
            )
            title.grid(row=0, column=0, sticky="ew", padx=(8, 8), pady=(8, 0))

            detail = label(
                row,
                text=f"数据：{record.profile_dir}\n快捷方式：{record.shortcut_path}",
                font=UI_FONT_SMALL,
                text_color=UI_TEXT_MUTED,
                anchor="w",
                justify="left",
            )
            detail.grid(row=1, column=0, sticky="ew", padx=(8, 8), pady=(0, 8))

            delete_btn = btn(row, text="删除", width=64, command=lambda r=record: self._on_delete(r))
            delete_btn.grid(row=0, column=1, rowspan=2, padx=(0, 8), pady=8)

        self._set_status(f"共 {len(self._records)} 个配置")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        self._create_btn.configure(state=state)

    def _set_status(self, text: str) -> None:
        self._status_var.set(f"状态：{text}")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ChromeProfileApp().run()
