# 3GPP 文档文本提取脚本（.doc 二进制格式，通过 Word COM 提取）
param(
  [string]$src = "<3GPP文档库目录>",
  [string]$out = "<用户临时目录>\opencode\specs"
)
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try { $word.AutomationSecurity = 3 } catch {}
$results = @()
Get-ChildItem $src -Filter *.doc | ForEach-Object {
  $f = $_
  $txtPath = Join-Path $out "$($f.BaseName).txt"
  if (Test-Path $txtPath) { return }
  try {
    $doc = $word.Documents.Open($f.FullName, $false, $true)
    $text = $doc.Content.Text
    $doc.Close($false)
    [System.IO.File]::WriteAllText($txtPath, $text, (New-Object System.Text.UTF8Encoding($false)))
    $results += "$($f.Name) OK $((Get-Item $txtPath).Length) bytes"
  } catch {
    $results += "$($f.Name) FAILED: $($_.Exception.Message)"
  }
}
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
$results | ForEach-Object { Write-Output $_ }
Write-Output "DONE doc"