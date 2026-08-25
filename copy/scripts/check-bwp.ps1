# BWP HTML 校验脚本：用 Chrome headless 加载页面并捕获 JS 控制台错误
param([string]$file = $null)
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$dir = "C:\Users\job_p\Desktop\NR-f40"
$files = if ($file) { @(Join-Path $dir $file) } else { @(Get-ChildItem $dir -Filter "BWP-*.html" | Sort-Object Name | ForEach-Object { $_.FullName }) }
foreach ($f in $files) {
  $url = "file:///" + ($f -replace '\\','/')
  $out = & $chrome --headless=new --disable-gpu --no-first-run --enable-logging=stderr --v=0 --virtual-time-budget=6000 --dump-dom $url 2>&1 | Out-String
  $errs = @()
  if ($out -match 'Uncaught') { $errs += ($out -split "`n" | Where-Object { $_ -match 'Uncaught|SyntaxError|ReferenceError|TypeError' } | ForEach-Object { $_.Trim() } | Select-Object -First 5) }
  $hasCalc = $out -match 'RIV = |bitwidth|K = |T_BWPswitchDelay = |q='
  "{0}" -f [System.IO.Path]::GetFileName($f)
  if ($errs.Count -gt 0) { $errs | ForEach-Object { "  ERROR: $_" } } else { "  JS OK (no console errors)" }
  "  dump contains calc output test: $hasCalc"
}