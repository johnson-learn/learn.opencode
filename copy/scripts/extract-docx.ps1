param(
  [string]$src = "<用户桌面目录>\NR-f40",
  [string]$out = "<用户临时目录>\opencode\specs"
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $out | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Convert-OMML([System.Xml.XmlNode]$node, $ns) {
  $sb = New-Object System.Text.StringBuilder
  $base = $node.SelectSingleNode(".//m:e/m:t", $ns)
  $baseTxt = if ($base) { $base.InnerText } else { "" }
  if ($baseTxt) { [void]$sb.Append($baseTxt) }
  $sub = $node.SelectSingleNode(".//m:sub/m:t", $ns)
  if ($sub) { [void]$sb.Append("_$($sub.InnerText)") }
  $sup = $node.SelectSingleNode(".//m:sup/m:t", $ns)
  if ($sup) { [void]$sb.Append("^$($sup.InnerText)") }
  return $sb.ToString()
}

function Convert-OMMLRec($node, $ns) {
  $sb = New-Object System.Text.StringBuilder
  foreach ($child in $node.ChildNodes) {
    switch ($child.Name) {
      "m:t" { [void]$sb.Append($child.InnerText) }
      "m:sSub" {
        $e = $child.SelectSingleNode("./m:e", $ns)
        $s = $child.SelectSingleNode("./m:sub", $ns)
        $et = if ($e) { (Convert-OMMLRec $e $ns) } else { "" }
        $st = if ($s) { (Convert-OMMLRec $s $ns) } else { "" }
        if ($et -and $st) { [void]$sb.Append("$et" + "_$st") } else { [void]$sb.Append($et + $st) }
      }
      "m:sSup" {
        $e = $child.SelectSingleNode("./m:e", $ns)
        $s = $child.SelectSingleNode("./m:sup", $ns)
        $et = if ($e) { (Convert-OMMLRec $e $ns) } else { "" }
        $st = if ($s) { (Convert-OMMLRec $s $ns) } else { "" }
        if ($et -and $st) { [void]$sb.Append("$et" + "^$st") } else { [void]$sb.Append($et + $st) }
      }
      "m:sSubSup" {
        $e = $child.SelectSingleNode("./m:e", $ns)
        $s = $child.SelectSingleNode("./m:sub", $ns)
        $p = $child.SelectSingleNode("./m:sup", $ns)
        $et = if ($e) { (Convert-OMMLRec $e $ns) } else { "" }
        $st = if ($s) { (Convert-OMMLRec $s $ns) } else { "" }
        $pt = if ($p) { (Convert-OMMLRec $p $ns) } else { "" }
        if ($et) { [void]$sb.Append("$et" + "_$st" + "^$pt") }
      }
      "m:f" {
        $n = $child.SelectSingleNode("./m:num", $ns)
        $d = $child.SelectSingleNode("./m:den", $ns)
        $nt = if ($n) { (Convert-OMMLRec $n $ns) } else { "" }
        $dt = if ($d) { (Convert-OMMLRec $d $ns) } else { "" }
        [void]$sb.Append("{$nt}/{$dt}")
      }
      "m:rad" {
        $deg = $child.SelectSingleNode("./m:deg", $ns)
        $ee = $child.SelectSingleNode("./m:e", $ns)
        $et = if ($ee) { (Convert-OMMLRec $ee $ns) } else { "" }
        [void]$sb.Append("sqrt($et)")
      }
      "m:d" {
        $parts = @()
        foreach ($pe in $child.SelectNodes("./m:e", $ns)) { $parts += (Convert-OMMLRec $pe $ns) }
        [void]$sb.Append("(" + ($parts -join "") + ")")
      }
      "m:nary" {
        $ee = $child.SelectSingleNode("./m:e", $ns)
        $sub = $child.SelectSingleNode("./m:sub", $ns)
        $sup = $child.SelectSingleNode("./m:sup", $ns)
        $et = if ($ee) { (Convert-OMMLRec $ee $ns) } else { "" }
        $st = if ($sub) { (Convert-OMMLRec $sub $ns) } else { "" }
        $pt = if ($sup) { (Convert-OMMLRec $sup $ns) } else { "" }
        [void]$sb.Append("SUM($st..$pt)[$et]")
      }
      default {
        $inner = (Convert-OMMLRec $child $ns)
        if ($inner) { [void]$sb.Append($inner) }
      }
    }
  }
  return $sb.ToString()
}

function Get-ParaText($para, $ns) {
  $parts = New-Object System.Collections.ArrayList
  foreach ($child in $para.ChildNodes) {
    if ($child.Name -eq "w:r") {
      $t = ($child.SelectNodes(".//w:t", $ns) | ForEach-Object { $_.InnerText }) -join ""
      if ($t) { [void]$parts.Add($t) }
      $br = $child.SelectNodes(".//w:br | .//w:cr", $ns)
      if ($br.Count -gt 0) { [void]$parts.Add(" ") }
    } elseif ($child.Name -eq "w:tab") { [void]$parts.Add(" ") }
    elseif ($child.Name -eq "m:oMath") {
      $mt = Convert-OMMLRec $child $ns
      if ($mt) { [void]$parts.Add("[$mt]") }
    }
  }
  return ($parts -join "")
}

$results = @()
Get-ChildItem $src -Filter *.docx | ForEach-Object {
  $f = $_
  $txtPath = Join-Path $out "$($f.BaseName).txt"
  try {
    $zip = [System.IO.Compression.ZipFile]::OpenRead($f.FullName)
    $entry = $zip.GetEntry("word/document.xml")
    $reader = New-Object System.IO.StreamReader($entry.Open(), [System.Text.Encoding]::UTF8)
    $xmlStr = $reader.ReadToEnd(); $reader.Close(); $zip.Dispose()
    [xml]$doc = $xmlStr
    $ns = New-Object System.Xml.XmlNamespaceManager($doc.NameTable)
    $ns.AddNamespace("w","http://schemas.openxmlformats.org/wordprocessingml/2006/main")
    $ns.AddNamespace("m","http://schemas.openxmlformats.org/officeDocument/2006/math")
    $sb = New-Object System.Text.StringBuilder
    $body = $doc.SelectSingleNode("//w:body", $ns)
    foreach ($child in $body.ChildNodes) {
      if ($child.Name -eq "w:p") {
        $t = Get-ParaText $child $ns
        if ($t.Trim().Length -gt 0) { [void]$sb.AppendLine($t) }
      } elseif ($child.Name -eq "w:tbl") {
        foreach ($row in $child.SelectNodes("./w:tr", $ns)) {
          $cells = @()
          foreach ($cell in $row.SelectNodes("./w:tc", $ns)) {
            $ct = ($cell.SelectNodes(".//w:p", $ns) | ForEach-Object { Get-ParaText $_ $ns }) -join " "
            $cells += $ct
          }
          [void]$sb.AppendLine(($cells -join " | "))
        }
        [void]$sb.AppendLine("")
      }
    }
    Set-Content -Path $txtPath -Value $sb.ToString() -Encoding UTF8
    $results += "$($f.Name) OK $((Get-Item $txtPath).Length) bytes"
  } catch {
    $results += "$($f.Name) FAILED: $($_.Exception.Message)"
  }
}
$results | ForEach-Object { Write-Output $_ }
Write-Output "DONE docx"