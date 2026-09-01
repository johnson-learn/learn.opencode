# -*- coding: utf-8 -*-
# setup 安装核心逻辑独立模块：setup-windows.ps1 引用 + 测试 mock 模拟共用同一份代码
# 2026-08-28 单一工作窗口模式（用户定）：只弹出一个窗口，后续所有工具的下载安装全在此窗口进行

# ---------- 单一工作窗口（Worker） ----------
$script:workerProc = $null
$script:workerCmdFile = Join-Path $env:TEMP "opencode_worker_cmd.txt"
$script:workerScript = Join-Path $env:TEMP "opencode_worker.ps1"
$script:workerStopFile = Join-Path $env:TEMP "opencode_worker_stop.txt"

function Start-WorkerCommand([string]$cmd) {
  # 首次调用：生成 worker 循环脚本 + 弹出工作窗口（全程只弹这一次）
  if (-not $script:workerProc -or $script:workerProc.HasExited) {
    # 清理上一轮残留的 stop 信号，防新 worker 一启动即误退出
    Remove-Item $script:workerStopFile -Force -ErrorAction SilentlyContinue
    # 命令文件路径直接内嵌进 worker 脚本（2026-08-28 实测：-Verb RunAs 提权进程不继承主进程
    # 运行时设置的环境变量，$env:WORKER_CMD 为空导致 Test-Path 空值刷屏——内嵌后无环境依赖）
    $doneFile = $script:workerCmdFile + ".done"
    $loop = @"
`$f = '$($script:workerCmdFile)'
`$doneF = '$doneFile'
`$stopF = '$($script:workerStopFile)'
while (`$true) {
  # stop 信号自毁（2026-08-28 实测修复：worker 为提权进程，主窗口非管理员时
  # Stop-Process 杀不掉致窗口残留——worker 轮询到信号自行 exit 关窗，不依赖主窗口权限）
  if (Test-Path `$stopF) { exit }
  if (Test-Path `$f) {
    `$c = Get-Content `$f -Raw -ErrorAction SilentlyContinue
    Remove-Item `$f -Force -ErrorAction SilentlyContinue
    if (`$c -and `$c.Trim()) {
      try { iex `$c } catch { Write-Host ("[工作窗口] 命令执行失败：" + `$_.Exception.Message) }
      if (`$LASTEXITCODE -ne `$null -and `$LASTEXITCODE -ne 0) {
        Write-Host ("[工作窗口] 命令退出码 " + `$LASTEXITCODE + "（可能失败：权限不足/安装包异常，见 REQUIREMENTS.md）")
      }
      # 完成信号（2026-08-28 用户要求：新窗口安装完提醒主窗口）——写信号文件由主窗口轮询读取
      Set-Content -LiteralPath `$doneF -Value ("done exit=" + `$LASTEXITCODE) -Encoding UTF8
      `$global:LASTEXITCODE = `$null
    }
  }
  Start-Sleep -Milliseconds 400
}
"@
    Set-Content -LiteralPath $script:workerScript -Value $loop -Encoding UTF8
    # 管理员化工作窗口（2026-08-28 实测：普通权限 msiexec 装 Program Files 静默失败致"一直没反应"）：
    # -Verb RunAs 弹 UAC 一次（请点『是』），此后 winget/curl/msiexec 全部有权限；
    # 无 -NoExit：脚本 exit 后窗口自动关闭（配合 stop 信号不留残留窗口）
    $script:workerProc = Start-Process powershell -Verb RunAs -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $script:workerScript) -PassThru
    Write-Host "    [工作窗口] 已弹出（管理员权限，UAC 请点『是』；后续所有工具的下载安装都在此窗口进行）"
  }
  # 原子写命令文件（临时文件 + Move 替换，防 worker 读到半截文件）
  $tmpFile = $script:workerCmdFile + ".tmp"
  Set-Content -LiteralPath $tmpFile -Value $cmd -Encoding UTF8
  Move-Item -LiteralPath $tmpFile -Destination $script:workerCmdFile -Force
}

function Stop-WorkerWindow {
  if (-not $script:workerProc) { return }
  # 写 stop 信号并等待 worker 自行退出。worker 可能正在执行长命令（winget/下载），
  # 要等命令结束后才轮询到信号——故 stop 文件不能过早删除，需等 HasExited
  # 或兜底 Stop-Process 杀掉后才清理（2026-08-28 方案一修复竞态）
  Set-Content -LiteralPath $script:workerStopFile -Value "stop" -Encoding UTF8 -ErrorAction SilentlyContinue
  $waitedMs = 0
  while ($waitedMs -lt 12000) {
    $script:workerProc.Refresh()
    if ($script:workerProc.HasExited) { break }
    Start-Sleep -Milliseconds 500
    $waitedMs += 500
  }
  if (-not $script:workerProc.HasExited) {
    try { Stop-Process -Id $script:workerProc.Id -Force -ErrorAction SilentlyContinue } catch {}
  }
  Remove-Item $script:workerStopFile -Force -ErrorAction SilentlyContinue
  $script:workerProc = $null
}

# ---------- 动态版本解析 ----------
function Get-DynamicVersions {
  # 动态版本解析（2026-08-28 用户要求全部动态化：从镜像目录页解析最新可用版本，
  # 防镜像站清理历史版本致固定版本 404；解析失败回退固定版本兜底）
  $gitVer = $null; $nodeVer = $null; $pyVer = $null; $loVer = $null; $tesVer = $null
  try {
    $gitList = curl.exe -s --connect-timeout 15 "https://registry.npmmirror.com/-/binary/git-for-windows/" | ConvertFrom-Json
    $gitVer = $gitList | Where-Object { $_ -match '^v\d+\.\d+\.\d+\.windows\.1/$' } | ForEach-Object { $_.Trim('/').TrimStart('v') } | Sort-Object { [version]($_ -replace '\.windows\.1$', '') } -Descending | Select-Object -First 1
  } catch {}
  try {
    $nodeList = curl.exe -s --connect-timeout 15 "https://registry.npmmirror.com/-/binary/node/" | ConvertFrom-Json
    $nodeVer = $nodeList | Where-Object { $_ -match '^v\d+\.\d+\.\d+/$' } | ForEach-Object { $_.Trim('/').TrimStart('v') } | Where-Object { ([int](($_ -split '\.')[0])) % 2 -eq 0 } | Sort-Object { [version]$_ } -Descending | Select-Object -First 1
  } catch {}
  try {
    $pyList = curl.exe -s --connect-timeout 15 "https://registry.npmmirror.com/-/binary/python/" | ConvertFrom-Json
    $pyVer = $pyList | Where-Object { $_ -match '^3\.12\.\d+/$' } | ForEach-Object { $_.Trim('/') } | Sort-Object { [version]$_ } -Descending | Select-Object -First 1
  } catch {}
  try {
    $loIdx = curl.exe -s --connect-timeout 15 "https://mirrors.tuna.tsinghua.edu.cn/libreoffice/libreoffice/stable/"
    $loVer = [regex]::Matches($loIdx, 'href="(\d+\.\d+\.\d+)/"') | ForEach-Object { $_.Groups[1].Value } | Sort-Object { [version]$_ } -Descending | Select-Object -First 1
  } catch {}
  try {
    # Tesseract（UB-Mannheim GitHub release）：GitHub API 经 gh-proxy 代理（直连可能被墙）
    $tesApi = curl.exe -s --connect-timeout 15 "https://gh-proxy.com/https://api.github.com/repos/UB-Mannheim/tesseract/releases/latest" | ConvertFrom-Json
    $tesVer = ($tesApi.tag_name -replace '^v', '')
    if (-not $tesVer -or $tesVer -notmatch '^\d+\.\d+\.\d+$') { $tesVer = $null }
  } catch {}
  if (-not $gitVer) { $gitVer = "2.45.2.windows.1" }
  if (-not $nodeVer) { $nodeVer = "20.15.1" }
  if (-not $pyVer) { $pyVer = "3.12.4" }
  if (-not $loVer) { $loVer = "24.8.0" }
  if (-not $tesVer) { $tesVer = "5.4.0" }
  return @{ git = $gitVer; node = $nodeVer; py = $pyVer; lo = $loVer; tes = $tesVer }
}

# ---------- 同步镜像安装（主循环不用；保留供模拟测试与备用） ----------
function Install-FromMirror($p) {
  $idx = 0
  foreach ($url in $p.mirrors) {
    $idx++
    try {
      $ext = [System.IO.Path]::GetExtension($url).ToLower()
      $dl = Join-Path $env:TEMP ("opencode_dl_" + ($p.id -replace "[^A-Za-z0-9]", "_") + "_$idx" + $ext)
      Write-Host "    镜像源 $idx/$($p.mirrors.Count) 下载中：$url"
      curl.exe -L --connect-timeout 20 -o $dl $url
      if (-not (Test-Path $dl) -or (Get-Item $dl).Length -lt 1MB) {
        Write-Host "    该源下载失败或文件异常（大小 <1MB），换下一个源..."
        Remove-Item $dl -ErrorAction SilentlyContinue
        continue
      }
      Write-Host "    下载完成，静默安装中（$($p.name)；若提示权限不足请以管理员身份运行本脚本）..."
      if ($ext -eq ".msi") {
        Start-Process msiexec -ArgumentList @("/i", "`"$dl`"", "/qn", "/norestart") -Wait | Out-Null
      } else {
        Start-Process $dl -ArgumentList $p.silent -Wait | Out-Null
      }
      Start-Sleep -Seconds 5
      if (& $p.check) { return $true }
      Write-Host "    该源安装完成但未检测到（可能权限不足或安装失败），换下一个源..."
    } catch {
      Write-Host "    该源安装异常，换下一个源..."
    }
  }
  return $false
}
