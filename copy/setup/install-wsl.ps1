# ============================================================
# install-wsl.ps1 — WSL2 + Ubuntu 22.04 自动安装（需管理员权限）
# 用法：右键"使用 PowerShell 运行"（UAC 弹窗确认），或：
#       Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','install-wsl.ps1'
# 注意：启用功能后通常需要重启一次；脚本会在重启前给出提示。
# ============================================================
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function IsAdmin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $p = New-Object Security.Principal.WindowsPrincipal($id)
  return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}
if (-not (IsAdmin)) {
  Write-Host "[失败] 需要管理员权限。请右键以管理员身份运行。" -ForegroundColor Red
  exit 1
}

Write-Host "=== 1. 启用 Windows 功能（WSL + 虚拟机平台）===" -ForegroundColor Cyan
dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

$needReboot = $false
Write-Host "=== 2. 更新 WSL 内核并设置默认版本 2 ===" -ForegroundColor Cyan
try {
  wsl --update 2>&1 | Out-Null
  wsl --set-default-version 2
  Write-Host "  WSL2 默认版本已设置"
} catch {
  $needReboot = $true
  Write-Host "  WSL 内核需重启后生效" -ForegroundColor Yellow
}

Write-Host "=== 3. 安装 Ubuntu 22.04 ===" -ForegroundColor Cyan
$existing = wsl -l -v 2>&1
if ($existing -match "Ubuntu-22.04") {
  Write-Host "  Ubuntu-22.04 已安装，跳过"
} else {
  Write-Host "  尝试在线安装（微软商店渠道）..."
  wsl --install -d Ubuntu-22.04 2>&1 | Out-Null
  Start-Sleep -Seconds 3
  $after = wsl -l -v 2>&1
  if ($after -notmatch "Ubuntu-22.04") {
    Write-Host "  在线安装未完成，改用离线包下载安装（aka.ms/wslubuntu2204）..."
    $appx = Join-Path $env:TEMP "ubuntu2204.appx"
    curl.exe -L -o $appx "https://aka.ms/wslubuntu2204"
    if (Test-Path $appx -and (Get-Item $appx).Length -gt 1MB) {
      Add-AppxPackage $appx
      Write-Host "  appx 安装完成；请在开始菜单运行 Ubuntu 22.04 完成首次初始化"
    } else {
      Write-Host "  [失败] 离线包下载失败。请手动从可用电脑下载 https://aka.ms/wslubuntu2204 拷贝安装" -ForegroundColor Red
    }
  }
}

Write-Host "=== 4. Ubuntu 内初始化（编译工具链）===" -ForegroundColor Cyan
if (wsl -l -v 2>&1 | Select-String "Ubuntu-22.04") {
  wsl -d Ubuntu-22.04 -- bash -c "sudo apt update -y && sudo apt install -y build-essential git python3 curl && echo WSL-READY"
  Write-Host "  Ubuntu 初始化完成（build-essential/git/python3/curl）"
}

Write-Host ""
Write-Host "安装流程结束。验证命令：wsl -l -v（应显示 Ubuntu-22.04 VERSION 2）" -ForegroundColor Cyan
if ($needReboot) { Write-Host "提示：请重启电脑后再运行 wsl --set-default-version 2" -ForegroundColor Yellow }
