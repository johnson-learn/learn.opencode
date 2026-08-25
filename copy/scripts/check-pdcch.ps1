# PDCCH 计算器 CDP 校验：模拟点击并核对数值
$chrome = "<Chrome目录>\chrome.exe"
$port = 9245
$tmp = "<用户临时目录>\opencode\chrome-pdcch"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
$proc = Start-Process $chrome -ArgumentList "--headless=new","--disable-gpu","--remote-debugging-port=$port","--user-data-dir=$tmp","about:blank" -PassThru
Start-Sleep -Seconds 2

function Send-CDP([string]$method, [string]$paramsJson) {
  $body = "{`"id`":1,`"method`":`"$method`",`"params`":$paramsJson}"
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
  $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
  $script:ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
  $buf = New-Object byte[] 262144
  $rseg = New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)
  $out = New-Object System.Collections.Generic.List[byte]
  do { $res = $ws.ReceiveAsync($rseg, [Threading.CancellationToken]::None).Result; for ($i=0; $i -lt $res.Count; $i++) { $out.Add($buf[$i]) } } while (-not $res.EndOfMessage)
  return ([System.Text.Encoding]::UTF8.GetString($out.ToArray()) | ConvertFrom-Json)
}
function Eval([string]$expr) {
  $p = "{`"expression`":`"$($expr -replace '\\','\\\\' -replace '"','\\"')`",`"returnByValue`":true}"
  $r = Send-CDP "Runtime.evaluate" $p
  if ($r.result.result.value) { return $r.result.result.value.ToString() } else { return "(no value)" }
}

$files = @(
  "file:///<3GPP文档库目录>/PDCCH-02-CORESET资源结构.html",
  "file:///<3GPP文档库目录>/PDCCH-04-盲检与哈希公式.html",
  "file:///<3GPP文档库目录>/PDCCH-08-练习册与计算器.html"
)
foreach ($f in $files) {
  $t = Invoke-RestMethod -Method Put "http://127.0.0.1:$port/json/new?$([uri]::EscapeDataString($f))"
  Start-Sleep -Seconds 3
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $ws.ConnectAsync([uri]$t.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
  Write-Output "=== $([System.IO.Path]::GetFileName($f)) ==="
  if ($f -like "*PDCCH-02*") {
    Write-Output ("ccalc: " + (Eval "(function(){document.getElementById('rbN').value=48;document.getElementById('symN').value=2;ccalc();return document.getElementById('cOut').innerHTML;})()"))
  } elseif ($f -like "*PDCCH-04*") {
    Write-Output ("hcalc: " + (Eval "(function(){document.getElementById('hAp').value=39829;document.getElementById('hY').value=100;hcalc();return document.getElementById('hOut').innerHTML;})()"))
    Write-Output ("bcalc: " + (Eval "(function(){document.getElementById('bNc').value=16;document.getElementById('bL').value=4;document.getElementById('bM').value=4;document.getElementById('bCi').value=0;document.getElementById('bY').value=0;bcalc();return document.getElementById('bOut').innerHTML.replace(/\n/g,' | ').substring(0,200);})()"))
  } else {
    Write-Output ("ccalc: " + (Eval "(function(){document.getElementById('cRb').value=48;document.getElementById('cSy').value=2;ccalc();return document.getElementById('cOut').innerHTML;})()"))
    Write-Output ("hstep: " + (Eval "(function(){document.getElementById('cAp').value=39829;document.getElementById('cYv').value=100;hstep();return document.getElementById('cYOut').innerHTML;})()"))
    Write-Output ("bcand: " + (Eval "(function(){document.getElementById('cNc').value=16;document.getElementById('cLv').value=4;document.getElementById('cMs').value=4;document.getElementById('cCi').value=0;document.getElementById('cYp').value=0;bcand();return document.getElementById('cBOut').innerHTML.replace(/\n/g,' | ').substring(0,200);})()"))
  }
  $ws.Dispose()
}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue