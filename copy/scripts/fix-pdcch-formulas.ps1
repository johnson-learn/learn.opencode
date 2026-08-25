# 修复 PDCCH 各文件中纯文本伪公式（⌈⌉、log2( 等未用 MathJax 包裹），统一为标准 LaTeX 输出
$ErrorActionPreference = "Stop"
$LC = [char]0x2308
$RC = [char]0x2309
$LF = [char]0x230A
$RF = [char]0x230B

$f3 = "<3GPP文档库目录>\PDCCH-03-DCI格式与字段.html"
$c = Get-Content $f3 -Raw -Encoding UTF8
$pairs = @(
  @("max(" + $LC + "log2(N_RB^BWP(N_RB^BWP+1)/2)" + $RC + "," + $LC + "N_RB^BWP/P" + $RC + ")+1", '$\max(\lceil\log_2(N_{RB}^{BWP}(N_{RB}^{BWP}+1)/2)\rceil,\lceil N_{RB}^{BWP}/P\rceil)+1$'),
  @($LC + "log2(N_RB^DL,BWP(N_RB^DL,BWP+1)/2)" + $RC, '$\lceil\log_2(N_{RB}^{DL,BWP}(N_{RB}^{DL,BWP}+1)/2)\rceil$'),
  @($LC + "log2(N_RB^BWP(N_RB^BWP+1)/2)" + $RC, '$\lceil\log_2(N_{RB}^{BWP}(N_{RB}^{BWP}+1)/2)\rceil$'),
  @($LC + "log2(N_RB(N_RB+1)/2)" + $RC, '$\lceil\log_2(N_{RB}(N_{RB}+1)/2)\rceil$'),
  @($LC + "N_RB^BWP/P" + $RC, '$\lceil N_{RB}^{BWP}/P\rceil$'),
  @($LC + "N_RB/P" + $RC, '$\lceil N_{RB}/P\rceil$'),
  @($LC + "log2(n_BWP)" + $RC, '$\lceil\log_2(n_{BWP})\rceil$'),
  @($LC + "log2(I)" + $RC, '$\lceil\log_2(I)\rceil$'),
  @($LC + "log2(24" + [char]0xD7 + "25/2)" + $RC, '$\lceil\log_2(24\times25/2)\rceil$'),
  @($LC + "log2(300)" + $RC, '$\lceil\log_2(300)\rceil$'),
  @($LC + "log2(48" + [char]0xD7 + "49/2)" + $RC, '$\lceil\log_2(48\times49/2)\rceil$'),
  @($LC + "log2(1176)" + $RC, '$\lceil\log_2(1176)\rceil$'),
  @($LC + "log2(100" + [char]0xD7 + "101/2)" + $RC, '$\lceil\log_2(100\times101/2)\rceil$'),
  @($LC + "log2(50" + [char]0xD7 + "51/2)" + $RC, '$\lceil\log_2(50\times51/2)\rceil$'),
  @($LC + "log2(20100)" + $RC, '$\lceil\log_2(20100)\rceil$'),
  @($LC + "log2(5050)" + $RC, '$\lceil\log_2(5050)\rceil$'),
  @($LC + "log2(1275)" + $RC, '$\lceil\log_2(1275)\rceil$'),
  @($LC + "log2(1176)" + $RC + " = 11 bit", '$\lceil\log_2(1176)\rceil = 11$ bit')
)
foreach ($p in $pairs) { $c = $c.Replace($p[0], $p[1]) }
[System.IO.File]::WriteAllText($f3, $c, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "03 done"

$f6 = "<3GPP文档库目录>\PDCCH-06-配置链.html"
$c = Get-Content $f6 -Raw -Encoding UTF8
$c = $c.Replace("N_RB^CORESET", '$N_{RB}^{CORESET}$')
$c = $c.Replace("N_symb^CORESET", '$N_{symb}^{CORESET}$')
[System.IO.File]::WriteAllText($f6, $c, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "06 done"

$f8 = "<3GPP文档库目录>\PDCCH-08-练习册与计算器.html"
$c = Get-Content $f8 -Raw -Encoding UTF8
$c = $c.Replace("n_0=(O" + [char]0xB7 + "2^" + [char]0x3BC + "+" + $LF + "i" + [char]0xB7 + "M" + $RF + ") mod N_slot^frame," + [char]0x3BC, '$n_0=(O\cdot 2^{\mu}+\lfloor i\cdot M\rfloor) \bmod N_{slot}^{frame,\mu}$')
$c = $c.Replace("n_0=12 mod 10=2", '$n_0=12 \bmod 10=2$')
$c = $c.Replace($LC + "12/10" + $RC + "=1", '$\lfloor12/10\rfloor=1$')
$c = $c.Replace($LC + "log2(5050)" + $RC + "=13 bit", '$\lceil\log_2(5050)\rceil=13$ bit')
$c = $c.Replace($LC + "log2(1275)" + $RC + "=11 bit", '$\lceil\log_2(1275)\rceil=11$ bit')
[System.IO.File]::WriteAllText($f8, $c, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "08 done"