# ============================================================
# install-tools.ps1 — 工具一键自动安装脚本（2026-09-01 新增）
# 用途：自动安装 setup-windows.ps1 检测出的缺失工具（winget 渠道 + npm/pip），
#       每个工具独立安装、失败跳过继续（永不阻塞），收尾汇总失败清单。
# 用法：右键"使用 PowerShell 运行"，或：
#       powershell -NoProfile -ExecutionPolicy Bypass -File install-tools.ps1
#       powershell -NoProfile -ExecutionPolicy Bypass -File install-tools.ps1 -UseChinaMirror
# 说明：winget 安装机器级软件需管理员权限（UAC 自动弹窗）；全部静默安装；
#       装完后重跑 setup-windows.ps1 自动补齐相关配置（PATH/path_map/占位符等）。
# ============================================================
param(
  [switch]$UseChinaMirror,  # npm/pip 使用国内镜像（npmmirror/清华源）
  [switch]$SkipNpm,         # 跳过 npm 全局包安装
  [switch]$SkipPip          # 跳过 pip 包安装
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 共享检测模块：工具清单 $checks1、检测函数 Test-ToolEntry/Test-Soffice 等
. (Join-Path $PSScriptRoot "setup-check.ps1")

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
  Warn "建议以管理员身份运行本脚本（winget 安装机器级软件需要管理员权限，否则安装会失败并提示）"
}

# ---------- 1. 检测缺失工具 ----------
Step "1. 检测缺失工具（清单同 setup-windows.ps1；已装自动跳过）"
$missing = @()
foreach ($t in $checks1) {
  if (Test-ToolEntry $t) { Ok "[$($t.tier)] $($t.name) 已安装" }
  else { $missing += $t }
}
if ($missing.Count -eq 0) { Ok "全部工具已安装" } else { Write-Host "  缺失 $($missing.Count) 项，开始自动安装..." -ForegroundColor Yellow }

# ---------- 2. winget 渠道安装（每个独立、失败跳过继续） ----------
if ($missing.Count -gt 0) {
  Step "2. winget 渠道安装"
  if (-not (Test-Cmd "winget")) {
    Warn "winget 不存在——无法自动安装基础软件，请手动安装（见 REQUIREMENTS.md §1）或安装 App Installer"
  } else {
    foreach ($t in $missing) {
      if (-not $t.wingetId) { continue }   # 非 winget 渠道（npm/pip/手动）留给后续环节
      Write-Host "  安装 $($t.name)（winget --id $($t.wingetId)，静默；失败自动跳过继续）..."
      winget install --id $($t.wingetId) -e --silent --disable-interactivity --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
      Start-Sleep -Seconds 3
      if (Test-ToolEntry $t) {
        Ok "$($t.name) 安装完成"
        # 装好后若命令不在 PATH（winget 装的个别工具不进 PATH）→ 修复
        if ($t.cmd -and $t.pathDir -and (Test-Path $t.pathDir) -and -not (Test-Cmd $t.cmd)) {
          if (Add-ToUserPath $t.pathDir) { Ok "    已修复 PATH：$($t.pathDir) 已加入用户 PATH（新开终端生效）" }
        }
      } else {
        Warn "$($t.name) winget 安装未成功（可能缺管理员权限或网络问题）——请手动安装：$($t.hint)"
        if ($UseChinaMirror) { Warn "    国内网络可尝试 gh-proxy.com 镜像直链下载安装包（见 REQUIREMENTS.md）" }
      }
    }
  }
}

# ---------- 3. npm 全局包 ----------
if (-not $SkipNpm) {
  Step "3. npm 全局包"
  if (-not (Test-Cmd "npm")) {
    Warn "npm 不可用（Node.js 未装或安装未成功）。装好 Node 后重跑本脚本即可。"
  } else {
    if ($UseChinaMirror) {
      npm config set registry https://registry.npmmirror.com
      Ok "npm 镜像源已持久化配置（registry.npmmirror.com）"
    }
    $npmReg = if ($UseChinaMirror) { "--registry=https://registry.npmmirror.com" } else { "" }
    foreach ($t in $checks1) {
      if (-not $t.npmPkg) { continue }
      if (Test-ToolEntry $t) { Ok "$($t.name) 已安装"; continue }
      Write-Host "  npm i -g $($t.npmPkg) ..."
      npm i -g $t.npmPkg $npmReg
      if (Test-ToolEntry $t) { Ok "$($t.name) 安装完成" }
      else { Warn "$($t.name) 安装失败——请手动安装：$($t.hint)" }
    }
  }
} else { Warn "已跳过 npm 全局包（-SkipNpm）" }

# ---------- 4. pip 包 ----------
if (-not $SkipPip) {
  Step "4. pip 包（tools-manifest B 类 19 包 + 可选大件）"
  if (-not (Test-Cmd "python")) {
    Warn "python 不可用（未装或安装未成功）。装好 Python 后重跑本脚本即可。"
  } else {
    $pi = if ($UseChinaMirror) { "-i https://pypi.tuna.tsinghua.edu.cn/simple" } else { "" }
    if ($UseChinaMirror) {
      python -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
      Ok "pip 镜像源已持久化配置（清华源）"
    }
    $toInstall = @()
    foreach ($pp in $pyPkgs) {
      python -c "import $($pp.mod)" 2>$null
      if ($LASTEXITCODE -ne 0) { $toInstall += $pp.pkg }
    }
    foreach ($t in $checks1) {
      if ($t.pipPkg -and -not (Test-ToolEntry $t)) { $toInstall += $t.pipPkg }
    }
    if ($toInstall.Count -eq 0) { Ok "pip 包全部已安装" }
    else {
      Write-Host "  安装 $($toInstall.Count) 个缺失包（失败自动跳过继续）..."
      foreach ($pkg in $toInstall) {
        Write-Host "  pip install $pkg ..."
        python -m pip install --upgrade --user $pkg $pi
        if ($LASTEXITCODE -eq 0) { Ok "$pkg 安装完成" } else { Warn "$pkg 安装失败（可稍后手动补装）" }
      }
    }
    $scriptsDir = Get-PipScriptsDir
    if ($scriptsDir -and (Add-ToUserPath $scriptsDir)) {
      Ok "已将 pip Scripts 目录加入用户 PATH：$scriptsDir（新开终端生效）"
    }
  }
} else { Warn "已跳过 pip 包（-SkipPip）" }

