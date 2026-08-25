# REQUIREMENTS.md — 新电脑环境依赖清单与下载途径

> 本清单覆盖本仓库 5 个全局 skill（3gpp_skill / files_skill / find_skill / program_skill / update_skill）与 AGENTS.md 工作约定的全部工具依赖。
> 安装方式：**推荐直接运行 `setup\setup-windows.ps1`**（自动检测+安装+配置），本文件是它的依据与手动安装备查表。
> 所有工具均可纯命令行安装，无 GUI 操作；下载途径同时给出官方源与国内镜像（按网络环境选一）。

## 1. 核心依赖总表

| # | 工具 | 用途（被哪个 skill 使用） | 建议版本 | 官方下载途径 | 国内镜像/备选 | 自动安装命令（winget/npm/pip） |
|---|---|---|---|---|---|---|
| 1 | **opencode CLI** | opencode 本体（所有 skill 的运行宿主） | 最新 | `https://opencode.ai/docs/`（npm 包 `opencode-ai`） | npm 镜像：`https://npmmirror.com/mirrors/opencode-ai/` | `npm i -g opencode-ai` |
| 2 | **Node.js LTS + npm** | opencode、mermaid-cli（mmdc）的运行环境 | ≥20 LTS | `https://nodejs.org/zh-cn/download` | 淘宝镜像 `https://npmmirror.com/mirrors/node/`（选 `node-vXX-x64.msi`） | `winget install OpenJS.NodeJS.LTS` |
| 3 | **Python 3.12** | p2t（公式识别）、matplotlib（配图）、PyMuPDF（PDF 处理） | 3.12.x | `https://www.python.org/downloads/` | 华为云镜像 `https://mirrors.huaweicloud.com/python/` | `winget install Python.Python.3.12` |
| 4 | **Google Chrome** | headless 校验（JS console/CDP 点击/SVG 重叠检测）、mmdc 的 puppeteer 渲染引擎 | 最新稳定 | `https://www.google.com/chrome/` | `https://www.google.cn/chrome/`；winget 最稳 | `winget install Google.Chrome` |
| 5 | **Git for Windows** | 拉取本仓库、WSL 内开发 | 最新 | `https://git-scm.com/download/win` | 淘宝镜像 `https://npmmirror.com/mirrors/git-for-windows/` | `winget install Git.Git` |
| 6 | **LibreOffice** | soffice 将 doc/docx 转 PDF（公式核实流程前置） | 24.x | `https://www.libreoffice.org/download/` | 清华镜像 `https://mirrors.tuna.tsinghua.edu.cn/libreoffice/` | `winget install TheDocumentFoundation.LibreOffice` |
| 7 | **WSL2 + Ubuntu 22.04** | program_skill 默认编译运行环境（C/C++/Python/Shell） | 内核 5.15+ | 微软商店 Ubuntu-22.04；或 `wsl --install -d Ubuntu-22.04` | 应用商店打不开时用离线包（见 §4） | `setup\install-wsl.ps1` |
| 8 | **PowerShell 5.1** | 全部 .ps1 脚本宿主 | 系统自带 | Windows 10/11 内置 | — | 无需安装 |

## 2. npm 全局包（Node 装好后）

| 包 | 用途 | 命令 | 说明 |
|---|---|---|---|
| `opencode-ai` | opencode CLI | `npm i -g opencode-ai` | 慢时加 `--registry=https://registry.npmmirror.com` |
| `@mermaid-js/mermaid-cli` | mmdc（Mermaid → SVG） | `npm i -g @mermaid-js/mermaid-cli` | 渲染依赖 Chrome（用 `PUPPETEER_EXECUTABLE_PATH` 指向系统 Chrome） |
| `@opencode-ai/plugin` | skill-banner 插件依赖 | 在 `~/.config/opencode/` 下 `npm i` | package.json 已随包携带 |

## 3. Python 包（pip，清华镜像）

