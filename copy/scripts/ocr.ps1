# OCR 工具：读取图片文字（Windows 内置 OCR 引擎，支持中英文）
# 用法：
#   powershell -File ocr.ps1 -path "图片路径.png"   对文件识别
#   powershell -File ocr.ps1                       对剪贴板中的截图识别
param([string]$path = "")

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder,Windows.Foundation,ContentType=WindowsRuntime]
$null = [Windows.Storage.StorageFile,Windows.Storage,ContentType=WindowsRuntime]
$null = [Windows.Storage.Streams.RandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime]

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($WinRtTask, $ResultType) {
  $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
  $netTask = $asTask.Invoke($null, @($WinRtTask))
  $netTask.Wait(-1) | Out-Null
  $netTask.Result
}

$tmpPng = Join-Path $env:TEMP "ocr-input.png"
$useTmp = $false

if (-not $path) {
  # 从剪贴板读图片
  Add-Type -AssemblyName System.Windows.Forms
  Add-Type -AssemblyName System.Drawing
  $img = [System.Windows.Forms.Clipboard]::GetImage()
  if ($null -eq $img) { Write-Output "ERROR: 剪贴板中没有图片"; exit 1 }
  $img.Save($tmpPng, [System.Drawing.Imaging.ImageFormat]::Png)
  $path = $tmpPng
  $useTmp = $true
}

if (-not (Test-Path $path)) { Write-Output "ERROR: 文件不存在: $path"; exit 1 }

try {
  $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path $path).Path)) ([Windows.Storage.StorageFile])
  $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
  $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
  if ($null -eq $engine) {
    $lang = New-Object Windows.Globalization.Language "en-US"
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
  }
  if ($null -eq $engine) { Write-Output "ERROR: 无法创建 OCR 引擎"; exit 1 }
  $result = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
  Write-Output ("[OCR 语言: " + $engine.RecognizerLanguage.LanguageTag + "]")
  Write-Output "----- OCR 结果（按行）-----"
  foreach ($line in $result.Lines) { Write-Output $line.Text }
  $stream.Dispose()
} catch {
  Write-Output "ERROR: $($_.Exception.Message)"
} finally {
  if ($useTmp -and (Test-Path $tmpPng)) { Remove-Item $tmpPng -Force -ErrorAction SilentlyContinue }
}