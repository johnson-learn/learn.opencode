# ============================================================
# setup-windows.ps1 — 新电脑一键环境安装与配置
# 用途：根据本仓库迁移包，把全局 skill + 配置 + 辅助脚本部署到新电脑，
#       并自动安装全部依赖工具（可勾选）。
# 用法：右键"使用 PowerShell 运行"，或在 PowerShell 中执行：
#       powershell -NoProfile -ExecutionPolicy Bypass -File setup-windows.ps1
# 说明：安装类操作会请求管理员权限（UAC 弹窗）；全部为官方/镜像静默安装。
# ============================================================
param(
  [switch]$SkipWinget,      # 跳过 winget 安装的软件（Git/Node/Python/Chrome/LibreOffice）
  [switch]$SkipNpm,         # 跳过 npm 全局包（opencode/mermaid-cli）
  [switch]$SkipPip,         # 跳过 pip 包（pix2text/matplotlib/pymupdf/pillow）
  [switch]$SkipDeploy,      # 跳过 skill/配置/脚本部署
  [switch]$SkipWsl,         # 跳过 WSL 安装
  [switch]$UseChinaMirror,  # npm/pip 使用国内镜像
  [switch]$NoPathRewrite    # 部署时不改写旧机路径（不推荐）
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $RepoRoot            # 脚本在 setup\ 下，仓库根是其上一级
$ConfigDir = Join-Path $env:USERPROFILE ".config\opencode"
$ToolDir = Join-Path $env:LOCALAPPDATA "Temp\opencode"   # skill 引用的脚本目录（与原机约定一致）
$OLD_USER = "job_p"      # 旧机用户名（skill 文本中写死的路径的用户名，按实际情况修改）
$OLD_TEMP = "C:\Users\$OLD_USER\AppData\Local\Temp\opencode"
$OLD_EDRIVE = "E:\openCodeDefault\temp"

function Test-Cmd([string]$cmd) { return $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue) }
function Step([string]$msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Ok([string]$msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Warn([string]$msg) { Write-Host "  [跳过/警告] $msg" -ForegroundColor Yellow }

# ---------- 0. 前置检查 ----------
Step "0. 前置检查"
$psVer = $PSVersionTable.PSVersion
Write-Host "  PowerShell $psVer；脚本要求 5.1+（Windows 10/11 内置即满足）"
if ($psVer.Major -lt 5) { Write-Host "  [失败] PowerShell 版本过低" -ForegroundColor Red; exit 1 }

# ---------- 1. winget 安装基础软件 ----------
if (-not $SkipWinget) {
  Step "1. 基础软件安装（winget 静默）"
  if (-not (Test-Cmd "winget")) {
    Warn "winget 不存在，跳过软件安装。请手动安装 Git/Node/Python/Chrome/LibreOffice（见 REQUIREMENTS.md §1）"
  } else {
    $pkgs = @(
      @{ id = "Git.Git";                  name = "Git for Windows" },
      @{ id = "OpenJS.NodeJS.LTS";        name = "Node.js LTS" },
      @{ id = "Python.Python.3.12";       name = "Python 3.12" },
      @{ id = "Google.Chrome";            name = "Google Chrome" },
      @{ id = "TheDocumentFoundation.LibreOffice"; name = "LibreOffice" }
    )
    foreach ($p in $pkgs) {
      $already = $false
      if ($p.id -eq "Git.Git") { $already = Test-Cmd "git" }
      elseif ($p.id -eq "OpenJS.NodeJS.LTS") { $already = Test-Cmd "node" }
      elseif ($p.id -eq "Python.Python.3.12") { $already = Test-Cmd "python" }
      elseif ($p.id -eq "Google.Chrome") { $already = Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe" }
      elseif ($p.id -eq "TheDocumentFoundation.LibreOffice") { $already = Test-Cmd "soffice" }
      if ($already) { Ok "$($p.name) 已安装"; continue }
      Write-Host "  安装 $($p.name) ...（可能耗时数分钟，请耐心等待）"
      winget install --id $p.id -e --accept-source-agreements --accept-package-agreements --silent
      if ($?) { Ok "$($p.name) 安装完成" } else { Warn "$($p.name) 安装失败，可手动安装（见 REQUIREMENTS.md）" }
    }
  }
} else { Warn "已跳过基础软件安装（-SkipWinget）" }

# ---------- 2. npm 全局包 ----------
if (-not $SkipNpm) {
  Step "2. npm 全局包（opencode / mermaid-cli）"
  if (-not (Test-Cmd "npm")) {
    Warn "npm 不可用（Node.js 未装或未刷新 PATH）。装好 Node 后重跑本脚本即可。"
  } else {
    $reg = if ($UseChinaMirror) { "--registry=https://registry.npmmirror.com" } else { "" }
    if (-not (Test-Cmd "opencode")) {
      npm i -g opencode-ai $reg
      if ($?) { Ok "opencode-ai 安装完成" } else { Warn "opencode-ai 安装失败" }
    } else { Ok "opencode 已安装" }
    if (-not (Test-Cmd "mmdc")) {
      npm i -g @mermaid-js/mermaid-cli $reg
      if ($?) { Ok "mermaid-cli 安装完成" } else { Warn "mermaid-cli 安装失败" }
    } else { Ok "mmdc 已安装" }
  }
} else { Warn "已跳过 npm 全局包（-SkipNpm）" }

# ---------- 3. pip 包 ----------
if (-not $SkipPip) {
  Step "3. pip 包（pix2text / matplotlib / PyMuPDF / pillow）"
  if (-not (Test-Cmd "python")) {
    Warn "python 不可用（未装或未刷新 PATH）。装好后重跑本脚本即可。"
  } else {
    $pi = if ($UseChinaMirror) { "-i https://pypi.tuna.tsinghua.edu.cn/simple" } else { "" }
    foreach ($pkg in @("pix2text","matplotlib","PyMuPDF","pillow")) {
      Write-Host "  pip install $pkg ..."
      python -m pip install --upgrade $pkg $pi
      if ($?) { Ok "$pkg 安装完成" } else { Warn "$pkg 安装失败" }
    }
    if (-not (Test-Cmd "p2t")) { Warn "p2t 命令未在 PATH（pip 的 Scripts 目录未入 PATH，可手动加：%LOCALAPPDATA%\Programs\Python\Python312\Scripts 或 Python 安装目录\Scripts）" }
  }
} else { Warn "已跳过 pip 包（-SkipPip）" }

# ---------- 4. WSL ----------
if (-not $SkipWsl) {
  Step "4. WSL2 + Ubuntu 22.04"
  $wslOk = $false
  try { $l = wsl -l -v 2>&1; $wslOk = ($l -match "Ubuntu-22.04") } catch { $wslOk = $false }
  if ($wslOk) { Ok "WSL Ubuntu-22.04 已就绪" }
  else {
    Write-Host "  运行 install-wsl.ps1（需要管理员权限，可能要求重启）..."
    $installer = Join-Path $RepoRoot "setup\install-wsl.ps1"
    if (Test-Path $installer) {
      Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File","`"$installer`""
      Write-Host "  已启动管理员窗口安装 WSL，请在弹窗中确认。装完可重跑本脚本验证。"
    } else { Warn "install-wsl.ps1 未找到" }
  }
} else { Warn "已跳过 WSL（-SkipWsl）" }

# ---------- 5. 部署 skill / 配置 / 脚本 ----------
if (-not $SkipDeploy) {
  Step "5. 部署全局 skill 与配置"
  $srcSkills = Join-Path $RepoRoot "opencode\skills"
  $dstSkills = Join-Path $ConfigDir "skills"
  if (-not (Test-Path $srcSkills)) { Warn "仓库内 opencode\skills 不存在，跳过" }
  else {
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    foreach ($f in @("opencode.jsonc","instructions.md","evolution.md","package.json")) {
      $s = Join-Path $RepoRoot "opencode\$f"
      if (Test-Path $s) { Copy-Item $s $ConfigDir -Force }
    }
    New-Item -ItemType Directory -Path $dstSkills -Force | Out-Null
    Get-ChildItem $srcSkills -Directory | ForEach-Object {
      robocopy $_.FullName (Join-Path $dstSkills $_.Name) /E /NFL /NDL /NJH /NJS /NP | Out-Null
    }
    Ok "skills/配置已部署到 $ConfigDir"
  }

  Step "6. 部署辅助脚本到 $ToolDir"
  $srcScripts = Join-Path $RepoRoot "scripts"
  if (Test-Path $srcScripts) {
    New-Item -ItemType Directory -Path $ToolDir -Force | Out-Null
    Copy-Item (Join-Path $srcScripts "*") $ToolDir -Force -Recurse
    Ok "辅助脚本已部署（extract-docx/doc、ocr、check-*、color-asn1、inject_skills 等）"
  } else { Warn "scripts 目录不存在" }

  # ---------- 7. 路径改写（旧机路径 → 新机路径） ----------
  if (-not $NoPathRewrite) {
    Step "7. 路径改写（把 skill 文本中的旧机路径替换为新机路径）"
    $newUser = $env:USERNAME
    $newProfile = $env:USERPROFILE
    $newTemp = Join-Path $env:LOCALAPPDATA "Temp\opencode"
    $targets = @()
    $targets += Get-ChildItem $ConfigDir -Recurse -File -Include "*.md","*.json","*.jsonc","*.txt" -ErrorAction SilentlyContinue
    $targets += Get-ChildItem $ToolDir -Recurse -File -Include "*.ps1","*.py","*.md" -ErrorAction SilentlyContinue
    $n = 0
    foreach ($tf in $targets) {
      $t = [System.IO.File]::ReadAllText($tf.FullName)
      $orig = $t
      $t = $t.Replace($OLD_TEMP, $newTemp)
      $t = $t.Replace("C:\Users\$OLD_USER\", "$newProfile\")
      $t = $t.Replace("C:/Users/$OLD_USER/", "$newProfile/".Replace("\","/"))
      $t = $t.Replace($OLD_EDRIVE, $newTemp)
      if ($t -ne $orig) {
        [System.IO.File]::WriteAllText($tf.FullName, $t, (New-Object System.Text.UTF8Encoding($false)))
        $n++
      }
    }
    Ok "路径改写完成：$n 个文件（$OLD_TEMP / C:\Users\$OLD_USER / $OLD_EDRIVE → 新机路径）"
  } else { Warn "已跳过路径改写（-NoPathRewrite）" }
} else { Warn "已跳过部署（-SkipDeploy）" }

# ---------- 8. 汇总验证 ----------
Step "8. 验证汇总"
$checks = @(
  @{ name = "opencode CLI";    ok = (Test-Cmd "opencode") },
  @{ name = "mmdc";            ok = (Test-Cmd "mmdc") },
  @{ name = "python";          ok = (Test-Cmd "python") },
  @{ name = "p2t";             ok = (Test-Cmd "p2t") },
  @{ name = "git";             ok = (Test-Cmd "git") },
  @{ name = "soffice";         ok = (Test-Cmd "soffice") },
  @{ name = "Chrome";          ok = (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") -or (Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe") },
  @{ name = "skills 部署";     ok = (Test-Path (Join-Path $ConfigDir "skills\3gpp_skill\SKILL.md")) },
  @{ name = "辅助脚本部署";    ok = (Test-Path (Join-Path $ToolDir "extract-docx.ps1")) }
)
foreach ($c in $checks) {
  if ($c.ok) { Ok $c.name } else { Warn "$($c.name) 缺失（见 REQUIREMENTS.md 手动补装）" }
}
Write-Host ""
Write-Host "完成。请重启 opencode（或新开终端）使 skill 生效。" -ForegroundColor Cyan
Write-Host "提示：p2t 首次使用会自动下载模型（约 1~2 GB）；网络慢时执行：" -ForegroundColor Cyan
Write-Host '  $env:HF_ENDPOINT = "https://hf-mirror.com"' -ForegroundColor Cyan
