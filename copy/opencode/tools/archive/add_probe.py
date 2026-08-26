# -*- coding: utf-8 -*-
# 在 setup-windows.ps1 第 6 步后插入"7.0 自动探测安装工具目录并生成 path_map.txt"
p = "/home/github/learn.opencode/copy/setup/setup-windows.ps1"
with open(p, encoding="utf-8") as f:
    c = f.read()

anchor = "  # ---------- 7. 路径改写（占位符 → 新机真实路径，path_convert 体系） ----------"
if anchor not in c:
    print("锚点未找到")
    raise SystemExit(1)

block = '''  # ---------- 6.5 自动探测安装工具目录并生成 path_map.txt ----------
  Step "6.5 自动探测工具安装目录（生成 path_map.txt）"
  $pathMapFile = Join-Path $ConfigDir "skills\\update_skill\\path_map.txt"
  New-Item -ItemType Directory -Path (Split-Path $pathMapFile) -Force | Out-Null

  # 探测函数：在候选目录中找标记文件，命中即返回目录
  function Find-AppDir {
    param([string[]]$Candidates, [string]$Marker)
    foreach ($p in $Candidates) {
      if ($p -and (Test-Path (Join-Path $p $Marker))) { return $p.TrimEnd("\\") }
    }
    return ""
  }

  $loDir = Find-AppDir @(
    "<工具目录>\Program Files\\LibreOffice",
    "<工具目录>\Program Files (x86)\\LibreOffice",
    "D:\\LibreOffice",
    "D:\\Program Files\\LibreOffice"
  ) "program\\soffice.com"
  if (-not $loDir -and (Test-Soffice)) {
    try { $loDir = (Split-Path -Parent (Split-Path -Parent (Get-Command soffice).Source)) } catch {}
  }

  $chromeDir = Find-AppDir @(
    "<工具目录>\Program Files\\Google\\Chrome\\Application",
    "<工具目录>\Program Files (x86)\\Google\\Chrome\\Application",
    "${env:LOCALAPPDATA}\\Google\\Chrome\\Application"
  ) "chrome.exe"

  $nodeDir = ""
  try { if (Test-Cmd "node") { $nodeDir = Split-Path -Parent (Get-Command node).Source } } catch {}

  # w64devkit：从 PATH 或常见盘符探测
  $toolDir = ""
  foreach ($p in @("<工具目录>\w64devkit", "D:\\w64devkit", "E:\\w64devkit")) {
    if (Test-Path (Join-Path $p "w64devkit\\bin\\gcc.exe")) { $toolDir = Split-Path $p; break }
  }

  # WSL 安装目录：从注册表 BasePath 探测
  $wslDir = ""
  foreach ($root in @("HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Lxss", "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Lxss")) {
    foreach ($k in (Get-ChildItem $root -ErrorAction SilentlyContinue)) {
      $bp = (Get-ItemProperty $k.PSPath -ErrorAction SilentlyContinue).BasePath
      if ($bp) { $wslDir = $bp; break }
    }
    if ($wslDir) { break }
  }

  # 生成 path_map.txt：工具类自动填入；数据类留占位提示用户填写
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
c = c.replace(anchor, block + anchor, 1)
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(c)
print("6.5 自动探测块已插入")
