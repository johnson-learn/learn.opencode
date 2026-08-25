# PDCCH-06 校验 v2：CDP 加载页面，检查关键内容
$chrome = "<Chrome目录>\chrome.exe"
$port = 9252
$tmp = "<用户临时目录>\opencode\chrome-pdcch06b"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
$proc = Start-Process $chrome -ArgumentList "--headless=new","--disable-gpu","--remote-debugging-port=$port","--user-data-dir=$tmp","about:blank" -PassThru
Start-Sleep -Seconds 3

function Send-CDP([string]$method, [string]$paramsJson) {
  $body = "{`"id`":1,`"method`":`"$method`",`"params`":$paramsJson}"
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
  $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
  $script:ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
  for ($attempt = 0; $attempt -lt 20; $attempt++) {
    $buf = New-Object byte[] 524288
    $rseg = New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)
    $out = New-Object System.Collections.Generic.List[byte]
    do { $res = $ws.ReceiveAsync($rseg, [Threading.CancellationToken]::None).Result; for ($i=0; $i -lt $res.Count; $i++) { $out.Add($buf[$i]) } } while (-not $res.EndOfMessage)
    $txt = [System.Text.Encoding]::UTF8.GetString($out.ToArray())
    if ($txt -match '"id"') { return ($txt | ConvertFrom-Json) }
  }
  return $null
}
function Eval([string]$expr) {
  $p = "{`"expression`":`"$($expr -replace '\\','\\\\' -replace '"','\\"')`",`"returnByValue`":true}"
  $r = Send-CDP "Runtime.evaluate" $p
  if ($r -and $r.result -and $r.result.result -and $r.result.result.value -ne $null) { return $r.result.result.value.ToString() } else { return "(no value)" }
}

$f = "file:///<3GPP文档库目录>/PDCCH-06-配置链.html"
$t = Invoke-RestMethod -Method Put "http://127.0.0.1:$port/json/new?$([uri]::EscapeDataString($f))"
Start-Sleep -Seconds 4
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ws.ConnectAsync([uri]$t.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
$null = Send-CDP "Runtime.enable" "{}"
Start-Sleep -Milliseconds 300

$chk1 = Eval "document.title"
$chk2 = Eval "document.querySelectorAll('h2').length"
$chk3 = Eval "document.body.innerText.includes('2.5 四链对比')"
$chk4 = Eval "document.body.innerText.includes('链条3：专用公共链')"
$chk5 = Eval "document.body.innerText.includes('链 C 溯源结论')"
$chk6 = Eval "document.body.innerText.includes('2.4 链 D：专用专属链')"
$chk7 = Eval "document.querySelectorAll('table').length"
$chk8 = Eval "document.querySelectorAll('.chain pre').length"

Write-Output "title: $chk1"
Write-Output "h2数: $chk2 | table数: $chk7 | 溯源块数: $chk8"
Write-Output "2.5四链对比: $chk3 | 链条3总览: $chk4 | 链C溯源结论: $chk5 | 2.4链D: $chk6"
$ws.Dispose()
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue