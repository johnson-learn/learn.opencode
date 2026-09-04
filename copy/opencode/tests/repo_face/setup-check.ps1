# ============================================================
# setup-check.ps1 — 工具检测共享模块（setup-windows.ps1 与 install-tools.ps1 共用）
# 内容：工具清单（必须/可选 + winget 包 id + 检测双通道）、检测函数、PATH 修复函数、输出函数
# 注意：本文件只定义函数与数据，不执行任何动作；两个脚本 dot-source 引入
# ============================================================

function Test-Cmd([string]$cmd) { return $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue) }
function Step([string]$msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Ok([string]$msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Warn([string]$msg) { Write-Host "  [跳过/警告] $msg" -ForegroundColor Yellow }

# LibreOffice 的 soffice 通常不在 PATH，不能只靠 Get-Command 判断是否已安装
function Test-Soffice {
  if (Test-Cmd "soffice") { return $true }
  foreach ($p in @(
    "C:\Program Files\LibreOffice\program\soffice.exe",
    "C:\Program Files\LibreOffice\program\soffice.com",
    "C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "C:\Program Files (x86)\LibreOffice\program\soffice.com"
  )) { if (Test-Path $p) { return $true } }
  return $false
}

# Tesseract 同 soffice：winget 装的不进 PATH，需按安装位置探测（双通道检测）
function Test-Tesseract {
  if (Test-Cmd "tesseract") { return $true }
  foreach ($p in @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
  )) { if (Test-Path $p) { return $true } }
  return $false
}

# 获取当前 python 的 pip Scripts 目录（--user 安装后 p2t 等命令所在位置）
# 2026-09-01 实测修复：pip --user 默认装到 %APPDATA%\Python\Python312\Scripts（Roaming），
# 但部分 Python 安装（winget Local 版）site.getuserbase 不可用导致只回退到 Local Scripts——
# 必须把 Roaming 用户 site Scripts 也纳入候选并优先加入 PATH，否则 p2t 等命令装好也找不到
function Get-PipScriptsDir {
  try {
    $ub = (python -c "import site; print(site.getuserbase())" 2>$null).Trim()
    if ($ub) { $d = Join-Path $ub "Scripts"; if (Test-Path $d) { return $d } }
  } catch {}
  $appData = [Environment]::GetFolderPath("ApplicationData")
  $pyVerMajorMinor = ""
  try { $pyVerMajorMinor = ((python -c "import sys; print('%d%d' % (sys.version_info[0], sys.version_info[1]))" 2>$null).Trim()) } catch {}
  if ($pyVerMajorMinor) {
    $d = Join-Path $appData ("Python\Python" + $pyVerMajorMinor + "\Scripts")
    if (Test-Path $d) { return $d }
  }
  try {
    $sc = (python -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null).Trim()
    if ($sc -and (Test-Path $sc)) { return $sc }
  } catch {}
  return $null
}

# 把目录加入用户级 PATH（已存在则跳过；返回是否写入）
function Add-ToUserPath([string]$dir) {
  if (-not $dir -or -not (Test-Path $dir)) { return $false }
  $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
  if ($userPath -and $userPath.TrimEnd(';') -split ';' -contains $dir.TrimEnd('\')) { return $false }
  [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(';') + ';' + $dir), "User")
  $env:Path += ';' + $dir
  return $true
}

# 工具清单（唯一权威定义，setup 检测与 install-tools 自动安装共用）：
# - tier：必须/可选；必须=缺失不影响基本使用（update_skill 双向同步除外）；可选=使用过程中可随时安装
# - wingetId：winget 包 id（install-tools.ps1 自动安装渠道）；空=非 winget 渠道（npm/pip/手动）
# - check 类字段：cmd（命令检测）/pathDir（PATH 修复目录）/pathChecks（安装位置双通道）/
#   sofficeCheck/tessCheck（专用双通道）/wslCheck（WSL 注册表）/pyImport（pip 包 import 检测）
# - guide：完整安装方法与完整安装命令（未装时随提示输出，含国内镜像方案）
# 后续新增工具：先在 tools-manifest.md 登记，再把检测条目加进本表——test_setup_ps1.py 的
# tools-manifest 对齐检查会强制本表与总表一致（新增工具漏加本表 = 测试失败）
$checks1 = @(
  @{ name = "Git for Windows"; tier = "必须"; cmd = "git"; pathDir = "C:\Program Files\Git\cmd"; wingetId = "Git.Git";
     hint = "winget install Git.Git";
     guide = "安装方法：管理员 PowerShell 执行 winget（推荐）或官网下载安装包；国内 winget 失败可下载 npmmirror 直链 `n完整命令：winget install Git.Git   |   官网 https://git-scm.com/download/win" },
  @{ name = "Node.js LTS";     tier = "必须"; cmd = "node"; pathDir = "C:\Program Files\nodejs"; wingetId = "OpenJS.NodeJS.LTS";
     hint = "winget install OpenJS.NodeJS.LTS";
     guide = "安装方法：管理员 PowerShell 执行 winget（推荐）或官网下载 MSI；国内下载走 npmmirror `n完整命令：winget install OpenJS.NodeJS.LTS   |   官网 https://nodejs.org/zh-cn/download" },
  @{ name = "Python 3.12";     tier = "必须"; cmd = "python"; pathDir = ""; wingetId = "Python.Python.3.12";
     hint = "winget install Python.Python.3.12";
     guide = "安装方法：管理员 PowerShell 执行 winget（推荐）或 python.org 下载安装包（勾选 Add to PATH）；勿用 Microsoft Store 版（路径过长易致 torch 安装失败）`n完整命令：winget install Python.Python.3.12   |   官网 https://www.python.org/downloads/windows/";
     pathChecks = @("$env:LOCALAPPDATA\Programs\Python\Python312\python.exe", "C:\Program Files\Python312\python.exe") },
  @{ name = "opencode CLI";    tier = "必须"; cmd = "opencode"; pathDir = ""; wingetId = "";
     hint = "npm i -g opencode-ai";
     guide = "安装方法：Node.js 已装后 npm 全局安装（国内加 npmmirror 镜像）`n完整命令：npm i -g opencode-ai --registry=https://registry.npmmirror.com";
     npmPkg = "opencode-ai" },
  @{ name = "WSL2 + Ubuntu";   tier = "必须"; cmd = ""; pathDir = ""; wingetId = "";
     hint = "右键管理员运行 setup\install-wsl.ps1（可能需重启）";
     guide = '安装方法（自动）：右键"使用 PowerShell 运行" setup\install-wsl.ps1（启用 WSL 功能+装 Ubuntu 22.04+Linux 工具链，可能需重启一次）`n安装方法（手动）：管理员 PowerShell 执行 wsl --install -d Ubuntu-22.04；离线包下载 https://aka.ms/wslubuntu2204 后 Add-AppxPackage';
     wslCheck = $true },
  @{ name = "Google Chrome";   tier = "可选"; cmd = ""; pathDir = ""; wingetId = "Google.Chrome";
     hint = "winget install Google.Chrome";
     guide = "安装方法：winget（推荐）或官网下载安装器`n完整命令：winget install Google.Chrome   |   官网 https://www.google.com/chrome/";
     pathChecks = @("C:\Program Files\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe") },
  @{ name = "LibreOffice";     tier = "可选"; cmd = "soffice"; pathDir = ""; wingetId = "TheDocumentFoundation.LibreOffice";
     hint = "winget install TheDocumentFoundation.LibreOffice";
     guide = "安装方法：winget（推荐）或官网下载 MSI；国内下载走清华镜像直链`n完整命令：winget install TheDocumentFoundation.LibreOffice   |   清华镜像 https://mirrors.tuna.tsinghua.edu.cn/libreoffice/libreoffice/stable/";
     sofficeCheck = $true },
  @{ name = "Tesseract OCR";   tier = "可选"; cmd = "tesseract"; pathDir = ""; wingetId = "UB-Mannheim.TesseractOCR";
     hint = "winget install UB-Mannheim.TesseractOCR";
     guide = "安装方法：winget（推荐）；winget 失败（GitHub 源被墙）改用 gh-proxy 镜像直链下安装包`n完整命令：winget install UB-Mannheim.TesseractOCR   |   镜像 https://gh-proxy.com/https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0/tesseract-ocr-w64-setup-5.4.0.exe";
     tessCheck = $true },
  @{ name = "mermaid-cli";     tier = "可选"; cmd = "mmdc"; pathDir = ""; wingetId = "";
     hint = "npm i -g @mermaid-js/mermaid-cli";
     guide = "安装方法：Node.js 已装后 npm 全局安装（国内加 npmmirror 镜像）；渲染需设环境变量 PUPPETEER_EXECUTABLE_PATH 指向系统 Chrome（skill 中有记载）`n完整命令：npm i -g @mermaid-js/mermaid-cli --registry=https://registry.npmmirror.com";
     npmPkg = "@mermaid-js/mermaid-cli" },
  @{ name = "playwright";      tier = "可选"; cmd = ""; pathDir = ""; wingetId = "";
     hint = "pip install playwright 后 python -m playwright install chromium";
     guide = "安装方法：pip 装包 + 下载 chromium 内核（约 300MB；国内设 PLAYWRIGHT_DOWNLOAD_HOST 镜像）`n完整命令：pip install playwright -i https://pypi.tuna.tsinghua.edu.cn/simple；$env:PLAYWRIGHT_DOWNLOAD_HOST='https://npmmirror.com/mirrors/playwright'；python -m playwright install chromium";
     pyImport = "playwright"; pipPkg = "playwright" },
  @{ name = "weasyprint";      tier = "可选"; cmd = ""; pathDir = ""; wingetId = "";
     hint = "pip install weasyprint（先 winget install MSYS2.MSYS2 + pacman -S mingw-w64-ucrt-x86_64-gtk3）";
     guide = "安装方法：pip 装包 + MSYS2 装 GTK3 DLL + 永久环境变量（缺 GTK 时 import 正常但渲染报 DLL 错）`n完整命令：1) pip install weasyprint -i https://pypi.tuna.tsinghua.edu.cn/simple  2) winget install MSYS2.MSYS2  3) C:\msys64\usr\bin\bash.exe -lc 'pacman -Syu --noconfirm; pacman -S --noconfirm mingw-w64-ucrt-x86_64-gtk3'  4) setx WEASYPRINT_DLL_DIRECTORIES C:\msys64\ucrt64\bin";
     pyImport = "weasyprint"; pipPkg = "weasyprint" }
)

# 检测判定（双通道：命令 OR 安装位置；Python 包 OR import；WSL 注册表）
function Test-ToolEntry($t) {
  if ($t.wslCheck) {
    foreach ($root in @("HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss","HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss")) {
      foreach ($k in (Get-ChildItem $root -ErrorAction SilentlyContinue)) {
        $dn = (Get-ItemProperty $k.PSPath -ErrorAction SilentlyContinue).DistributionName
        if ($dn -and $dn -match "Ubuntu") { return $true }
      }
    }
    return $false
  }
  if ($t.sofficeCheck) { return (Test-Soffice) }
  if ($t.tessCheck) { return (Test-Tesseract) }
  if ($t.pyImport) {
    if (-not (Test-Cmd "python")) { return $false }
    python -c "import $($t.pyImport)" 2>$null
    return ($LASTEXITCODE -eq 0)
  }
  if ($t.pathChecks) {
    foreach ($p in $t.pathChecks) { if ($p -and (Test-Path $p)) { return $true } }
  }
  if ($t.cmd) { return (Test-Cmd $t.cmd) }
  return $false
}

# pip 常规包 import 检测表（与 tools-manifest B 类一致；test_setup_ps1.py 清单对齐检查强制同步）
$pyPkgs = @(
  @{ pkg = "pix2text";        mod = "pix2text" },
  @{ pkg = "matplotlib";      mod = "matplotlib" },
  @{ pkg = "PyMuPDF";         mod = "pymupdf" },
  @{ pkg = "pillow";          mod = "PIL" },
  @{ pkg = "pypandoc-binary"; mod = "pypandoc" },
  @{ pkg = "python-docx";     mod = "docx" },
  @{ pkg = "python-pptx";     mod = "pptx" },
  @{ pkg = "openpyxl";        mod = "openpyxl" },
  @{ pkg = "xlrd";            mod = "xlrd" },
  @{ pkg = "pypdf";           mod = "pypdf" },
  @{ pkg = "pdfplumber";      mod = "pdfplumber" },
  @{ pkg = "chardet";         mod = "chardet" },
  @{ pkg = "pyzbar";          mod = "pyzbar" },
  @{ pkg = "opencv-python";   mod = "cv2" },
  @{ pkg = "imageio-ffmpeg";  mod = "imageio_ffmpeg" },
  @{ pkg = "docxtpl";         mod = "docxtpl" },
  @{ pkg = "Jinja2";          mod = "jinja2" },
  @{ pkg = "python-magic-bin";mod = "magic" },
  @{ pkg = "ocrmypdf";        mod = "ocrmypdf" }
)
