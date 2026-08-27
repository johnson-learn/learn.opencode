# -*- coding: utf-8 -*-
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<3GPP文档库目录>'
for f in ['PDSCH-物理下行共享信道全梳理.html', 'PUSCH-物理上行共享信道全梳理.html']:
    h = open(d + '\\' + f, encoding='utf-8').read()
    body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
    o = len(re.findall(r'(?<!\\)\\\(', h))
    c = len(re.findall(r'(?<!\\)\\\)', h))
    toks = re.findall(r'<div[\s>]|</div>|<table[\s>]|</table>|<pre[\s>]|</pre>|<figure[\s>]|</figure>|<h2>|</h2>|<h3>|</h3>|<ol[\s>]|</ol>|<ul[\s>]|</ul>|<span[\s>]|</span>', h)
    dep = 0
    for t in toks:
        dep += -1 if t.startswith('</') else 1
        if dep < 0:
            dep = 0
    print(f, '| 同构:', len(re.findall(r'同构|完全相同|几乎同构', body)), '| MathJax:', o, '/', c, '| 标签深度:', dep, '| 大小:', len(h))
