# -*- coding: utf-8 -*-
# setup 安装核心逻辑独立模块：setup-windows.ps1 引用 + 测试 mock 模拟共用同一份代码
# 2026-08-28 单一工作窗口模式（用户定）：只弹出一个窗口，后续所有工具的下载安装全在此窗口进行

# ---------- 单一工作窗口（Worker） ----------
$script:workerProc = $null
$script:workerCmdFile = Join-Path $env:TEMP "opencode_worker_cmd.txt"
$script:workerScript = Join-Path $env:TEMP "opencode_worker.ps1"

function Start-WorkerCommand([string]$cmd) {
  # 首次调用：生成 worker 循环脚本 + 弹出工作窗口（全程只弹这一次）
  if (-not $script:workerProc -or $script:workerProc.HasExited) {
    $loop = @'
while ($true) {
  $f = $env:WORKER_CMD
  if (Test-Path $f) {
    $c = Get-Content $f -Raw -ErrorAction SilentlyContinue
    Remove-Item $f -Force -ErrorAction SilentlyContinue
    if ($c -and $c.Trim()) { iex $c }
  }
  Start-Sleep -Milliseconds 400
}
'@
    Set-Content -LiteralPath $script:workerScript -Value $loop -Encoding UTF8
    $env:WORKER_CMD = $script:workerCmdFile
    $script:workerProc = Start-Process powershell -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-NoExit", "-File", $script:workerScript) -PassThru
    Write-Host "    [工作窗口] 已弹出（后续所有工具的下载安装都在此窗口进行）"
  }
  # 写命令文件 → 工作窗口循环检测到即执行
  Set-Content -LiteralPath $script:workerCmdFile -Value $cmd -Encoding UTF8
}

function Stop-WorkerWindow {
  if ($script:workerProc -and -not $script:workerProc.HasExited) {
    try { Stop-Process -Id $script:workerProc.Id -Force -ErrorAction SilentlyContinue } catch {}
  }
  $script:workerProc = $null
}

# ---------- 动态版本解析 ----------
function Get-DynamicVersions {
  # 动态版本解析（2026-08-28 用户要求全部动态化：从镜像目录页解析最新可用版本，
  # 防镜像站清理历史版本致固定版本 404；解析失败回退固定版本兜底）
  $gitVer = $null; $nodeVer = $null; $pyVer = $null; $loVer = $null
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
  if (-not $gitVer) { $gitVer = "2.45.2.windows.1" }
  if (-not $nodeVer) { $nodeVer = "20.15.1" }
  if (-not $pyVer) { $pyVer = "3.12.4" }
  if (-not $loVer) { $loVer = "24.8.0" }
  return @{ git = $gitVer; node = $nodeVer; py = $pyVer; lo = $loVer }
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
