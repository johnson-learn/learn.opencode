# -*- coding: utf-8 -*-
# setup 安装核心逻辑模拟测试（2026-08-28 用户要求：真模拟而非文本断言）
# mock curl.exe（目录页 JSON/HTML + 下载写文件）与 Start-Process（安装窗口），
# 实际执行 Install-FromMirror / Get-DynamicVersions 各分支验证流转
# 用法：powershell -NoProfile -File test_setup_sim.ps1 -FuncFile <setup-install-functions.ps1 路径>
param(
  [string]$FuncFile = "\\wsl.localhost\Ubuntu\home\github\learn.opencode\copy\setup\setup-install-functions.ps1"
)
$ErrorActionPreference = "Continue"
$pass = 0; $fail = 0
function Check([string]$name, [bool]$cond) {
  if ($cond) { $script:pass++; Write-Host "  [PASS] $name" }
  else { $script:fail++; Write-Host "  [FAIL] $name" }
}

if (-not (Test-Path $FuncFile)) { Write-Host "函数文件不存在: $FuncFile"; exit 2 }
# ---------- mock 状态 ----------
$script:mockCurlCalls = @()
$script:mockInstallCalls = @()
$script:mockInstalled = $false
$script:mockDlSmall = $false        # true=下载写小文件(<1MB 判失败)
$script:mockDlFail = $false         # true=curl 抛异常
$script:mockInstalledOnInstall = $true  # true=Start-Process 后 check 置真

function curl.exe {
  [CmdletBinding(PositionalBinding = $false)]
  param(
    [string]$o,
    [Parameter(ValueFromRemainingArguments = $true)] $rest
  )
  $script:mockCurlCalls += ,@($rest)
  if ($script:mockDlFail) { throw "mock curl 网络异常" }
  $url = ""
  $out = $o
  foreach ($x in $rest) { if ($x -match "^https?://") { $url = $x } }
  if ($out) {
    # 下载场景：写文件（mockDlSmall=小文件）
    $size = if ($script:mockDlSmall) { 100 } else { 2MB }
    [System.IO.File]::WriteAllBytes($out, (New-Object byte[] $size))
    return
  }
  # 目录页场景
  if ($url -like "*binary/node/*") { Write-Output '["v18.20.4/","v20.15.1/","v21.7.3/","v22.14.0/"]' }
  elseif ($url -like "*binary/python/*") { Write-Output '["3.12.4/","3.12.7/","3.13.1/"]' }
  elseif ($url -like "*git-for-windows/*") { Write-Output '["v2.45.2.windows.1/","v2.47.1.windows.1/"]' }
  elseif ($url -like "*libreoffice/stable/*") { Write-Output '<html><a href="24.8.0/">24.8.0</a> <a href="26.8.0/">26.8.0</a></html>' }
  elseif ($url -like "*api.github.com/repos/UB-Mannheim/tesseract*") { Write-Output '{"tag_name":"5.5.0"} ' }
  else { Write-Output "[]" }
}

function Start-Sleep { param([int]$Seconds, [int]$Milliseconds) }
$script:mockProcId = 1000
$script:mockStopCalls = 0
$script:mockTaskKillCalls = 0
$script:mockWindowCalls = 0
function taskkill {
  param([Parameter(ValueFromRemainingArguments = $true)] $rest)
  $script:mockTaskKillCalls++
}
function Start-Process {
  [CmdletBinding()]
  param(
    [string]$FilePath,
    [string]$Verb,
    [switch]$Wait,
    [string]$WindowStyle,
    [object]$ArgumentList,
    [switch]$PassThru,
    [Parameter(ValueFromRemainingArguments = $true)] $rest
  )
  $script:mockInstallCalls += ,@($rest)
  $script:mockProcId++
  if ($FilePath -eq "powershell") { $script:mockWindowCalls++ }
  if ($script:mockInstalledOnInstall) { $script:mockInstalled = $true }
  $obj = [pscustomobject]@{ Id = $script:mockProcId; HasExited = $false }
  $obj | Add-Member -MemberType ScriptMethod -Name Refresh -Value { }
  return $obj
}
function Stop-Process {
  param([int]$Id, [switch]$Force, [Parameter(ValueFromRemainingArguments = $true)] $rest)
  $script:mockStopCalls++
}

function Reset-Mock {
  $script:mockCurlCalls = @()
  $script:mockInstallCalls = @()
  $script:mockInstalled = $false
  $script:mockDlSmall = $false
  $script:mockDlFail = $false
  $script:mockInstalledOnInstall = $true
  $script:mockStopCalls = 0
  $script:mockTaskKillCalls = 0
  $script:mockWindowCalls = 0
}

. $FuncFile

# ---------- 场景 1：动态版本解析（正常 JSON/HTML 目录页） ----------
Write-Host "[场景1] 动态版本解析"
Reset-Mock
$v = Get-DynamicVersions
Check "Node 解析为最新 LTS 偶数版 22.14.0" ($v.node -eq "22.14.0")
Check "Python 解析为 3.12 系列最新 3.12.7" ($v.py -eq "3.12.7")
Check "Git 解析为最新 2.47.1.windows.1" ($v.git -eq "2.47.1.windows.1")
Check "LibreOffice 解析为 26.8.0" ($v.lo -eq "26.8.0")
Check "Tesseract 解析为 5.5.0（gh-proxy 代理 GitHub API）" ($v.tes -eq "5.5.0")

# ---------- 场景 2：解析失败兜底固定版本 ----------
Write-Host "[场景2] 解析失败兜底"
Reset-Mock
$script:mockDlFail = $true
$v = Get-DynamicVersions
Check "全失败时 Git 兜底 2.45.2.windows.1" ($v.git -eq "2.45.2.windows.1")
Check "全失败时 Node 兜底 20.15.1" ($v.node -eq "20.15.1")
Check "全失败时 LibreOffice 兜底 24.8.0" ($v.lo -eq "24.8.0")
Check "全失败时 Tesseract 兜底 5.4.0" ($v.tes -eq "5.4.0")
$script:mockDlFail = $false

# ---------- 场景 3：镜像渠道安装成功（下载+提权安装+检测通过） ----------
Write-Host "[场景3] 镜像渠道安装成功"
Reset-Mock
$p = @{ id = "Test.Tool"; name = "测试工具"; mirrors = @("https://mirror.example.com/tool-1.msi", "https://mirror.example.com/tool-2.msi"); silent = @("/qn") ; check = { $script:mockInstalled } }
$r = Install-FromMirror $p
Check "安装成功返回 true" $r
Check "只用了第 1 个源（成功即停）" ($script:mockCurlCalls.Count -eq 1)
Check "安装走 Start-Process（提权窗口）" ($script:mockInstallCalls.Count -ge 1)

# ---------- 场景 4：第 1 源下载 <1MB → 自动换第 2 源 ----------
Write-Host "[场景4] 小文件自动换源"
Reset-Mock
$script:mockDlSmall = $true
$p = @{ id = "Test.Tool"; name = "测试工具"; mirrors = @("https://mirror.example.com/tool-1.msi", "https://mirror.example.com/tool-2.msi"); silent = @("/qn"); check = { $script:mockInstalled } }
# 第 1 源小文件失败 → 第 2 源也小文件失败 → false；统计 curl 调用次数验证换源
$r = Install-FromMirror $p
Check "两源都小文件时返回 false" (-not $r)
Check "curl 被调用 2 次（逐源尝试）" ($script:mockCurlCalls.Count -eq 2)

# ---------- 场景 5：下载成功但安装后检测不到 → 换下一源 ----------
Write-Host "[场景5] 装完检测不到换源"
Reset-Mock
$script:mockInstalledOnInstall = $false   # Start-Process 后 mockInstalled 不置真
$p = @{ id = "Test.Tool"; name = "测试工具"; mirrors = @("https://mirror.example.com/tool-1.msi", "https://mirror.example.com/tool-2.msi"); silent = @("/qn"); check = { $script:mockInstalled } }
$r = Install-FromMirror $p
Check "全部源装完检测不到时返回 false" (-not $r)
Check "curl 被调用 2 次（逐源尝试）" ($script:mockCurlCalls.Count -eq 2)
Check "Start-Process 被调用 2 次（每源各装一次）" ($script:mockInstallCalls.Count -eq 2)

# ---------- 场景 6：第 1 源网络异常 → 自动换第 2 源成功 ----------
Write-Host "[场景6] 网络异常换源后成功"
Reset-Mock
$script:mockDlFail = $true
$p = @{ id = "Test.Tool"; name = "测试工具"; mirrors = @("https://mirror.example.com/tool-1.msi", "https://mirror.example.com/tool-2.msi"); silent = @("/qn"); check = { $script:mockInstalled } }
$r = Install-FromMirror $p
Check "全源网络异常返回 false" (-not $r)
Check "异常不中断（两次都尝试）" ($script:mockCurlCalls.Count -eq 2)
$script:mockDlFail = $false

# ---------- 场景 7：worker 窗口停止信号（2026-08-28 实测修复：提权窗口残留） ----------
Write-Host "[场景7] worker 停止信号自毁"
Reset-Mock
Start-WorkerCommand "echo A"
Start-WorkerCommand "echo B"
Check "首次命令生成 worker 循环脚本" (Test-Path (Join-Path $env:TEMP "opencode_worker.ps1"))
Check "worker 循环含 stop 信号自毁检查（提权窗口自行退出关窗）" ((Get-Content (Join-Path $env:TEMP "opencode_worker.ps1") -Raw) -match "stopF")
Check "worker 存续期间重复发命令只弹一次窗口（方案一：非退出场景不杀 worker）" ($script:mockWindowCalls -eq 1)
Stop-WorkerWindow
Check "停止时先写 stop 信号文件再兜底 Stop-Process" ($script:mockStopCalls -ge 1)

Write-Host ""
Write-Host "SIM_RESULT: pass=$pass fail=$fail"
if ($fail -gt 0) { exit 1 }
exit 0
