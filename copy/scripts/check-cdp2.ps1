# 校验 BWP-02 与 BWP-05 的计算器（CDP 模拟点击）
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$port = 9234
$tmp = "<用户临时目录>\opencode\chrome-tmp2"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
$proc = Start-Process $chrome -ArgumentList "--headless=new","--disable-gpu","--remote-debugging-port=$port","--user-data-dir=$tmp","about:blank" -PassThru
Start-Sleep -Seconds 2

function New-Tab([string]$url) {
  return Invoke-RestMethod -Method Put "http://127.0.0.1:$port/json/new?$([uri]::EscapeDataString($url))"
}
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

$f2 = "file:///<用户桌面目录>/NR-f40/BWP-02-物理层定义与资源网格.html"
$f5 = "file:///<用户桌面目录>/NR-f40/BWP-05-DCI切换.html"

foreach ($f in @($f2,$f5)) {
  $t = New-Tab $f
  Start-Sleep -Seconds 3
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $ws.ConnectAsync([uri]$t.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
  Write-Output "=== $([System.IO.Path]::GetFileName($f)) ==="
  if ($f -like "*BWP-02*") {
    Write-Output ("enc: " + (Eval "(function(){document.getElementById('cS').value=100;document.getElementById('cL').value=48;doEnc();return document.getElementById('encOut2').innerHTML.replace(/<[^>]+>/g,'').substring(0,120);})()"))
    Write-Output ("dec: " + (Eval "(function(){document.getElementById('dR').value=34804;doDec();return document.getElementById('decOut2').innerHTML.replace(/<[^>]+>/g,'').substring(0,120);})()"))
  } else {
    Write-Output ("bw : " + (Eval "(function(){document.getElementById('nbw').value=3;doBw();return document.getElementById('bwOut').innerHTML.replace(/<[^>]+>/g,'').substring(0,120);})()"))
    Write-Output ("ra : " + (Eval "(function(){document.getElementById('nrB').value=100;document.getElementById('pP').value=8;document.getElementById('raT').value='both';doRa();return document.getElementById('raOut').innerHTML.replace(/<[^>]+>/g,'').substring(0,120);})()"))
    Write-Output ("k  : " + (Eval "(function(){document.getElementById('kNi').value=48;document.getElementById('kNa').value=200;doK();return document.getElementById('kOut').innerHTML.replace(/<[^>]+>/g,'').substring(0,120);})()"))
  }
  $ws.Dispose()
}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue