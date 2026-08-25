# -*- coding: utf-8 -*-
"""修复 BIT/OCTET STRING 拆分着色"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
d = r'<用户桌面目录>\NR-f40'
for f in ['系统消息-01-SSB-MIB-SIB1与OSI.html', 'PDCCH-物理下行控制信道全梳理.html']:
    h = open(d + '\\' + f, encoding='utf-8').read()
    n1 = h.count('<span class="rt">BIT</span> STRING')
    n2 = h.count('<span class="rt">OCTET</span> STRING')
    h = h.replace('<span class="rt">BIT</span> STRING', '<span class="rt">BIT STRING</span>')
    h = h.replace('<span class="rt">OCTET</span> STRING', '<span class="rt">OCTET STRING</span>')
    open(d + '\\' + f, 'w', encoding='utf-8').write(h)
    print(f, '| BIT 拆分修复:', n1, '| OCTET 拆分修复:', n2)
