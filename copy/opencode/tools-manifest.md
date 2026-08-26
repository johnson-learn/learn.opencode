# 工具总清单（Tools Manifest）—— 唯一权威工具管理表

> 本表是全体系工具的唯一权威清单：新机器移植时按本表逐项检查安装。
> **收录范围**：① 所有全局 skill 依赖的工具；② 项目级 skill 依赖的工具；③ 思考回答中发现的好用工具/脚本/库（即使未写进任何具体 skill，也登记本表——可先入"待补充"清单，装好后移入对应类别）。
> **更新铁律**：任何 skill（含项目级）新增依赖工具、或会话中发现好用工具时，必须同步更新本表（instructions.md 规范 3c 条强制执行）。
> 各 skill 的「工具依赖清单」章节为本表的分 skill 视角摘录，冲突时以本表为准。

## 分类速览

| 类别 | 工具数 | 安装方式 |
|---|---|---|
| A. 基础环境 | 5 | winget/官方 |
| B. Python 环境与核心包 | 20 | pip 清华源 |
| C. 文档处理工具 | 4 | winget/pip |
| D. OCR 与公式识别 | 2 | pip |
| E. 网络与同步 | 4 | 自带/apt |
| F. 编程环境 | 3 | 离线包/apt |
| G. 校验与辅助 | 3 | 自带/脚本 |

---

## A. 基础环境（winget / 官方安装，非 GitHub 源）

| 工具 | 用途 | 安装命令 | 检查命令 |
|---|---|---|---|
| Git for Windows | 版本控制 | `winget install Git.Git` | `git --version` |
| Node.js LTS | node/npm/npx | `winget install OpenJS.NodeJS.LTS` | `node --version` |
| Python 3.12 | 一切脚本基础 | `winget install Python.Python.3.12` | `python --version` |
| Google Chrome | headless 校验、浏览器渲染 | `winget install Google.Chrome` | 检查 `<Chrome目录>\chrome.exe` |
| LibreOffice 26.x | 批量文档转 PDF/转换 | `winget install TheDocumentFoundation.LibreOffice` | `soffice.com --headless -env:UserInstallation=file:///<工具目录>Temp/LO --version` |

## B. Python 环境与核心包（pip 清华源：`-i https://pypi.tuna.tsinghua.edu.cn/simple`）

| 包 | 用途 | 安装命令 | 检查命令 |
|---|---|---|---|
| pix2text | 公式/版面 OCR（核心） | `pip install pix2text`（首次自动下模型 ~1GB） | `p2t.exe predict -h` |
| pypandoc-binary | pandoc 内嵌（md⇄docx 等） | `pip install pypandoc_binary` | `python -c "import pypandoc; print(pypandoc.get_pandoc_path())"` |
| python-docx | Word 读写 | `pip install python-docx` | `python -c "import docx"` |
| python-pptx | PPT 读写 | `pip install python-pptx` | `python -c "import pptx"` |
| openpyxl | Excel .xlsx 读写 | `pip install openpyxl` | `python -c "import openpyxl"` |
| xlrd | 老 .xls 读取（openpyxl 不支持） | `pip install xlrd`（2.x 仅支持 .xls，本机 2.0.2 实测） | `python -c "import xlrd; print(xlrd.__version__)"` |
| pypdf | PDF 基础操作 | `pip install pypdf` | `python -c "import pypdf"` |
| pdfplumber | PDF 文本/表格精确提取 | `pip install pdfplumber` | `python -c "import pdfplumber"` |
| PyMuPDF | PDF 渲染 PNG/文本搜索 | `pip install pymupdf` | `python -c "import pymupdf"` |
| matplotlib | 公式/图表渲染 PNG/SVG/PDF | `pip install matplotlib` | `python -c "import matplotlib"` |
| pillow | 图像处理基础 | `pip install pillow` | `python -c "import PIL"` |
| chardet | 编码检测 | `pip install chardet` | `python -c "import chardet"` |
| pyzbar | 条码/二维码解码 | `pip install pyzbar` | `python -c "import pyzbar"` |
| opencv-python + imageio-ffmpeg | 视频抽帧、音视频 | `pip install opencv-python imageio-ffmpeg` | `python -c "import cv2, imageio_ffmpeg"` |
| playwright | headless 浏览器渲染 HTML→PDF/截图 | `pip install playwright` + `python -m playwright install chromium`（下载慢设 `PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright`） | `python -c "from playwright.sync_api import sync_playwright"`（本机实测 HTML→PDF ✓） |
| weasyprint | HTML/CSS→矢量 PDF | `pip install weasyprint` + MSYS2：`winget install MSYS2.MSYS2` → `pacman -S mingw-w64-ucrt-x86_64-gtk3` + 永久环境变量 `WEASYPRINT_DLL_DIRECTORIES=<工具目录>msys64\ucrt64\bin` | `python -c "import weasyprint; print(weasyprint.__version__)"`（本机 69.0 实测 ✓） |
| docxtpl | Word 模板渲染（docx 模板 + jinja2） | `pip install docxtpl` | `python -c "import docxtpl"` |
| jinja2 | 模板引擎（docxtpl 依赖） | `pip install jinja2` | `python -c "import jinja2"` |
| python-magic-bin | 文件类型魔数识别（Windows 免装 libmagic） | `pip install python-magic-bin` | `python -c "import magic"` |
| ocrmypdf | 扫描 PDF OCR（转可搜索 PDF） | `pip install ocrmypdf`（依赖 ghostscript/tesseract 系统组件） | `python -c "import ocrmypdf"` |

