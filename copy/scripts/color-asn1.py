# -*- coding: utf-8 -*-
"""ASN.1 pre 块规则化着色：结构名紫/字段名红/类型蓝/行尾注释绿/省略号灰"""
import re

d = r'<3GPP文档库目录>'

def color_pre(pre):
    m = re.match(r'(<pre[^>]*>)([\s\S]*?)</pre>', pre)
    open_tag, body = m.group(1), m.group(2)
    # 1) 行尾注释
    body = re.sub(r'( -- [^\n<]*)', r'<span class="rc">\1</span>', body)
    # 2) 结构名 ::=
    body = re.sub(r'(^|\n)(\s*)([A-Z][A-Za-z0-9-]*)(\s*::=)', lambda m: m.group(1) + m.group(2) + '<span class="asn">' + m.group(3) + '</span>' + m.group(4), body)
    # 3) 字段名 + 类型
    body = re.sub(
        r'(^|\n)(\s*)([a-z][A-Za-z0-9-]*)(\s+)([A-Z][A-Za-z0-9-]*|BIT STRING|INTEGER|ENUMERATED|BOOLEAN|NULL|OCTET STRING|CHOICE|SEQUENCE|SetupRelease)',
        lambda m: m.group(1) + m.group(2) + '<span class="rv">' + m.group(3) + '</span>' + m.group(4) + '<span class="rt">' + m.group(5) + '</span>',
        body)
    # 4) 独立省略号行
    body = re.sub(r'(^|\n)(\s*)(\.\.\.)(\s*)(?:\n|$)', lambda m: m.group(1) + m.group(2) + '<span class="dot">' + m.group(3) + '</span>' + m.group(4), body)
    return open_tag + body + '</pre>'

for fname in ['系统消息-01-SSB-MIB-SIB1与OSI.html', 'PDCCH-物理下行控制信道全梳理.html']:
    f = d + '\\' + fname
    h = open(f, encoding='utf-8').read()
    def fix(m):
        p = m.group(0)
        if ('class="rv"' in p or 'class="rt"' in p or 'class="asn"' in p or 'class="rc"' in p or 'class="dot"' in p):
            return p
        return color_pre(p)
    h2 = re.sub(r'<pre[^>]*>[\s\S]*?</pre>', fix, h)
    open(f, 'w', encoding='utf-8').write(h2)
    # 复查
    pres = re.findall(r'<pre[^>]*>[\s\S]*?</pre>', h2)
    unc = [re.sub(r'<[^>]+>', ' ', p)[:50] for p in pres
           if ('::=' in p or 'SEQUENCE {' in p or 'ENUMERATED {' in p) and 'class="rv"' not in p]
    print(fname, '| 剩余无着色:', len(unc))
    for t in unc:
        print('   >>', t)
