# -*- coding: utf-8 -*-
# Ask-Dir 改为明确"两个选项"呈现：1=默认目录，2=用户自定义
p = "/home/github/learn.opencode/copy/setup/setup-windows.ps1"
with open(p, encoding="utf-8") as f:
    c = f.read()

old_fn = '''  function Ask-Dir {
    param([string]$Label, [string]$DefaultDir)
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

new_fn = '''  function Ask-Dir {
    param([string]$Label, [string]$DefaultDir)
    $existingVal = $existingMap[$Label]
    if ($existingVal -and $existingVal -ne "FILL_ME") {
      Write-Host "    $Label" -ForegroundColor White
      Write-Host "      已配置: $existingVal"
      $ans = Read-Host "      [1] 保留已配置目录   [2] 修改为自定义路径   (直接回车=1)"
      if ($ans -eq "2") {
        $newPath = Read-Host "      请输入自定义路径"
        if (-not [string]::IsNullOrWhiteSpace($newPath)) { return $newPath.Trim().TrimEnd("\\") }
      }
      return $existingVal
    }
    Write-Host "    $Label" -ForegroundColor White
    Write-Host "      [1] 默认目录: $DefaultDir"
    Write-Host "      [2] 自定义路径（自己填写）"
    $ans = Read-Host "      请选择 (1/2，直接回车=1)"
    if ($ans -eq "2") {
      $newPath = Read-Host "      请输入自定义路径"
      if (-not [string]::IsNullOrWhiteSpace($newPath)) { return $newPath.Trim().TrimEnd("\\") }
      # 选了 2 但没填 → 回退默认
    }
    New-Item -ItemType Directory -Path $DefaultDir -Force | Out-Null
    return $DefaultDir
  }'''

if old_fn not in c:
    print("旧 Ask-Dir 未找到")
    raise SystemExit(1)
c = c.replace(old_fn, new_fn, 1)
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(c)
print("Ask-Dir 已改为两选项呈现（1=默认 / 2=自定义填写）")
