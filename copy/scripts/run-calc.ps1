[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$files = [System.IO.File]::ReadAllLines("C:\Users\job_p\AppData\Local\Temp\opencode\files-to-check.txt", [System.Text.Encoding]::UTF8)
& "C:\Users\job_p\AppData\Local\Temp\opencode\check-calc.ps1" -Files $files