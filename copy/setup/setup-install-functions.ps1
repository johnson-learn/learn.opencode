# -*- coding: utf-8 -*-
# setup 安装核心逻辑独立模块（2026-08-28 抽取）：setup-windows.ps1 引用 + 测试 mock 模拟共用同一份代码
# 依赖 mock 的外部命令：curl.exe（下载）、Start-Process（安装窗口）——测试中可重定义这两个做模拟

# 镜像直链第二渠道安装（2026-08-27 用户方案：winget 源国内经常不可达，镜像直链成功率更高；
# 2026-08-28 多源化：每工具多个安装源按序尝试，任一成功即完成）
# 逐个源：下载安装包 → 按扩展名区分静默安装方式（msi 走 msiexec，exe 直跑）→ 检测结果
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
      Write-Host "    下载完成，已新开管理员 PowerShell 窗口执行静默安装（如弹出 UAC 请点『是』；安装期间窗口可见）..."
      if ($ext -eq ".msi") {
        Start-Process powershell -Verb RunAs -ArgumentList @("-NoProfile", "-Command", "msiexec /i `"$dl`" /qn /norestart") | Out-Null
      } else {
        $silentArgs = ($p.silent -join " ")
        Start-Process powershell -Verb RunAs -ArgumentList @("-NoProfile", "-Command", "& `"$dl`" $silentArgs") | Out-Null
      }
      # 轮询检测安装完成（2026-08-28 防挂起：UAC 未确认时 -Wait 会无限等待；
      # 改为最长 5 分钟轮询，超时未检测到自动换下一源）
      for ($wi = 0; $wi -lt 60; $wi++) {
        if (& $p.check) { return $true }
        Start-Sleep -Seconds 5
      }
      Write-Host "    该源安装窗口超时未检测到（可能 UAC 未确认或安装失败），换下一个源..."
    } catch {
      Write-Host "    该源安装异常，换下一个源..."
    }
  }
  return $false
}

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


# 下载窗口（2026-08-28 状态机化：下载放新窗口可见进度，原窗口菜单始终可选）
function Start-DownloadWindow([string]$url, [string]$dl) {
  Start-Process powershell -ArgumentList @("-NoProfile", "-Command", "curl.exe -L --connect-timeout 20 -o `"$dl`" $url") | Out-Null
}

# 提权安装窗口（msi 走 msiexec /qn；exe 走 silent 参数；UAC 弹窗确认）
function Start-InstallWindow($p, [string]$dl) {
  $ext = [System.IO.Path]::GetExtension($dl).ToLower()
  if ($ext -eq ".msi") {
    Start-Process powershell -Verb RunAs -ArgumentList @("-NoProfile", "-Command", "msiexec /i `"$dl`" /qn /norestart") | Out-Null
  } else {
    $silentArgs = ($p.silent -join " ")
    Start-Process powershell -Verb RunAs -ArgumentList @("-NoProfile", "-Command", "& `"$dl`" $silentArgs") | Out-Null
  }
}
