# 发布安装包指南

面向维护者：如何让用户直接从 Releases 下载，而无需自行打包。

## 推荐方式：GitHub Releases + 自动构建

仓库已配置 GitHub Actions（`.github/workflows/release.yml`）。

### 发布新版本

1. 确认代码已合并到 `main`
2. 打标签并推送：

```bash
git tag v1.0.0
git push origin v1.0.0
```

3. GitHub 会自动在 Windows / macOS / Linux 上打包，并创建 Release
4. 用户访问：<https://github.com/Caspian-hub/chrome-creator/releases/latest>

### 手动触发构建（可选）

GitHub 仓库 → **Actions** → **Release** → **Run workflow**

> 仅手动触发时不会自动创建 Release，主要用于测试构建；正式发布请使用标签 `v*`。

## 用户看到的内容

每个 Release 包含三个 zip：

| 文件 | 平台 |
|------|------|
| `ChromeProfileTool-Windows-x64.zip` | Windows 10/11 |
| `ChromeProfileTool-macOS.zip` | macOS |
| `ChromeProfileTool-Linux-x64.zip` | Linux |

## 手动上传 Release（备用）

若暂时不用 Actions，也可本地打包后手动上传：

1. 本地执行 `build.bat` 或 `build.sh`
2. 将 `ChromeProfileTool` 文件夹打成 zip
3. GitHub 仓库 → **Releases** → **Draft a new release**
4. 填写版本号（如 `v1.0.0`），上传 zip 文件
5. 点击 **Publish release**

## 首次发布检查清单

- [ ] 推送 `.github/workflows/release.yml` 到 GitHub
- [ ] 执行 `git tag v1.0.0 && git push origin v1.0.0`
- [ ] 在 Actions 页面确认三个平台构建成功
- [ ] 在 Releases 页面确认安装包可下载
- [ ] README 中的 Releases 链接可正常打开
