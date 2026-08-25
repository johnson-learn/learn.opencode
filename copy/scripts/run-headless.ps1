[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$files = [System.IO.File]::ReadAllLines("C:\Users\<用户名>\AppData\Local\Temp\opencode\files-to-check.txt", [System.Text.Encoding]::UTF8)
& "C:\Users\<用户名>\AppData\Local\Temp\opencode\check-headless.ps1" -Files $files