# -*- coding: utf-8 -*-
# 修改 setup-windows.ps1 6.5 步的数据类目录：改为"默认目录/用户定制"交互式选择
p = "/home/github/learn.opencode/copy/setup/setup-windows.ps1"
with open(p, encoding="utf-8") as f:
    c = f.read()

old = '''  # 生成 path_map.txt：工具类自动填入；数据类留占位提示用户填写
  $mapLines = @("# 路径映射（本机特定，不进仓库）：占位符=本机真实路径", "# 工具类已自动探测；数据类请手动填写")
  $mapLines += "<LibreOffice目录>=" + $loDir
  $mapLines += "<Chrome目录>=" + $chromeDir
  $mapLines += "<Node目录>=" + $nodeDir
  $mapLines += "<工具目录>=" + $toolDir
  $mapLines += "<WSL安装目录>=" + $wslDir
  $mapLines += "# 以下数据类目录请按本机实际填写（不填则相关 skill 使用占位符时会提示）"
  $mapLines += "<项目目录>=FILL_ME"
  $mapLines += "<源码目录>=FILL_ME"
  $mapLines += "<离线安装包目录>=FILL_ME"
  $mapLines += "<3GPP文档库目录>=FILL_ME"
  [System.IO.File]::WriteAllLines($pathMapFile, $mapLines, (New-Object System.Text.UTF8Encoding($false)))

  Ok "工具类目录已自动探测（LibreOffice/Chrome/Node/工具/WSL）"
  Warn "数据类目录（项目/源码/离线安装包/3GPP文档库）请在 $pathMapFile 中把 FILL_ME 改为实际路径"
'''

new = '''  # 生成 path_map.txt：工具类自动探测；数据类交互选择（默认目录 / 用户定制）
  Write-Host ""
  Write-Host "  —— 数据目录配置（每项：直接回车=使用默认目录；输入路径=定制）——" -ForegroundColor Cyan
  function Ask-Dir {
    param([string]$Label, [string]$DefaultDir)
    $ans = Read-Host "    $Label`n    默认: $DefaultDir （回车使用默认）"
    if ([string]::IsNullOrWhiteSpace($ans)) {
      New-Item -ItemType Directory -Path $DefaultDir -Force | Out-Null
      return $DefaultDir
    }
    return $ans.Trim().TrimEnd("\\")
  }
  $dBase = "D:\\opencode"
  $docDir  = Ask-Dir "<资料目录>"          "$dBase\\doc\\default"
  $gppDir  = Ask-Dir "<3GPP文档库目录>"     "$dBase\\doc\\3gpp"
  $projDir = Ask-Dir "<项目目录>"           "$dBase\\project\\default"
  $srcDir  = Ask-Dir "<源码目录>"           "$dBase\\code\\default"
  $pkgDir  = Ask-Dir "<离线安装包目录>"     "$dBase\\tool\\default"

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
'''

if old not in c:
    print("旧块未找到")
    raise SystemExit(1)
c = c.replace(old, new, 1)
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(c)
print("数据类目录交互选择已写入")
