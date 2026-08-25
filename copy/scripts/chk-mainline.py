# -*- coding: utf-8 -*-
import re

d = r'C:\Users\job_p\Desktop\NR-f40'
for f in ['BWP-带宽部分全梳理.html', 'PDCCH-物理下行控制信道全梳理.html']:
    h = open(d + '\\' + f, encoding='utf-8').read()
    print(f, '| mainline:', h.count('mainline'), '| bridge:', h.count('class="bridge"'), '| 大小:', len(h))
    toks = re.findall(r'<div[\s>]|</div>|<h2>|</h2>|<table[\s>]|</table>|<pre[\s>]|</pre>', h)
    depth = 0
    for t in toks:
        depth += -1 if t.startswith('</') else 1
        if depth < 0:
            depth = 0
    print('  标签深度:', depth)
