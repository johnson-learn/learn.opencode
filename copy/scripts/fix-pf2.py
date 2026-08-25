# -*- coding: utf-8 -*-
"""修复 PDSCH 例题 4.2 与系统消息双视角表的裸取整符号"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<用户桌面目录>\NR-f40'
f1 = d + r'\PDSCH-物理下行共享信道全梳理.html'
h = open(f1, encoding='utf-8').read()
h = h.replace('C=⌈100000/(8448−24)⌉=⌈100000/8424⌉=12 段', 'C=\\(\\lceil 100000/(8448-24) \\rceil=\\lceil 100000/8424 \\rceil=12\\) 段')
open(f1, 'w', encoding='utf-8').write(h)

f2 = d + r'\系统消息-01-SSB-MIB-SIB1与OSI.html'
h = open(f2, encoding='utf-8').read()
h = h.replace('按窗口公式（x=(n−1)w、SFN mod T=⌊x/N⌋）逐个窗口盲检', '按窗口公式（\\(x=(n-1)w\\)、\\(SFN\\bmod T=\\lfloor x/N\\rfloor\\)）逐个窗口盲检')
open(f2, 'w', encoding='utf-8').write(h)

for f in [f1, f2]:
    h = open(f, encoding='utf-8').read()
    body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
    nojs = re.sub(r'<script[\s\S]*?</script>', '', body)
    print(f.split(chr(92))[-1], '| 伪公式:', len(re.findall(r'[\u2308\u230A]|(?<![\\a-zA-Z])log2\(', nojs)),
          '| math:', len(re.findall(r'(?<!\\)\\\(', h)), '/', len(re.findall(r'(?<!\\)\\\)', h)))
