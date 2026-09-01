# 工具权威源：`opencode\tools-manifest.md`（分类 A~G + 本机配置 + 待补充），本文件为历史详细清单，冲突以 tools-manifest.md 为准。

# REQUIREMENTS.md — 新电脑环境依赖清单与下载途径

> 本清单覆盖本仓库 6 个全局 skill（3gpp_skill / files_skill / find_skill / program_skill / update_skill / evolution_skill）与 AGENTS.md 工作约定的全部工具依赖。
> 安装方式：**推荐直接运行 `setup\setup-windows.ps1`**（自动检测+安装+配置；下表各项均已纳入脚本，含 winget 失败自动换镜像直链、动态版本解析与安装后 PATH/环境变量自动配置），本文件是它的依据与手动安装备查表。
> 所有工具均可纯命令行安装，无 GUI 操作；下载途径同时给出官方源与国内镜像（按网络环境选一）。

## ① 基础软件（winget 安装）

| 软件 | 用途 | 安装命令 |
|---|---|---|
| Git for Windows | 版本控制 | `winget install Git.Git` |
| Node.js LTS | node/npm/npx | `winget install OpenJS.NodeJS.LTS` |
| Python 3.12 | 一切脚本基础 | `winget install Python.Python.3.12` |
| Google Chrome | headless 校验、浏览器渲染 | `winget install Google.Chrome` |
| LibreOffice | 批量文档转 PDF/转换 | `winget install TheDocumentFoundation.LibreOffice` |
| Tesseract OCR | OCR 引擎（OCRmyPDF 依赖） | `winget install UB-Mannheim.TesseractOCR`（脚本：GitHub 源失败自动换 gh-proxy 直链；安装位置检测 Test-Tesseract） |

## ② npm 全局包（-UseChinaMirror 走 npmmirror）

| 包 | 用途 |
|---|---|
| opencode-ai | 本体 |
| @mermaid-js/mermaid-cli | 流程图/SVG 渲染 |

## ③ pip 包（-UseChinaMirror 走清华源）

按 `tools-manifest.md` B 类清单逐项安装（pix2text、pypandoc_binary、python-docx、python-pptx、openpyxl、xlrd、pypdf、pdfplumber、pymupdf、matplotlib、pillow、chardet、pyzbar、opencv-python、imageio-ffmpeg、playwright、weasyprint、docxtpl、jinja2、python-magic-bin、ocrmypdf）。脚本已全量纳入：常规 19 包必装，playwright/weasyprint 为可选大件（`-SkipBigPkgs` 跳过，失败仅警告）。

系统级依赖（脚本自动处理）：Tesseract（`winget install UB-Mannheim.TesseractOCR`，OCRmyPDF 依赖）、MSYS2（`winget install MSYS2.MSYS2` + `pacman -S mingw-w64-ucrt-x86_64-gtk3`，WeasyPrint 依赖，脚本自动持久化环境变量 WEASYPRINT_DLL_DIRECTORIES）。

## ④ WSL2 + Ubuntu 22.04

见 `doc\WSL安装步骤说明书.html` 与 `setup\install-wsl.ps1`（初始化时自动装 Linux 工具链：build-essential/gdb/valgrind/cmake/ninja-build/python3-pip/perl/jq/openssh-client）。

## ⑤ 数据（不入 git）

- 3GPP 文档：`setup\download-specs.ps1` 下载或网盘拷贝
- pix2text 模型：首次运行自动下载（约 1GB）

## ⑥ 本机状态文件（部署时生成，不入 git）

- `skills\update_skill\path_map.txt`：占位符→本机路径映射
- `skills\update_skill\sync_target.txt`：同步目标目录记忆
