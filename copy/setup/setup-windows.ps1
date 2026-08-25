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

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

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

# 依据 winget 包 id 判断是否已装（Chrome/LibreOffice 用安装路径判断更可靠）
function Test-Pkg([string]$id) {
  switch ($id) {
    "Git.Git"                     { return (Test-Cmd "git") }
    "OpenJS.NodeJS.LTS"           { return (Test-Cmd "node") }
    "Python.Python.3.12"          { return (Test-Cmd "python") }
    "Google.Chrome"               { return (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") }
    "TheDocumentFoundation.LibreOffice" { return (Test-Soffice) }
    default                       { return $false }
  }
}

# 获取当前 python 的 pip Scripts 目录（--user 安装后 p2t 等命令所在位置）
function Get-PipScriptsDir {
  try {
    $ub = (python -c "import site; print(site.getuserbase())" 2>$null).Trim()
    if ($ub) { $d = Join-Path $ub "Scripts"; if (Test-Path $d) { return $d } }
  } catch {}
  # 回退：sysconfig 的 scripts 路径
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

# ---------- 0. 前置检查 ----------
Step "0. 前置检查"
$psVer = $PSVersionTable.PSVersion
Write-Host "  PowerShell $psVer；脚本要求 5.1+（Windows 10/11 内置即满足）"
if ($psVer.Major -lt 5) { Write-Host "  [失败] PowerShell 版本过低" -ForegroundColor Red; exit 1 }

# 启用 Windows 长路径（默认关闭，会导致 pip 安装 torch/pix2text 时因路径超 260 字符报 OSError）
$lpKey = "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem"
$lp = Get-ItemProperty -Path $lpKey -Name LongPathsEnabled -ErrorAction SilentlyContinue
if ($lp.LongPathsEnabled -ne 1) {
  if ($isAdmin) {
    Set-ItemProperty -Path $lpKey -Name LongPathsEnabled -Value 1 -Type DWord
    Ok "已启用 Windows 长路径（LongPathsEnabled=1，建议重启后生效）"
  } else {
    Warn "Windows 长路径未启用，pip 安装 torch/pix2text 可能因路径过长失败。请以管理员运行一次：reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f"
  }
} else {
  Ok "Windows 长路径已启用（LongPathsEnabled=1）"
}

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
      $already = Test-Pkg $p.id
      if ($already) { Ok "$($p.name) 已安装"; continue }
      Write-Host "  安装 $($p.name) ...（可能耗时数分钟，请耐心等待）"
      winget install --id $p.id -e --accept-source-agreements --accept-package-agreements --silent | Out-Null
      # winget 在"已装但无可用升级"等场景下返回码可能非 0，故结合再检测判断是否成功
      if (($LASTEXITCODE -eq 0) -or (Test-Pkg $p.id)) { Ok "$($p.name) 安装完成" } else { Warn "$($p.name) 安装失败，可手动安装（见 REQUIREMENTS.md）" }
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
    # 识别 Microsoft Store 版 Python（路径含 WindowsApps，其 --user 目录极长，易触发 torch 安装失败）
    $pyExe = $null
    try { $pyExe = (python -c "import sys; print(sys.executable)" 2>$null).Trim() } catch {}
    if ($pyExe -and $pyExe -like "*WindowsApps*") {
      Warn "检测到 Microsoft Store 版 Python（$pyExe）。其用户目录路径过长，torch/pix2text 可能安装失败。建议用 winget 安装官方 Python 3.12 后重跑本脚本。"
    }
    $pi = if ($UseChinaMirror) { "-i https://pypi.tuna.tsinghua.edu.cn/simple" } else { "" }
    foreach ($pkg in @("pix2text","matplotlib","PyMuPDF","pillow")) {
      Write-Host "  pip install $pkg ..."
      python -m pip install --upgrade --user $pkg $pi
      if ($LASTEXITCODE -eq 0) { Ok "$pkg 安装完成" } else { Warn "$pkg 安装失败" }
    }
    # 把 pip 的 Scripts 目录加入用户 PATH（否则 p2t 等命令找不到）
    $scriptsDir = Get-PipScriptsDir
    if ($scriptsDir -and (Add-ToUserPath $scriptsDir)) {
      Ok "已将 pip Scripts 目录加入用户 PATH：$scriptsDir（新开终端生效）"
    }
    if (-not (Test-Cmd "p2t")) { Warn "p2t 命令仍未在 PATH（可手动加：$scriptsDir）" }
  }
} else { Warn "已跳过 pip 包（-SkipPip）" }

# ---------- 4. WSL ----------
if (-not $SkipWsl) {
  Step "4. WSL2 + Ubuntu 22.04"
  $wslOk = $false
  # 发行版注册位置：新版 WSL（应用商店版）在 HKCU，旧版在 HKLM；发行版名可能为 Ubuntu / Ubuntu-22.04。
  # 用注册表判断可避免 wsl.exe 输出 UTF-16 编码导致的字符串匹配失效问题。
  foreach ($root in @("HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss","HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss")) {
    foreach ($k in (Get-ChildItem $root -ErrorAction SilentlyContinue)) {
      $dn = (Get-ItemProperty $k.PSPath -ErrorAction SilentlyContinue).DistributionName
      if ($dn -and $dn -match "Ubuntu") { $wslOk = $true; break }
    }
    if ($wslOk) { break }
  }
  if ($wslOk) { Ok "WSL Ubuntu 已就绪" }
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
    # 部署 plugins\（skill-banner.js 等 opencode 插件）
    $srcPlugins = Join-Path $RepoRoot "opencode\plugins"
    if (Test-Path $srcPlugins) {
      New-Item -ItemType Directory -Path (Join-Path $ConfigDir "plugins") -Force | Out-Null
      robocopy $srcPlugins (Join-Path $ConfigDir "plugins") /E /NFL /NDL /NJH /NJS /NP | Out-Null
    }
    # 安装 skill-banner 插件依赖（@opencode-ai/plugin），否则 plugins\skill-banner.js 无法加载
    if ((Test-Path (Join-Path $ConfigDir "package.json")) -and (Test-Cmd "npm")) {
      Push-Location $ConfigDir
      try { npm install --no-audit --no-fund 2>&1 | Out-Null; Ok "skill-banner 插件依赖已安装" } catch { Warn "skill-banner 插件依赖安装失败（可手动在 $ConfigDir 运行 npm install）" }
      Pop-Location
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

  # ---------- 7. 路径改写（旧机路径 → 新机路径） ----------  # ---------- 6.5 自动探测安装工具目录并生成 path_map.txt ----------
  Step "6.5 自动探测工具安装目录（生成 path_map.txt）"
  $pathMapFile = Join-Path $ConfigDir "skills\update_skill\path_map.txt"
  New-Item -ItemType Directory -Path (Split-Path $pathMapFile) -Force | Out-Null

  # 探测函数：在候选目录中找标记文件，命中即返回目录
  function Find-AppDir {
    param([string[]]$Candidates, [string]$Marker)
    foreach ($p in $Candidates) {
      if ($p -and (Test-Path (Join-Path $p $Marker))) { return $p.TrimEnd("\") }
    }
    return ""
  }

  $loDir = Find-AppDir @(
    "C:\Program Files\LibreOffice",
    "C:\Program Files (x86)\LibreOffice",
    "D:\LibreOffice",
    "D:\Program Files\LibreOffice"
  ) "program\soffice.com"
  if (-not $loDir -and (Test-Soffice)) {
    try { $loDir = (Split-Path -Parent (Split-Path -Parent (Get-Command soffice).Source)) } catch {}
  }

  $chromeDir = Find-AppDir @(
    "C:\Program Files\Google\Chrome\Application",
    "C:\Program Files (x86)\Google\Chrome\Application",
    "${env:LOCALAPPDATA}\Google\Chrome\Application"
  ) "chrome.exe"

  $nodeDir = ""
  try { if (Test-Cmd "node") { $nodeDir = Split-Path -Parent (Get-Command node).Source } } catch {}

  # w64devkit：从 PATH 或常见盘符探测
  $toolDir = ""
  foreach ($p in @("C:\w64devkit", "D:\w64devkit", "E:\w64devkit")) {
    if (Test-Path (Join-Path $p "w64devkit\bin\gcc.exe")) { $toolDir = Split-Path $p; break }
  }

  # WSL 安装目录：从注册表 BasePath 探测
  $wslDir = ""
  foreach ($root in @("HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss", "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss")) {
    foreach ($k in (Get-ChildItem $root -ErrorAction SilentlyContinue)) {
      $bp = (Get-ItemProperty $k.PSPath -ErrorAction SilentlyContinue).BasePath
      if ($bp) { $wslDir = $bp; break }
    }
    if ($wslDir) { break }
  }

  # 生成 path_map.txt：工具类自动探测；数据类交互选择（幂等：已配置过则直接复用，不重复询问）
  # 幂等检查：path_map.txt 已存在且数据类 5 项目录完整（非 FILL_ME 非空）→ 跳过交互
  $dataKeys = @("<资料目录>", "<3GPP文档库目录>", "<项目目录>", "<源码目录>", "<离线安装包目录>")
  $existingMap = @{}
  if (Test-Path $pathMapFile) {
    Get-Content $pathMapFile | ForEach-Object {
      if ($_ -match "^([^#=]+)=(.*)$") { $existingMap[$matches[1].Trim()] = $matches[2].Trim() }
    }
  }
  $dataComplete = $true
  foreach ($k in $dataKeys) {
    $v = $existingMap[$k]
    if (-not $v -or $v -eq "FILL_ME") { $dataComplete = $false; break }
  }
  if ($dataComplete) {
    Ok "检测到已配置的数据目录（path_map.txt 完整），跳过目录选择直接复用"
  } else {
  Write-Host ""
  Write-Host "  —— 数据目录配置（每项：直接回车=使用默认目录；输入路径=定制；已配置项回车保留原值）——" -ForegroundColor Cyan
  function Ask-Dir {
    param([string]$Label, [string]$DefaultDir)
    $existingVal = $existingMap[$Label]
    if ($existingVal -and $existingVal -ne "FILL_ME") {
      $ans = Read-Host "    $Label`n    已配置: $existingVal （回车保留，输入新路径=修改）"
      if ([string]::IsNullOrWhiteSpace($ans)) { return $existingVal }
      return $ans.Trim().TrimEnd("\")
    }
    $ans = Read-Host "    $Label`n    默认: $DefaultDir （回车使用默认）"
    if ([string]::IsNullOrWhiteSpace($ans)) {
      New-Item -ItemType Directory -Path $DefaultDir -Force | Out-Null
      return $DefaultDir
    }
    return $ans.Trim().TrimEnd("\")
  }
  $dBase = "D:\opencode"
  $docDir  = Ask-Dir "<资料目录>"          "$dBase\doc\default"
  $gppDir  = Ask-Dir "<3GPP文档库目录>"     "$dBase\doc\3gpp"
  $projDir = Ask-Dir "<项目目录>"           "$dBase\project\default"
  $srcDir  = Ask-Dir "<源码目录>"           "$dBase\code\default"
  $pkgDir  = Ask-Dir "<离线安装包目录>"     "$dBase\tool\default"

  $mapLines = @("# 路径映射（本机特定，不进仓库）：占位符=本机真实路径", "# 工具类自动探测；数据类为默认目录或用户定制")
  $mapLines += "<LibreOffice目录>=" + $loDir
  $mapLines += "<Chrome目录>=" + $chromeDir
  $mapLines += "<Node目录>=" + $nodeDir
  $mapLines += "<工具目录>=" + $toolDir
  $mapLines += "<WSL安装目录>=" + $wslDir
  $mapLines += "<资料目录>=" + $docDir
  $mapLines += "<3GPP文档库目录>=" + $gppDir
  $mapLines += "<项目目录>=" + $projDir
  $mapLines += "<源码目录>=" + $srcDir
  $mapLines += "<离线安装包目录>=" + $pkgDir
  [System.IO.File]::WriteAllLines($pathMapFile, $mapLines, (New-Object System.Text.UTF8Encoding($false)))

  Ok "工具类目录已自动探测（LibreOffice/Chrome/Node/工具/WSL）"
  Ok "数据类目录已配置（默认或定制）并写入 $pathMapFile"
  }

  # ---------- 7. 路径改写（占位符 → 新机真实路径，path_convert 体系） ----------
  if (-not $NoPathRewrite) {
    Step "7. 路径改写（占位符转换为新机真实路径）"
    $conv = Join-Path $RepoRoot "scripts\path_convert.py"
    $homeSlash = $env:USERPROFILE.Replace("\", "/")
    if (Test-Path $conv) {
      python $conv to_local --home="$homeSlash" $ConfigDir
      python $conv to_local --home="$homeSlash" $ToolDir
      # 填写类占位符检查：提醒用户补 path_map.txt
      $leftover = Get-ChildItem $ConfigDir -Recurse -File -Include "*.md","*.jsonc" -ErrorAction SilentlyContinue | Select-String -Pattern "<(项目|源码|WSL安装|离线安装包|工具|LibreOffice|Chrome|Node|3GPP文档库)目录>" -List -ErrorAction SilentlyContinue
      if ($leftover) {
        Warn "存在未配置的填写类占位符，请编辑 $ConfigDir\skills\update_skill\path_map.txt（每行：占位符=本机真实路径）后重跑："
        Warn "  python $conv to_local --home=`"$homeSlash`" $ConfigDir"
      }
      # 自动类占位符残留检查
      $autoLeft = Get-ChildItem $ConfigDir -Recurse -File -Include "*.md","*.jsonc" -ErrorAction SilentlyContinue | Select-String -Pattern "<用户目录>|<opencode配置目录>|<用户临时目录>" -List -ErrorAction SilentlyContinue
      if ($autoLeft) { Warn "仍有自动类占位符未转换，请检查 python 是否可用" } else { Ok "路径改写完成（占位符已转换为新机路径）" }
    } else { Warn "path_convert.py 不存在（scripts 目录缺失），跳过路径改写" }
  } else { Warn "已跳过路径改写（-NoPathRewrite）" }

# ---------- 5.5 规则注入验证 ----------
# ---------- 7.5 规则注入验证（语言跟随/输出规则依赖 instructions.md 生效） ----------
  Step "7.5 验证全局规则注入"
  $okJson = (Test-Path (Join-Path $ConfigDir "opencode.jsonc")) -and (Select-String -Path (Join-Path $ConfigDir "opencode.jsonc") -Pattern "instructions" -Quiet)
  $okMd = Test-Path (Join-Path $ConfigDir "instructions.md")
  if ($okJson -and $okMd) {
    Ok "opencode.jsonc 已注册 instructions.md，规则文件已部署"
  } else {
    Warn "规则注入缺失！请确认 $ConfigDir 下有 opencode.jsonc（含 instructions 注册）与 instructions.md"
  }
  Write-Host "  语言规则验证：重启 opencode 后，用中文提问，回答应为中文；若仍为英文，说明 instructions 未加载" -ForegroundColor Yellow
# ---------- 8. 汇总验证 ----------
Step "8. 验证汇总"

# 若 LibreOffice 已安装但 soffice 不在 PATH，自动加入用户 PATH
if (Test-Soffice -and -not (Test-Cmd "soffice")) {
  $soDir = $null
  foreach ($p in @("C:\Program Files\LibreOffice\program","C:\Program Files (x86)\LibreOffice\program")) {
    if (Test-Path (Join-Path $p "soffice.exe")) { $soDir = $p; break }
  }
  if ($soDir -and (Add-ToUserPath $soDir)) { Ok "已将 LibreOffice program 目录加入用户 PATH：$soDir（新开终端生效）" }
}

$checks = @(
  @{ name = "opencode CLI";    ok = (Test-Cmd "opencode") },
  @{ name = "mmdc";            ok = (Test-Cmd "mmdc") },
  @{ name = "python";          ok = (Test-Cmd "python") },
  @{ name = "p2t";             ok = (Test-Cmd "p2t") },
  @{ name = "git";             ok = (Test-Cmd "git") },
  @{ name = "soffice";         ok = (Test-Soffice) },
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
