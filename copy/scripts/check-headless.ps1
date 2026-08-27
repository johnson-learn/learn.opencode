param([string[]]$Files)
$chrome = "<Chrome目录>\chrome.exe"
foreach ($f in $Files) {
  $url = "file:///" + [System.IO.Path]::GetFullPath($f).Replace("\", "/")
  $errs = & $chrome --headless --disable-gpu --no-sandbox --virtual-time-budget=6000 --dump-dom $url 2>&1 | Where-Object { $_ -match "Uncaught|ERROR" -and $_ -notmatch "GCM|gpu|GPU|Fontconfig|dbus|DBus" }
  if ($errs) { Write-Output ("=== " + (Split-Path $f -Leaf) + " CONSOLE ERRORS ==="); $errs | Select-Object -First 10 }
  else { Write-Output ("=== " + (Split-Path $f -Leaf) + " console OK ===") }
}