# ---------- 4b. 可选大件依赖链（playwright chromium 内核 / weasyprint MSYS2+GTK3；失败仅警告不阻塞） ----------
Step "4b. 可选大件依赖链（playwright chromium 内核 / weasyprint MSYS2+GTK3）"
# playwright：pip 包已装时自动补 chromium 内核（约 300MB；-UseChinaMirror 走 npmmirror 镜像）
if (Test-Cmd "python") {
  python -c "import playwright" 2>$null
  if ($LASTEXITCODE -eq 0) {
    if ($UseChinaMirror) { $env:PLAYWRIGHT_DOWNLOAD_HOST = "https://npmmirror.com/mirrors/playwright" }
    Write-Host "  安装 playwright chromium 内核（约 300MB，失败仅警告）..."
    python -m playwright install chromium 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Ok "playwright chromium 内核安装完成" }
    else { Warn "playwright chromium 内核安装失败（可稍后手动：python -m playwright install chromium）" }
  }
}
# weasyprint：pip 包已装时自动补 MSYS2 + GTK3 + 环境变量
if (Test-Cmd "python") {
  python -c "import weasyprint" 2>$null
  if ($LASTEXITCODE -eq 0) {
    $msysRoot = "C:\msys64"
    $msysBash = Join-Path $msysRoot "usr\bin\bash.exe"
    $gtkDll = Join-Path $msysRoot "ucrt64\bin\libgtk-3-0.dll"
    if (-not (Test-Path $gtkDll)) {
      Write-Host "  安装 weasyprint 依赖：MSYS2 + GTK3（失败仅警告）..."
      if (-not (Test-Path $msysBash)) {
        if (Test-Cmd "winget") {
          winget install --id MSYS2.MSYS2 -e --silent --disable-interactivity --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
          $msysWait = 0
          while (-not (Test-Path $msysBash) -and $msysWait -lt 60) { Start-Sleep -Seconds 5; $msysWait++ }
        }
      }
      if (Test-Path $msysBash) {
        Write-Host "    MSYS2 pacman 安装 GTK3（首次需 keyring 初始化，最长约 10 分钟）..."
        & $msysBash -lc "pacman-key --init 2>/dev/null; pacman-key --populate msys2 2>/dev/null; pacman -Sy --noconfirm 2>/dev/null; pacman -S --noconfirm mingw-w64-ucrt-x86_64-gtk3" 2>&1 | Out-Null
        $gtkWait = 0
        while (-not (Test-Path $gtkDll) -and $gtkWait -lt 30) { Start-Sleep -Seconds 5; $gtkWait++ }
      }
    }
    if (Test-Path $gtkDll) {
      $msysBin = Join-Path $msysRoot "ucrt64\bin"
      $curEnv = [Environment]::GetEnvironmentVariable("WEASYPRINT_DLL_DIRECTORIES", "User")
      if (-not $curEnv -or ($curEnv -split ';' -notcontains $msysBin)) {
        [Environment]::SetEnvironmentVariable("WEASYPRINT_DLL_DIRECTORIES", $msysBin, "User")
        $env:WEASYPRINT_DLL_DIRECTORIES = $msysBin
        Ok "WEASYPRINT_DLL_DIRECTORIES 已持久化配置：$msysBin"
      } else { Ok "WEASYPRINT_DLL_DIRECTORIES 已配置：$msysBin" }
    } else {
      Warn "weasyprint 依赖 MSYS2 GTK3 未就绪（可手动：winget install MSYS2.MSYS2 后 pacman -S mingw-w64-ucrt-x86_64-gtk3，配环境变量 WEASYPRINT_DLL_DIRECTORIES=C:\msys64\ucrt64\bin）"
    }
  }
}

# ---------- 5. 汇总 ----------
Step "5. 安装汇总"
$stillMissing = @()
foreach ($t in $checks1) { if (-not (Test-ToolEntry $t)) { $stillMissing += $t } }
$stillPy = @()
if (Test-Cmd "python") {
  foreach ($pp in $pyPkgs) {
    python -c "import $($pp.mod)" 2>$null
    if ($LASTEXITCODE -ne 0) { $stillPy += $pp.pkg }
  }
}
if ($stillMissing.Count -eq 0 -and $stillPy.Count -eq 0) {
  Ok "全部工具安装完成！请重跑 setup-windows.ps1 补齐配置（PATH/path_map/占位符转换）："
  Write-Host "    powershell -NoProfile -ExecutionPolicy Bypass -File setup\setup-windows.ps1"
} else {
  Warn "仍有未装工具（完整安装方法与命令如下；按方法装好后重跑本脚本验证）："
  foreach ($t in $stillMissing) {
    Warn "  [$($t.tier)] $($t.name)"
    if ($t.guide) {
      Write-Host "    $($t.guide -replace '`n', "`n    ")" -ForegroundColor Gray
    }
  }
  if ($stillPy.Count -gt 0) { Warn "  pip 包：$($stillPy -join ' ')" }
  Write-Host ""
  Write-Host "  已装工具无需等待——现在即可重跑 setup-windows.ps1 补齐已装项的配置：" -ForegroundColor Cyan
  Write-Host "    powershell -NoProfile -ExecutionPolicy Bypass -File setup\setup-windows.ps1" -ForegroundColor Cyan
}
