# SVG 文字重叠检测：真实浏览器渲染后用 getBBox 检测所有 text 元素两两重叠
param([string[]]$Files)
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$port = 9241
$tmp = "<用户临时目录>\opencode\chrome-ov"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
$proc = Start-Process $chrome -ArgumentList "--headless=new","--disable-gpu","--remote-debugging-port=$port","--user-data-dir=$tmp","about:blank" -PassThru
Start-Sleep -Seconds 2

function Send-CDP([string]$method, [string]$paramsJson) {
  $body = "{`"id`":1,`"method`":`"$method`",`"params`":$paramsJson}"
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
  $seg = New-Object System.ArraySegment[byte] -ArgumentList @(,$bytes)
  $script:ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).Wait()
  $buf = New-Object byte[] 1048576
  $rseg = New-Object System.ArraySegment[byte] -ArgumentList @(,$buf)
  $out = New-Object System.Collections.Generic.List[byte]
  do { $res = $ws.ReceiveAsync($rseg, [Threading.CancellationToken]::None).Result; for ($i=0; $i -lt $res.Count; $i++) { $out.Add($buf[$i]) } } while (-not $res.EndOfMessage)
  return ([System.Text.Encoding]::UTF8.GetString($out.ToArray()) | ConvertFrom-Json)
}

$js = @'
(function(){
  var out=[];
  var svgs=document.querySelectorAll('svg');
  svgs.forEach(function(svg,si){
    var texts=svg.querySelectorAll('text');
    var boxes=[];
    texts.forEach(function(t){
      try{
        var b=t.getBBox();
        if(b.width>0 && b.height>0){
          boxes.push({t:(t.textContent||'').replace(/\s+/g,' ').substring(0,36), x:b.x, y:b.y, w:b.width, h:b.height});
        }
      }catch(e){}
    });
    for(var i=0;i<boxes.length;i++)for(var j=i+1;j<boxes.length;j++){
      var a=boxes[i],b=boxes[j];
      if(a.x < b.x+b.w+1 && b.x < a.x+a.w+1 && a.y < b.y+b.h+1 && b.y < a.y+a.h+1){
        out.push('SVG#'+(si+1)+' ['+a.t+'] <<OVERLAP>> ['+b.t+']');
      }
    }
  });
  return JSON.stringify({count:out.length, items:out});
})()
'@

foreach ($f in $Files) {
  $url = "file:///" + ([System.IO.Path]::GetFullPath($f) -replace '\\','/')
  $t = Invoke-RestMethod -Method Put "http://127.0.0.1:$port/json/new?$([uri]::EscapeDataString($url))"
  Start-Sleep -Seconds 3
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $ws.ConnectAsync([uri]$t.webSocketDebuggerUrl, [Threading.CancellationToken]::None).Wait()
  $p = "{`"expression`":`"$($js -replace '\\','\\\\' -replace '"','\\"')`",`"returnByValue`":true}"
  $r = Send-CDP "Runtime.evaluate" $p
  $v = $r.result.result.value
  $o = $v | ConvertFrom-Json
  "{0} : {1} overlap pairs" -f (Split-Path $f -Leaf), $o.count
  if ($o.count -gt 0) { $o.items | ForEach-Object { "   $_" } }
  $ws.Dispose()
}
Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
