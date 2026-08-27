[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$files = [System.IO.File]::ReadAllLines("<用户临时目录>\opencode\files-to-check.txt", [System.Text.Encoding]::UTF8)
& "<用户临时目录>\opencode\check-overlap.ps1" -Files $files