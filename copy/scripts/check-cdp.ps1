# 用 CDP 模拟点击计算器并读取输出，真正验证交互是否工作
param([string]$urlFile = "C:\Users\job_p\Desktop\NR-f40\BWP-08-练习册与计算器.html")
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$port = 9233
$tmp = "C:\Users\job_p\AppData\Local\Temp\opencode\chrome-tmp"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
$proc = Start-Process $chrome -ArgumentList "--headless=new","--disable-gpu","--remote-debugging-port=$port","--user-data-dir=$tmp","about:blank" -PassThru
Start-Sleep -Seconds 2

$url = "file:///" + ((Resolve-Path $urlFile).Path -replace '\\','/')
$target = Invoke-RestMethod -Method Put "http://127.0.0.1:$port/json/new?$([uri]::EscapeDataString($url))"
Start-Sleep -Seconds 3

$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ws.ConnectAsync([uri]$target.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()

function Send-CDP([int]$id, [string]$method, [string]$paramsJson) {
  $body = if ($paramsJson) { "{`"id`":$id,`"method`":`"$method`",`"params`":$paramsJson}" } else { "{`"id`":$id,`"method`":`"$method`"}" }
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
  $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
  $script:ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
  $buf = New-Object byte[] 262144
  $rseg = New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)
  $out = New-Object System.Collections.Generic.List[byte]
  do {
    $res = $ws.ReceiveAsync($rseg, [Threading.CancellationToken]::None).Result
    for ($i=0; $i -lt $res.Count; $i++) { $out.Add($buf[$i]) }
  } while (-not $res.EndOfMessage)
  $json = [System.Text.Encoding]::UTF8.GetString($out.ToArray())
  return $json | ConvertFrom-Json
}

function Eval([string]$expr) {
  $p = "{`"expression`":`"$($expr -replace '\\','\\\\' -replace '"','\\"')`",`"returnByValue`":true}"
  $r = Send-CDP 1 "Runtime.evaluate" $p
  if ($r.result.result.value) { return $r.result.result.value.ToString() } else { return "(no value)" }
}

Write-Output "=== $([System.IO.Path]::GetFileName($urlFile)) ==="
Write-Output ("enc : " + (Eval "(function(){document.getElementById('cS').value=100;document.getElementById('cL').value=48;enc();return document.getElementById('eo').innerHTML;})()"))
Write-Output ("dec : " + (Eval "(function(){document.getElementById('dR').value=13025;dec();return document.getElementById('doOut').innerHTML;})()"))
Write-Output ("bw  : " + (Eval "(function(){document.getElementById('nbw').value=3;bw();return document.getElementById('bwo').innerHTML;})()"))
Write-Output ("ra  : " + (Eval "(function(){document.getElementById('nrB').value=100;document.getElementById('pP').value=8;document.getElementById('raT').value='both';ra();return document.getElementById('rao').innerHTML;})()"))
Write-Output ("k   : " + (Eval "(function(){document.getElementById('kNi').value=48;document.getElementById('kNa').value=200;k();return document.getElementById('ko').innerHTML;})()"))
Write-Output ("dl  : " + (Eval "(function(){document.getElementById('mu').value=1;document.getElementById('tp').value=1;dl();return document.getElementById('dlo').innerHTML;})()"))
Write-Output ("dec2 : " + (Eval "(function(){document.getElementById('dR').value=34804;dec();return document.getElementById('doOut').innerHTML.replace(/<[^>]+>/g,'').substring(0,150);})()"))

$ws.Dispose()
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue