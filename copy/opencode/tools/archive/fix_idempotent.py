# -*- coding: utf-8 -*-
# setup 6.5 步增加幂等：path_map.txt 已存在且数据类完整则跳过交互直接复用
p = "/home/github/learn.opencode/copy/setup/setup-windows.ps1"
with open(p, encoding="utf-8") as f:
    c = f.read()

anchor = "  Write-Host \"\""
old_head = '''  # 生成 path_map.txt：工具类自动探测；数据类交互选择（默认目录 / 用户定制）
  Write-Host ""
  Write-Host "  —— 数据目录配置（每项：直接回车=使用默认目录；输入路径=定制）——" -ForegroundColor Cyan
  function Ask-Dir {'''

new_head = '''  # 生成 path_map.txt：工具类自动探测；数据类交互选择（幂等：已配置过则直接复用，不重复询问）
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
  function Ask-Dir {'''

if old_head not in c:
    print("旧块未找到")
    raise SystemExit(1)
c = c.replace(old_head, new_head, 1)

# Ask-Dir 支持"已配置项回车保留原值"：函数增加 Existing 参数
old_fn = '''    param([string]$Label, [string]$DefaultDir)
    $ans = Read-Host "    $Label`n    默认: $DefaultDir （回车使用默认）"
    if ([string]::IsNullOrWhiteSpace($ans)) {
      New-Item -ItemType Directory -Path $DefaultDir -Force | Out-Null
      return $DefaultDir
    }
    return $ans.Trim().TrimEnd("\\")
  }'''
new_fn = '''    param([string]$Label, [string]$DefaultDir)
    $existingVal = $existingMap[$Label]
    if ($existingVal -and $existingVal -ne "FILL_ME") {
      $ans = Read-Host "    $Label`n    已配置: $existingVal （回车保留，输入新路径=修改）"
      if ([string]::IsNullOrWhiteSpace($ans)) { return $existingVal }
      return $ans.Trim().TrimEnd("\\")
    }
    $ans = Read-Host "    $Label`n    默认: $DefaultDir （回车使用默认）"
    if ([string]::IsNullOrWhiteSpace($ans)) {
      New-Item -ItemType Directory -Path $DefaultDir -Force | Out-Null
      return $DefaultDir
    }
    return $ans.Trim().TrimEnd("\\")
  }'''
if old_fn not in c:
    print("Ask-Dir 旧函数未找到")
    raise SystemExit(1)
c = c.replace(old_fn, new_fn, 1)

# 闭合 else 块：找到数据类写入后的 Ok 行，在其后补右花括号
old_tail = '''  Ok "工具类目录已自动探测（LibreOffice/Chrome/Node/工具/WSL）"
  Ok "数据类目录已配置（默认或定制）并写入 $pathMapFile"'''
new_tail = '''  Ok "工具类目录已自动探测（LibreOffice/Chrome/Node/工具/WSL）"
  Ok "数据类目录已配置（默认或定制）并写入 $pathMapFile"
  }'''
if old_tail not in c:
    print("尾部 Ok 未找到")
    raise SystemExit(1)
c = c.replace(old_tail, new_tail, 1)

with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(c)
print("幂等检查已写入（已配置则跳过询问、已配置项回车保留原值）")
