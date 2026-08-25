# -*- coding: utf-8 -*-
"""裸取整符号与 log2 转 MathJax"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<用户桌面目录>\NR-f40'
for f in ['PDSCH-物理下行共享信道全梳理.html', 'PUSCH-物理上行共享信道全梳理.html']:
    h = open(d + '\\' + f, encoding='utf-8').read()
    parts = re.split(r'(<script[\s\S]*?</script>)', h)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'\u230A([^\u230B]*?)\u230B', r'\\(\\lfloor \1 \\rfloor\\)', parts[i])
        parts[i] = re.sub(r'\u2308([^\u2309]*?)\u2309', r'\\(\\lceil \1 \\rceil\\)', parts[i])
        parts[i] = re.sub(r'(?<![\\a-zA-Z])log2\(', r'\\(\\log_2(\\)', parts[i])
    h = ''.join(parts)
    open(d + '\\' + f, 'w', encoding='utf-8').write(h)
    nojs = re.sub(r'<script[\s\S]*?</script>', '', h)
    print(f, '| 残留:', len(re.findall(r'[\u2308\u230A]|(?<![\\a-zA-Z])log2\(', nojs)),
          '| MathJax:', len(re.findall(r'(?<!\\)\\\(', h)), '/', len(re.findall(r'(?<!\\)\\\)', h)))