| 包 | 用途 | 命令 |
|---|---|---|
| `pix2text` | p2t 命令：图片文字+公式识别（转 LaTeX） | `pip install pix2text -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `matplotlib` | 结构图/走势图/时间轴 SVG 生成 | 同上换包名 |
| `PyMuPDF` | PDF 页定位/渲染 PNG（公式核实） | 同上换包名 |
| `pillow` | 图片基础处理 | 同上换包名 |

- p2t 首次运行会从 HuggingFace 下载模型（约 1~2 GB），网络慢时设环境变量走镜像：
  `$env:HF_ENDPOINT = "https://hf-mirror.com"`（hf-mirror.com 为国内 HF 镜像）
- 模型缓存默认位置：`%LOCALAPPDATA%\Temp\opencode\p2t-models`（由 skill 约定统一管理；换机可用移动硬盘直接拷贝该目录，免重新下载）

## 4. WSL2 + Ubuntu 22.04 安装途径（install-wsl.ps1 已封装）

1. **启用功能**（需管理员，重启一次）：
   `dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart`
   `dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart`
2. **设置 WSL2 内核**：`wsl --set-default-version 2`（旧系统需 `wsl --update`）
3. **安装发行版（三选一）**：
   - 在线：`wsl --install -d Ubuntu-22.04`（微软商店渠道）
   - 商店打不开：`curl.exe -L -o ubuntu2204.appx https://aka.ms/wslubuntu2204` 后 `Add-AppxPackage .\ubuntu2204.appx`
   - 纯离线：从任意可用电脑下载 `https://aka.ms/wslubuntu2204` 的 appx 拷贝到新机
4. **Ubuntu 内初始化**（脚本自动执行）：`sudo apt update && sudo apt install -y build-essential git python3 curl`
5. 验证：`wsl -l -v` 显示 Ubuntu-22.04 且 VERSION=2

## 5. 数据文件（3GPP 文档库，skill 的"教材"）

| 数据 | 位置约定 | 获取方式 |
|---|---|---|
| 3GPP 原始文档（docx/doc） | 任务目录（如 `NR-f40\`） | `setup\download-specs.ps1`（从 3gpp.org FTP 自动下载 38 系列 Rel-15 清单）；或从旧机直接拷贝 |
| 纯文本索引 `*.txt` | `%LOCALAPPDATA%\Temp\opencode\specs\` | 用 `scripts\extract-docx.ps1` / `extract-doc.ps1` 批量生成（脚本已随包携带） |
| 转换好的 PDF | `%LOCALAPPDATA%\Temp\opencode\ssb-pdf\` | LibreOffice 批量转换（公式核实用） |
| p2t 模型缓存 | `%LOCALAPPDATA%\Temp\opencode\p2t-models\` | 首次 p2t 运行自动下载（HF 镜像加速）；或旧机拷贝 |

## 6. 部署目标路径（setup-windows.ps1 自动完成）

| 源（仓库内） | 部署到（新电脑） | 说明 |
|---|---|---|
| `opencode\skills\*` | `%USERPROFILE%\.config\opencode\skills\*` | 5 个全局 skill |
| `opencode\opencode.jsonc`、`instructions.md`、`evolution.md`、`package.json` | `%USERPROFILE%\.config\opencode\` | 全局配置与规则 |
| `opencode\plugins\*` | `%USERPROFILE%\.config\opencode\plugins\*` | opencode 插件（skill-banner.js） |
| `scripts\*.ps1 / *.py` | `%LOCALAPPDATA%\Temp\opencode\` | skill 引用的辅助脚本（extract/ocr/check/inject 等） |

**路径自动改写**：skill 与脚本中写死的旧机路径（`C:\Users\<旧用户名>\...`、`E:\openCodeDefault\temp`）会在部署时被 setup 脚本自动替换为新电脑的实际用户路径（`%USERPROFILE%` 与 `%TEMP%\opencode`），无需手工修改任何文件。
