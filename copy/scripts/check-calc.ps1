# 通用计算器点击校验：点击每个 .calc 中的 button，检查 out 输出无 NaN/undefined/输入有误
param([string[]]$Files)
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

$js = @'
(function(){
  var out=[];
  var calcs=document.querySelectorAll('.calc');
  calcs.forEach(function(c,ci){
    var btns=c.querySelectorAll('button');
    btns.forEach(function(b){
      try{ b.click(); }catch(e){}
      var o=c.querySelector('.out');
      var txt=o? o.innerHTML : '(no .out)';
      var plain=txt.replace(/<[^>]+>/g,'').replace(/\s+/g,' ');
      var bad= /NaN|undefined|输入有误/.test(plain);
      out.push('calc'+(ci+1)+' btn['+b.textContent+'] '+(bad?'FAIL':'OK')+' | '+plain.substring(0,90));
    });
  });
  return JSON.stringify(out);
})()
'@

foreach ($f in $Files) {
  $url = "file:///" + ([System.IO.Path]::GetFullPath($f) -replace '\\','/')
  $t = New-Tab $url
  Start-Sleep -Seconds 3
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $ws.ConnectAsync([uri]$t.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
  Write-Output "=== $(Split-Path $f -Leaf) ==="
  $v = Eval $js
  ($v | ConvertFrom-Json) | ForEach-Object { Write-Output "  $_" }
  $ws.Dispose()
}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
