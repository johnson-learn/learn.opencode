﻿# ============================================================
# setup-windows.ps1 — 新电脑一键配置脚本（2026-09-01 检测模式）
# 用途：根据本仓库迁移包，把全局 skill + 配置 + 辅助脚本部署到新电脑，
#       并检测全部依赖工具（只检测+修复配置，不自动安装，永不阻塞）。
# 用法：右键"使用 PowerShell 运行"，或在 PowerShell 中执行：
#       powershell -NoProfile -ExecutionPolicy Bypass -File setup-windows.ps1
# 工具安装：未装工具按提示手动安装，或运行 setup\install-tools.ps1 一键自动安装。
# 说明：本脚本不弹 UAC；install-tools.ps1 安装类操作需管理员权限。
# ============================================================
param(
  [switch]$SkipDeploy,      # 跳过 skill/配置/脚本部署
  [switch]$SkipWsl,         # 跳过 WSL 检测
  [switch]$UseChinaMirror,  # 提示语/配置修复使用国内镜像
  [switch]$NoPathRewrite    # 部署时不改写旧机路径（不推荐）
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $RepoRoot            # 脚本在 setup\ 下，仓库根是其上一级
$ConfigDir = Join-Path $env:USERPROFILE ".config\opencode"
$ToolDir = Join-Path $env:LOCALAPPDATA "Temp\opencode"   # skill 引用的脚本目录（与原机约定一致）

. (Join-Path $PSScriptRoot "setup-check.ps1")

# ---------- 0. 前置检查 ----------
Step "0. 前置检查"
  Write-Host "  建议：以管理员身份运行本脚本（安装机器级软件需要管理员权限，否则安装会失败并提示）" -ForegroundColor Yellow
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

# ---------- 1. 工具清单与检测（2026-09-01 用户改造：只检测+修复配置，不自动安装，永不阻塞） ----------
Step "1. 工具清单与检测（只检测与修复配置，不自动安装；未装工具提示后跳过，装好后重跑本脚本自动补配置）"
Write-Host ""
Write-Host "  ---- 工具清单 --------------------------------------------------" -ForegroundColor Cyan
Write-Host "  [必须] 缺失不影响基本使用（update_skill 双向同步除外）：" -ForegroundColor Yellow
Write-Host "    Git for Windows / Node.js LTS / Python 3.12 / opencode CLI / pip 常规包集 / WSL2+Ubuntu" -ForegroundColor White
Write-Host "  [可选] 使用过程中可随时安装（用到对应功能前装好即可）：" -ForegroundColor Yellow
Write-Host "    Google Chrome / LibreOffice / Tesseract OCR / mermaid-cli(mmdc) / playwright / weasyprint" -ForegroundColor White
Write-Host "  ------------------------------------------------------------------" -ForegroundColor Cyan
Write-Host ""

# 工具检测条目：已装 -> [OK]；已装但 PATH 未配置 -> 自动修复；未装 -> 提示（建议命令）+ 跳过
# 工具清单与检测函数 $checks1 / Test-ToolEntry 由 setup-check.ps1 共享模块提供
foreach ($t in $checks1) {
  if (Test-ToolEntry $t) {
    Ok "[$($t.tier)] $($t.name) 已安装"
    # 已装但命令不在 PATH -> 修复 PATH（安装位置在但 PATH 未配置的常见场景）
    if ($t.cmd -and $t.pathDir -and (Test-Path $t.pathDir) -and -not (Test-Cmd $t.cmd)) {
      if (Add-ToUserPath $t.pathDir) { Ok "    已修复 PATH：$($t.pathDir) 已加入用户 PATH（新开终端生效）" }
    }
  } else {
    Warn "[$($t.tier)] $($t.name) 未安装——请手动安装或使用大模型协助安装（建议命令：$($t.hint)）；或运行 setup\install-tools.ps1 一键自动安装"
    Warn "    装好后重跑本脚本即可自动补齐相关配置（已装项自动跳过）"
  }
}

# 已装但 PATH 未配置的修复刷新：当前会话立即生效
$machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$env:Path = ($machinePath + ";" + $userPath)

# ---------- 2. npm 全局包检测（不自动安装，缺失提示） ----------
Step "2. npm 全局包检测（opencode / mermaid-cli）"
if (-not (Test-Cmd "npm")) {
  Warn "npm 不可用（Node.js 未装或未刷新 PATH）。装好 Node 后重跑本脚本即可。"
} else {
  if ($UseChinaMirror) {
    npm config set registry https://registry.npmmirror.com
    Ok "npm 镜像源已持久化配置（registry.npmmirror.com，后续 npm 命令自动走国内源）"
  }
  $npmMissing = @()
  if (-not (Test-Cmd "opencode")) { $npmMissing += "opencode-ai" }
  if (-not (Test-Cmd "mmdc")) { $npmMissing += "@mermaid-js/mermaid-cli" }
  if ($npmMissing.Count -gt 0) {
    Warn "npm 全局包缺失：$($npmMissing -join '、')——请手动安装或使用大模型协助安装："
    Warn "  npm i -g $($npmMissing -join ' ')$(if ($UseChinaMirror) { ' --registry=https://registry.npmmirror.com' })"
    Warn "  装好后重跑本脚本即可自动补齐相关配置"
  } else { Ok "npm 全局包已齐（opencode / mermaid-cli）" }
}

# ---------- 3. pip 常规包集检测（不自动安装，缺失汇总提示） ----------
Step "3. pip 常规包集检测（tools-manifest B 类 19 包；playwright/weasyprint 已在第 1 节可选工具检测）"
if (-not (Test-Cmd "python")) {
  Warn "python 不可用（未装或未刷新 PATH）。装好 Python 后重跑本脚本即可。"
} else {
  # 识别 Microsoft Store 版 Python（路径含 WindowsApps，其 --user 目录极长，易触发 torch 安装失败）
  $pyExe = $null
  try { $pyExe = (python -c "import sys; print(sys.executable)" 2>$null).Trim() } catch {}
  if ($pyExe -and $pyExe -like "*WindowsApps*") {
    Warn "检测到 Microsoft Store 版 Python（$pyExe）。其用户目录路径过长，torch/pix2text 可能安装失败。建议用 winget 安装官方 Python 3.12 后重跑本脚本。"
  }
  if ($UseChinaMirror) {
    python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    Ok "pip 镜像源已持久化配置（清华源，后续 pip 命令自动走国内源）"
  }
  # import 检测表 $pyPkgs 由 setup-check.ps1 共享模块提供（与 tools-manifest B 类一致）
  $missingPkgs = @()
  foreach ($pp in $pyPkgs) {
    python -c "import $($pp.mod)" 2>$null
    if ($LASTEXITCODE -ne 0) { $missingPkgs += $pp.pkg }
  }
  if ($missingPkgs.Count -gt 0) {
    Warn "pip 常规包缺失 $($missingPkgs.Count) 个——请手动安装或使用大模型协助安装："
    Warn "  python -m pip install --upgrade --user $($missingPkgs -join ' ')$(if ($UseChinaMirror) { ' -i https://pypi.tuna.tsinghua.edu.cn/simple' })"
    Warn "  装好后重跑本脚本即可自动补齐相关配置"
  } else { Ok "pip 常规包集全部已安装（19/19）" }
  # 已装 Python 但 pip Scripts 不在 PATH -> 修复
  $scriptsDir = Get-PipScriptsDir
  if ($scriptsDir -and (Add-ToUserPath $scriptsDir)) {
    Ok "已将 pip Scripts 目录加入用户 PATH：$scriptsDir（新开终端生效）"
  }
  if (-not (Test-Cmd "p2t")) { Warn "p2t 命令仍未在 PATH（可手动加：$scriptsDir）" }
}

# ---------- 4. WSL2 + Ubuntu（检测+提示，不自动安装） ----------
if (-not $SkipWsl) {
  Step "4. WSL2 + Ubuntu 22.04（已在第 1 节检测；此处仅提示补救路径）"
  $wslOk = $false
  foreach ($root in @("HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss","HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Lxss")) {
    foreach ($k in (Get-ChildItem $root -ErrorAction SilentlyContinue)) {
      $dn = (Get-ItemProperty $k.PSPath -ErrorAction SilentlyContinue).DistributionName
      if ($dn -and $dn -match "Ubuntu") { $wslOk = $true; break }
    }
    if ($wslOk) { break }
  }
  if ($wslOk) { Ok "WSL Ubuntu 已就绪" }
  else {
    $installer = Join-Path $RepoRoot "setup\install-wsl.ps1"
    Warn "WSL2 + Ubuntu 未安装——请手动安装（右键管理员运行 setup\install-wsl.ps1，可能需重启一次）："
    Warn "  装好后重跑本脚本即可自动补齐相关配置"
  }
} else { Warn "已跳过 WSL 检测（-SkipWsl）" }

# ---------- 5. 部署 skill / 配置 / 脚本 ----------
if (-not $SkipDeploy) {
  Step "5. 部署全局 skill 与配置"
  $srcSkills = Join-Path $RepoRoot "opencode\skills"
  $dstSkills = Join-Path $ConfigDir "skills"
  if (-not (Test-Path $srcSkills)) { Warn "仓库内 opencode\skills 不存在，跳过" }
  else {
    New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    foreach ($f in @("opencode.jsonc","AGENTS.md","instructions.md","regedit.md","docs-sync.md","tools-manifest.md","package.json")) {
      $s = Join-Path $RepoRoot "opencode\$f"
      if (Test-Path $s) { Copy-Item $s $ConfigDir -Force }
    }
    # 部署 plugins\（skill-banner.js 等 opencode 插件）
    $srcPlugins = Join-Path $RepoRoot "opencode\plugins"
    if (Test-Path $srcPlugins) {
      New-Item -ItemType Directory -Path (Join-Path $ConfigDir "plugins") -Force | Out-Null
      robocopy $srcPlugins (Join-Path $ConfigDir "plugins") /E /NFL /NDL /NJH /NJS /NP | Out-Null
    }
    # 部署 tests\ 与 tools\（测试用例与修炼工具，框架运行与进化门禁所需）
    foreach ($sub in @("tests","tools")) {
      $srcSub = Join-Path $RepoRoot "opencode\$sub"
      if (Test-Path $srcSub) {
        New-Item -ItemType Directory -Path (Join-Path $ConfigDir $sub) -Force | Out-Null
        robocopy $srcSub (Join-Path $ConfigDir $sub) /E /NFL /NDL /NJH /NJS /NP | Out-Null
      }
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
}

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

  # w64devkit：从现有盘符动态探测（不硬编码盘符，防无该盘符机器 Join-Path 报错）
  # 注意：必须用独立变量名（$w64Dir），PowerShell 变量大小写不敏感——用 $toolDir 会覆盖
  # 第 24 行定义的 $ToolDir（辅助脚本目录），导致第 8 节"辅助脚本部署"误报缺失（2026-08-27 实测）
  $w64Dir = ""
  try {
    foreach ($d in @(Get-PSDrive -PSProvider FileSystem -ErrorAction SilentlyContinue | ForEach-Object { $_.Root })) {
      $cand = Join-Path $d "w64devkit"
      if (Test-Path (Join-Path $cand "w64devkit\bin\gcc.exe")) { $w64Dir = $d; break }
    }
  } catch {}

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
      Write-Host "    $Label" -ForegroundColor White
      Write-Host "      已配置: $existingVal"
      $ans = Read-Host "      [1] 保留已配置目录   [2] 修改为自定义路径   (直接回车=1)"
      if ($ans -eq "2") {
        $newPath = Read-Host "      请输入自定义路径"
        if (-not [string]::IsNullOrWhiteSpace($newPath)) { return $newPath.Trim().TrimEnd("\") }
      }
      return $existingVal
    }
    Write-Host "    $Label" -ForegroundColor White
    Write-Host "      [1] 默认目录: $DefaultDir"
    Write-Host "      [2] 自定义路径（自己填写）"
    $ans = Read-Host "      请选择 (1/2，直接回车=1)"
    if ($ans -eq "2") {
      $newPath = Read-Host "      请输入自定义路径"
      if (-not [string]::IsNullOrWhiteSpace($newPath)) { return $newPath.Trim().TrimEnd("\") }
      # 选了 2 但没填 → 回退默认
    }
    New-Item -ItemType Directory -Path $DefaultDir -Force | Out-Null
    return $DefaultDir
  }
  $dBase = "D:\opencode"
  $docDir  = Ask-Dir "<资料目录>"          "$dBase\doc\default"
  $gppDir  = Ask-Dir "<3GPP文档库目录>"     "$dBase\doc\3gpp"
  $projDir = Ask-Dir "<项目目录>"           "$dBase\project\default"
  $srcDir  = Ask-Dir "<源码目录>"           "$dBase\code\default"
  $pkgDir  = Ask-Dir "<离线安装包目录>"     "$dBase\tool\default"

  $mapLines = @("# 路径映射（本机特定，不进仓库）：占位符=本机真实路径", "# 工具类自动探测；数据类为默认目录或用户定制")
  # 工具类空值当场询问（2026-08-27 改进：安装时闭环，不留事后警告；跳过=不写空值行，装好工具重跑本脚本自动补齐）
  foreach ($tk in @(@("<LibreOffice目录>", $loDir), @("<Chrome目录>", $chromeDir), @("<Node目录>", $nodeDir), @("<WSL安装目录>", $wslDir))) {
    $tName = $tk[0]
    $tVal = $tk[1]
    if (-not $tVal) {
      Write-Host "    $tName 未自动探测到（对应工具可能未安装）"
      Write-Host "      [1] 回车跳过（不写入映射，装好工具后重跑本脚本自动补齐）"
      Write-Host "      [2] 手动输入路径"
      $tAns = Read-Host "      请选择 (1/2，直接回车=1)"
      if ($tAns -eq "2") { $tVal = (Read-Host "      请输入路径").Trim() }
    }
    if ($tVal) { $mapLines += "$tName=$tVal" }
  }
  # <工具目录> 语义 = 系统盘根（w64devkit/MSYS2 等便携工具的约定安装盘），
  # 任何机器安装后相同，自动写入无需询问（2026-08-28 修复：此前误绑 $w64Dir，
  # 未装 w64devkit 时映射缺失 → to_local 转 0 个文件 + <工具目录> 残留）
  $mapLines += "<工具目录>=" + $env:SystemDrive + "\"
  $mapLines += "<资料目录>=" + $docDir
  $mapLines += "<3GPP文档库目录>=" + $gppDir
  $mapLines += "<项目目录>=" + $projDir
  $mapLines += "<源码目录>=" + $srcDir
  $mapLines += "<离线安装包目录>=" + $pkgDir
  [System.IO.File]::WriteAllLines($pathMapFile, $mapLines, (New-Object System.Text.UTF8Encoding($false)))

  Ok "工具类目录已自动探测（未探测到的已询问：跳过或手动填写）"
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
      # 填写类占位符检查：提醒用户补 path_map.txt（排除 tests 目录——repo_face 镜像文件保留占位符是设计；
      # <工具目录> 归自动类（盘符根自动写入），不在此列）
      $leftover = Get-ChildItem $ConfigDir -Recurse -File -Include "*.md","*.jsonc" -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "\\tests\\" } | Select-String -Pattern "<(项目|源码|WSL安装|离线安装包|LibreOffice|Chrome|Node|3GPP文档库)目录>" -List -ErrorAction SilentlyContinue
      if ($leftover) {
        Warn "存在未配置的填写类占位符（对应工具未安装或路径未探测到）。装好工具后重跑本脚本即可自动补齐（已装项自动跳过）："
        Warn "  powershell.exe -NoProfile -ExecutionPolicy Bypass -File setup-windows.ps1"
      }
      # 自动类占位符残留检查（排除 tests 目录——repo_face 镜像文件保留占位符是设计；
      # 含 <工具目录>：2026-08-28 Johnson 机器实测——映射缺失时 to_local 转 0 文件却误报 OK）
      $autoLeft = Get-ChildItem $ConfigDir -Recurse -File -Include "*.md","*.jsonc" -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch "\\tests\\" } | Select-String -Pattern "<用户目录>|<opencode配置目录>|<用户临时目录>|<工具目录>" -List -ErrorAction SilentlyContinue
      if ($autoLeft) { Warn "仍有自动类占位符未转换，请检查 python 是否可用" } else { Ok "路径改写完成（占位符已转换为新机路径）" }
    } else { Warn "path_convert.py 不存在（scripts 目录缺失），跳过路径改写" }
  } else { Warn "已跳过路径改写（-NoPathRewrite）" }

# ---------- 7.5 规则注入验证（注册事件注入体系：skill-banner system.transform 直读 4 规则文件） ----------
  Step "7.5 验证全局规则注入"
  $okPlugin = (Test-Path (Join-Path $ConfigDir "plugins\skill-banner.js")) -and (Select-String -Path (Join-Path $ConfigDir "plugins\skill-banner.js") -Pattern "experimental.chat.system.transform" -Quiet)
  $okFiles = $true
  foreach ($f in @("instructions.md", "regedit.md", "docs-sync.md", "tools-manifest.md")) {
    if (-not (Test-Path (Join-Path $ConfigDir $f))) { $okFiles = $false }
  }
  if ($okPlugin -and $okFiles) {
    Ok "注册事件注入体系完整（skill-banner system.transform + 4 规则文件已部署）"
  } else {
    Warn "规则注入缺失！请确认 $ConfigDir 下有 plugins\skill-banner.js（注册 experimental.chat.system.transform）与 instructions/regedit/docs-sync/tools-manifest 四文件"
  }
  Write-Host "  语言规则验证：重启 opencode 后，用中文提问，回答应为中文；若仍为英文，说明规则未加载" -ForegroundColor Yellow
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
  @{ name = "Tesseract";       ok = (Test-Tesseract) },
  @{ name = "Chrome";          ok = (Test-Path "C:\Program Files\Google\Chrome\Application\chrome.exe") -or (Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe") },
  @{ name = "skills 部署";     ok = (Test-Path (Join-Path $ConfigDir "skills\3gpp_skill\SKILL.md")) },
  @{ name = "辅助脚本部署";    ok = (Test-Path (Join-Path $ToolDir "extract-docx.ps1")) }
)
foreach ($c in $checks) {
  if ($c.ok) { Ok $c.name } else { Warn "$($c.name) 缺失（见 REQUIREMENTS.md 手动补装）" }
}
# ---------- 8.5 必备工具缺失醒目告警（2026-08-27 其它电脑安装实测反馈：失败只打警告容易被忽略） ----------
$requiredMissing = @()
$optionalMissing = @()
foreach ($c in $checks) {
  if ($c.ok) { continue }
  if ($c.name -in @("opencode CLI", "python", "p2t", "git")) { $requiredMissing += $c.name }
  else { $optionalMissing += $c.name }
}
if ($requiredMissing.Count -gt 0) {
  Write-Host ""
  Write-Host "  ⚠ 必备工具缺失或安装失败（核心功能受影响）：$($requiredMissing -join '、')" -ForegroundColor Red
  Write-Host "  影响：opencode CLI=无法运行本框架；python=全部测试与脚本不可用；p2t=公式识别不可用；git=版本控制与同步不可用" -ForegroundColor Yellow
  Write-Host "  补救：工具装好后重跑本脚本自动补齐（已装项自动跳过）：" -ForegroundColor Yellow
  Write-Host "    powershell.exe -NoProfile -ExecutionPolicy Bypass -File setup-windows.ps1" -ForegroundColor Yellow
}
if ($optionalMissing.Count -gt 0) {
  Write-Host "  ℹ 可选工具缺失（不影响核心使用）：$($optionalMissing -join '、')（见 REQUIREMENTS.md 手动补装）" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "完成。请重启 opencode（或新开终端）使 skill 生效。" -ForegroundColor Cyan
Write-Host "提示：p2t 首次使用会自动下载模型（约 1~2 GB）；网络慢时执行：" -ForegroundColor Cyan
Write-Host '  $env:HF_ENDPOINT = "https://hf-mirror.com"' -ForegroundColor Cyan
if ($requiredMissing.Count -gt 0) { exit 1 }
