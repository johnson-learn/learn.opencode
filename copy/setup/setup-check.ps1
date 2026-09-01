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
function Get-PipScriptsDir {
  try {
    $ub = (python -c "import site; print(site.getuserbase())" 2>$null).Trim()
    if ($ub) { $d = Join-Path $ub "Scripts"; if (Test-Path $d) { return $d } }
  } catch {}
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
# 后续新增工具：先在 tools-manifest.md 登记，再把检测条目加进本表——test_setup_ps1.py 的
# tools-manifest 对齐检查会强制本表与总表一致（新增工具漏加本表 = 测试失败）
$checks1 = @(
  @{ name = "Git for Windows"; tier = "必须"; cmd = "git"; pathDir = "C:\Program Files\Git\cmd"; wingetId = "Git.Git"; hint = "winget install Git.Git" },
  @{ name = "Node.js LTS";     tier = "必须"; cmd = "node"; pathDir = "C:\Program Files\nodejs"; wingetId = "OpenJS.NodeJS.LTS"; hint = "winget install OpenJS.NodeJS.LTS" },
  @{ name = "Python 3.12";     tier = "必须"; cmd = "python"; pathDir = ""; wingetId = "Python.Python.3.12"; hint = "winget install Python.Python.3.12"; pathChecks = @("$env:LOCALAPPDATA\Programs\Python\Python312\python.exe", "C:\Program Files\Python312\python.exe") },
  @{ name = "opencode CLI";    tier = "必须"; cmd = "opencode"; pathDir = ""; wingetId = ""; hint = "npm i -g opencode-ai（-UseChinaMirror 走 npmmirror）"; npmPkg = "opencode-ai" },
  @{ name = "WSL2 + Ubuntu";   tier = "必须"; cmd = ""; pathDir = ""; wingetId = ""; hint = "右键管理员运行 setup\install-wsl.ps1（可能需重启）；离线包见 REQUIREMENTS.md"; wslCheck = $true },
  @{ name = "Google Chrome";   tier = "可选"; cmd = ""; pathDir = ""; wingetId = "Google.Chrome"; hint = "winget install Google.Chrome"; pathChecks = @("C:\Program Files\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe") },
  @{ name = "LibreOffice";     tier = "可选"; cmd = "soffice"; pathDir = ""; wingetId = "TheDocumentFoundation.LibreOffice"; hint = "winget install TheDocumentFoundation.LibreOffice"; sofficeCheck = $true },
  @{ name = "Tesseract OCR";   tier = "可选"; cmd = "tesseract"; pathDir = ""; wingetId = "UB-Mannheim.TesseractOCR"; hint = "winget install UB-Mannheim.TesseractOCR"; tessCheck = $true },
  @{ name = "mermaid-cli";     tier = "可选"; cmd = "mmdc"; pathDir = ""; wingetId = ""; hint = "npm i -g @mermaid-js/mermaid-cli"; npmPkg = "@mermaid-js/mermaid-cli" },
  @{ name = "playwright";      tier = "可选"; cmd = ""; pathDir = ""; wingetId = ""; hint = "pip install playwright 后 python -m playwright install chromium"; pyImport = "playwright"; pipPkg = "playwright" },
  @{ name = "weasyprint";      tier = "可选"; cmd = ""; pathDir = ""; wingetId = ""; hint = "pip install weasyprint（先 winget install MSYS2.MSYS2 + pacman -S mingw-w64-ucrt-x86_64-gtk3）"; pyImport = "weasyprint"; pipPkg = "weasyprint" }
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
