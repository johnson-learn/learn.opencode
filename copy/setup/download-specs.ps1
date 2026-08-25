# ============================================================
# download-specs.ps1 — 下载 3GPP 文档库（38 系列 Rel-15 + 相关规范）
# 用途：为新电脑准备 3gpp_skill 的"教材"（docx 原始文档）。
# 源：3GPP FTP 官方存档 https://www.3gpp.org/ftp/Specs/archive/
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File download-specs.ps1 [-OutDir <目录>]
# 默认输出到脚本所在仓库根的 data\specs\
# ============================================================
param([string]$OutDir = "")
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $RepoRoot
if ($OutDir -eq "") { $OutDir = Join-Path $RepoRoot "data\specs" }
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

# 文档清单：规范号 = 版本目录（-f40 表示 15.4.0 系列）。下载 docx 格式（部分仅有 doc/zip）。
# 版本规则：3GPP 归档目录格式 38xxx\15.4.0 下的文件命名 38xxx-f40.docx / .doc / .zip
$specs = @(
  "38104","38133","38201","38202","38211","38212","38213","38214","38215",
  "38300","38304","38321","38322","38323","38331","37324",
  "38401","38410","38413","38415","38425","38473",
  "21900","23501","23502","24501","29274","29281","29502","29518","33501","29060","38533"
)
$rel = "15.4.0"
$base = "https://www.3gpp.org/ftp/Specs/archive"

Write-Host "下载目标目录：$OutDir" -ForegroundColor Cyan
$okCount = 0; $failCount = 0; $skipCount = 0

foreach ($s in $specs) {
  $series = $s.Substring(0, 2)
  $ver = $s.Substring(2, 3)
  # 版本目录名（如 38xxx/15.4.0；38533 为 15.4.0 分卷）
  $relDir = $rel
  $candidates = @()
  foreach ($ext in @(".docx", ".doc", ".zip")) {
    $candidates += "$base/${series}_series/${s}/${relDir}/${s}-f40${ext}"
  }
  # 先探测哪个存在（HEAD 请求太慢，直接按顺序尝试下载）
  $done = $false
  foreach ($u in $candidates) {
    $fname = Split-Path $u -Leaf
    $dest = Join-Path $OutDir $fname
    if (Test-Path $dest -and (Get-Item $dest).Length -gt 100KB) { $skipCount++; $done = $true; break }
    try {
      Write-Host "  下载 $fname ..."
      $ProgressPreference = "SilentlyContinue"
      curl.exe -L --retry 2 -f -o $dest $u 2>$null
      if ($LASTEXITCODE -eq 0 -and (Test-Path $dest) -and (Get-Item $dest).Length -gt 100KB) {
        $okCount++; $done = $true; break
      } else {
        Remove-Item $dest -Force -ErrorAction SilentlyContinue
      }
    } catch { }
  }
  if (-not $done) { $failCount++; Write-Host "  [失败] $s 未下载成功（检查 3GPP FTP 版本目录或网络）" -ForegroundColor Red }
}

Write-Host ""
Write-Host "完成：成功 $okCount，跳过(已存在) $skipCount，失败 $failCount" -ForegroundColor Cyan
Write-Host "后续步骤（生成纯文本索引，供 skill 检索）：" -ForegroundColor Cyan
Write-Host "  1) 用 scripts\extract-docx.ps1 / extract-doc.ps1 逐文档提取文本到 %LOCALAPPDATA%\Temp\opencode\specs\*.txt"
Write-Host "  2) 批量转 PDF（LibreOffice soffice）到 ssb-pdf\，供公式 p2t 核实"
