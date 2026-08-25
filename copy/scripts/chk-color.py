# -*- coding: utf-8 -*-
"""排查各文件 ASN.1 pre 块的着色情况"""
import re

d = r'<3GPP文档库目录>'
for f in ['BWP-带宽部分全梳理.html', 'PDCCH-物理下行控制信道全梳理.html',
          '系统消息-01-SSB-MIB-SIB1与OSI.html', 'CSI-信道状态信息全梳理.html']:
    h = open(d + '\\' + f, encoding='utf-8').read()
    pres = re.findall(r'<pre[^>]*>[\s\S]*?</pre>', h)
    uncolored = []
    for p in pres:
        has_asn = ('::=' in p or 'SEQUENCE {' in p or 'CHOICE {' in p or 'ENUMERATED {' in p)
        has_color = ('class="rv"' in p or 'class="rt"' in p or 'class="asn"' in p or 'class="rc"' in p)
        if has_asn and not has_color:
            txt = re.sub(r'<[^>]+>', ' ', p)
            txt = re.sub(r'\s+', ' ', txt).strip()[:70]
            uncolored.append(txt)
    print(f, '| pre 总数:', len(pres), '| ASN.1 无着色 pre:', len(uncolored))
    for t in uncolored:
        print('    >>', t)