## C. 文档处理工具

| 工具 | 用途 | 安装命令 | 检查命令 |
|---|---|---|---|
| OCRmyPDF | 扫描 PDF 加 OCR 层（可搜索） | `pip install ocrmypdf`（依赖 tesseract 引擎，见 D 类；本机 17.10.0 实测扫描件→可搜索 PDF ✓） | `python -m ocrmypdf --version`（exe 不在 PATH，用 -m 方式） |
| docxtpl | Word 模板填充 | `pip install docxtpl` | `python -c "from docxtpl import DocxTemplate"` |
| Jinja2 | 模板渲染（文档/HTML/报告） | `pip install jinja2` | `python -c "from jinja2 import Template"` |
| python-magic | 文件类型 magic bytes 检测 | `pip install python-magic-bin`（Windows） | `python -c "import magic"` |

## D. OCR 与公式识别

| 工具 | 用途 | 安装命令 | 检查命令 |
|---|---|---|---|
| Pix2Text（同 B 类） | 公式/中文 OCR | — | — |
| Tesseract（OCRmyPDF 依赖） | 通用 OCR 引擎（100+ 语言） | `winget install UB-Mannheim.TesseractOCR`（GitHub 源可能失败→改 gh-proxy 下安装包） | `& "<工具目录>Program Files\Tesseract-OCR\tesseract.exe" --version`（本机 5.4.0 ✓） |

## E. 网络与同步

| 工具 | 用途 | 安装命令 | 检查命令 |
|---|---|---|---|
| curl.exe | 下载/探测 | Windows 自带 | `curl.exe --version` |
| gh-proxy.com / ghproxy.net | GitHub 镜像渠道（零安装） | — | `curl -sL -m 20 -o NUL -w %{http_code} https://gh-proxy.com/` |
| git（WSL 内） | 仓库同步 | `apt install git` | `wsl -d Ubuntu -e bash -c "git --version"` |
| SSH 密钥 | GitHub 推送认证 | 生成并添加 GitHub 账号 | `ssh -T git@github.com` |

## F. 编程环境

| 工具 | 用途 | 安装命令 | 检查命令 |
|---|---|---|---|
| WSL2 + Ubuntu 22.04 | Linux 编译运行环境 | 离线包 `<离线安装包目录>\`（MSI+rootfs），见 WSL 安装说明书 | `wsl -l -v` |
| Linux 工具链（gcc/g++/make/cmake/gdb/valgrind/python3/perl/jq 等） | C/C++/脚本开发 | `apt install build-essential gdb valgrind cmake ninja-build python3 python3-pip perl jq git openssh-client` | `wsl -d Ubuntu -e bash -c "gcc --version && gdb --version"` |
| w64devkit（备选） | Windows 原生编译（winpthreads） | gh-proxy.com 下 `w64devkit-x64-2.9.1.7z.exe` 自解压 | `& "<工具目录>w64devkit\w64devkit\bin\gcc.exe" --version` |

## G. 校验与辅助

| 工具 | 用途 | 安装命令 | 检查命令 |
|---|---|---|---|
| skill_validate.py | skill 自检（frontmatter/路由） | 随仓库 scripts/ | `python scripts\skill_validate.py` |
| path_convert.py | 路径占位符双向转换 | 随仓库 scripts/ | `python scripts\path_convert.py` |
| 本机 PS 脚本集 | 文档提取/OCR/页面校验 | 随仓库 scripts/ 部署到 `%LOCALAPPDATA%\Temp\opencode\` | `Test-Path %LOCALAPPDATA%\Temp\opencode\extract-docx.ps1` |

---

## 本机配置（非安装类，移植时需重建）

| 配置 | 位置 | 说明 |
|---|---|---|
| path_map.txt | `<opencode配置目录>\skills\update_skill\path_map.txt` | 占位符→本机路径映射（工具类自动探测、数据类默认/定制） |
| sync_target.txt | 同上目录 | update_skill 同步目标目录记忆 |
| apt 清华源 | WSL 内 /etc/apt/sources.list | 加速 apt |
| pip 清华源 | 命令行参数 | 见 B 类安装命令 |
| WSL 开机自启任务 | 计划任务 WSL-AutoStart | 保持实例运行防 60s idle 停止 |
| WEASYPRINT_DLL_DIRECTORIES | 用户环境变量 = `<工具目录>msys64\ucrt64\bin` | WeasyPrint 加载 MSYS2 GTK DLL 必需（已永久设置） |

## 待补充（本机已分析未安装，装时更新本表）

- FFmpeg 完整版：`winget install Gyan.FFmpeg`
- yt-dlp：`pip install yt-dlp`
- ImageMagick：`winget install ImageMagick.ImageMagick`
