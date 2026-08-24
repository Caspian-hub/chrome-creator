# Chrome Profile Creator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#环境要求)

一款跨平台桌面工具，用于创建**相互独立**的 Google Chrome 浏览器配置。每个配置拥有独立的数据目录、书签、扩展和登录状态，可与主 Chrome 同时运行，互不影响。

![应用图标](assets\界面样式.png)

## 功能特性

- **跨平台支持**：Windows、macOS、Linux
- **自动检测 Chrome 路径**：启动时自动查找本机 Chrome / Chromium 安装位置
- **一键创建独立浏览器**：自动创建数据目录并生成平台对应的启动项
- **配置管理**：查看、刷新、删除已有独立浏览器配置
- **主浏览器保护**：系统默认 Chrome 数据目录不会出现在列表中，且不可误删
- **图形界面**：基于 CustomTkinter 的浅色卡片风格 UI

## 各平台启动项格式

| 平台 | 启动项格式 | 默认配置目录 |
|------|-----------|-------------|
| Windows | `.lnk` 快捷方式 | `C:\ChromeProfiles` |
| macOS | `.command` 脚本 | `~/ChromeProfiles` |
| Linux | `.desktop` 文件 | `~/ChromeProfiles` |

## 工作原理

本工具通过 Chrome 的 `--user-data-dir` 参数为每个配置指定独立的数据目录。例如：

```text
google-chrome --user-data-dir="$HOME/ChromeProfiles/work"
```

不同 `--user-data-dir` 之间的 Cookie、扩展、历史记录、登录状态完全隔离。

## 环境要求

- Python 3.11+（源码运行时需要）
- 已安装 Google Chrome 或 Chromium

| 平台 | 支持版本 |
|------|---------|
| Windows | 10 / 11 |
| macOS | 11+ |
| Linux | 主流桌面发行版（需 X11/Wayland 桌面环境） |

## 快速开始

### 下载安装包（推荐）

不需要安装 Python，直接下载对应系统的压缩包：

👉 **[GitHub Releases 下载页面](https://github.com/Caspian-hub/chrome-creator/releases/latest)**

| 平台 | 下载文件 | 使用方法 |
|------|---------|----------|
| Windows | `ChromeProfileTool-Windows-x64.zip` | 解压后运行 `ChromeProfileTool.exe` |
| macOS | `ChromeProfileTool-macOS.zip` | 解压后运行 `ChromeProfileTool`（首次可能需在「隐私与安全性」中允许） |
| Linux | `ChromeProfileTool-Linux-x64.zip` | 解压后运行 `./ChromeProfileTool` |

> 本工具仅用于创建 Chrome 独立配置，仍需本机已安装 Google Chrome 或 Chromium。

### 从源码运行（开发者）

```bash
git clone https://github.com/Caspian-hub/chrome-creator.git
cd chrome-creator

# 推荐使用 uv（项目已包含 uv.lock）
uv sync
uv run python main.py

# 或使用 pip
pip install -e .
python main.py
```

首次运行会在项目根目录自动生成 `config.json`（用户本地配置，不会提交到 Git）。可参考 `config.json.example`。

<details>
<summary><strong>自行打包（仅开发者）</strong></summary>

| 平台 | 命令 |
|------|------|
| Windows | 双击 `build.bat` |
| macOS / Linux | `chmod +x build.sh && ./build.sh` |

打包完成后，输出在项目根目录的 `ChromeProfileTool/` 文件夹中。

发布流程详见 [docs/RELEASE.md](docs/RELEASE.md)。

</details>

## 使用说明

### 默认设置

| 设置项 | 说明 |
|--------|------|
| Chrome 程序路径 | 自动检测，只读显示；可点击「重新检测」或「浏览」临时指定 |
| 配置根目录 | 所有独立浏览器数据文件夹的父目录 |
| 启动项目录 | 生成的启动项保存位置，默认为桌面 |

点击 **保存默认设置** 后，会持久化「配置根目录」和「启动项目录」（保存在 `config.json`）。

### 创建独立浏览器

1. 填写 **文件夹名称**（如 `work`、`personal`）
2. 可选填写 **启动项名称**（留空则自动命名为 `Chrome [文件夹名]`）
3. 点击 **创建并生成启动项**

### 删除配置

在 **已有配置** 列表中点击 **删除**，将同时移除数据目录、启动项和本地记录。

> 若 Chrome 正在使用该配置，请先关闭对应浏览器窗口后再删除。

## 项目结构

```text
chrome-creator/
├── main.py              # 入口
├── app.py               # GUI 主界面
├── config.py            # 配置读写
├── build.py             # PyInstaller 打包脚本
├── build.sh / build.bat # 打包快捷命令
├── pyproject.toml       # 项目依赖（Python 3.11+）
├── config.json.example  # 配置示例（运行时生成 config.json）
├── LICENSE
├── assets/              # 图标等资源
├── core/
│   ├── chrome_service.py   # 配置创建 / 列表 / 删除
│   ├── platform_paths.py   # 跨平台路径检测
│   ├── shortcuts.py        # 跨平台启动项创建
│   ├── constants.py
│   ├── models.py
│   └── utils.py
├── ui/
│   ├── components.py       # 通用 UI 组件
│   ├── theme.py            # 主题配色
│   ├── defaults.py
│   └── icon_utils.py
└── docs/
    └── RELEASE.md          # 发布指南
```

## 各平台 Chrome 检测路径

**Windows**
- `C:\Program Files\Google\Chrome\Application\chrome.exe`
- `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
- `%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe`

**macOS**
- `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- `~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

**Linux**
- `/usr/bin/google-chrome`
- `/usr/bin/google-chrome-stable`
- `/usr/bin/chromium`
- `/usr/bin/chromium-browser`
- `/snap/bin/chromium`
- `/snap/bin/google-chrome`

若未自动检测到，可点击 **浏览** 手动选择。

## 常见问题

<details>
<summary><strong>Linux 下 .desktop 文件无法启动？</strong></summary>

部分桌面环境需要将 `.desktop` 文件标记为可信任。可在文件管理器中右键该文件，选择「允许启动」或「Trust and Launch」。本工具已自动赋予可执行权限。

</details>

<details>
<summary><strong>macOS 提示无法打开 .command 文件？</strong></summary>

首次运行可能需要在「系统设置 → 隐私与安全性」中允许，或在终端中执行：

```bash
chmod +x ~/Desktop/Chrome\ work.command
xattr -d com.apple.quarantine ~/Desktop/Chrome\ work.command
```

</details>

<details>
<summary><strong>主浏览器会出现在列表里吗？</strong></summary>

不会。使用 Chrome 默认数据目录的主浏览器不会显示在配置列表中，也无法通过本工具删除。

</details>

## 开源协议

本项目采用 [MIT License](LICENSE) 开源。

## 免责声明

- 本工具仅通过 Google Chrome 官方支持的 `--user-data-dir` 参数管理浏览器配置
- 本工具与 Google LLC 无关联，Chrome 是 Google LLC 的商标
- 删除配置操作不可恢复，请谨慎操作
- 软件按「原样」提供，作者不对因使用本软件造成的任何数据丢失或其他损害承担责任

## 贡献

欢迎提交 Issue 和 Pull Request。

---

如果这个项目对你有帮助，欢迎 Star ⭐
