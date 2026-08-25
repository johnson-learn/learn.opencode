# -*- coding: utf-8 -*-
"""②③ BWP / PDCCH 整合为单文件（按讲次顺序拼接 body，练习册放最后）"""
import re, os

d = r'C:\Users\job_p\Desktop\NR-f40'

def integrate(series, order, outname, main_title):
    files = [os.path.join(d, f'{series}-{n:02d}-*.html') for n in range(10)]
    # 解析实际文件
    byn = {}
    for f in os.listdir(d):
        m = re.match(rf'{series}-(\d\d)-.*\.html', f)
        if m:
            byn[int(m.group(1))] = os.path.join(d, f)
    head = None
    parts = []
    for n in order:
        p = byn[n]
        h = open(p, encoding='utf-8').read()
        if head is None:
            head = h[h.index('<head>'):h.index('</head>')+7]
            head = head.replace('<title>' + re.search(r'<title>([\s\S]*?)</title>', head).group(1) + '</title>', f'<title>{main_title}</title>')
        body = h[h.index('<body>')+len('<body>'):h.index('</body>')]
        # 去掉各文件自己的 h1 标题与导航/版权行
        body = re.sub(r'<h1[^>]*>[\s\S]*?</h1>', '', body, count=1)
        body = re.sub(r'<p class="src"[^>]*>.*?</p>', '', body)
        parts.append(body)
    doc = ('<!DOCTYPE html>\n<html lang="zh-CN">\n' + head
           + f'\n<body>\n<h1>{main_title}</h1>\n'
           + '<p class="src" style="text-align:left;">本文件由原分讲文件整合而成（按讲次顺序），整合后原分文件已删除。</p>\n'
           + '\n'.join(parts)
           + '\n</body>\n</html>\n')
    out = os.path.join(d, outname)
    open(out, 'w', encoding='utf-8').write(doc)
    print(outname, len(doc))
    return out

bwp_out = integrate('BWP', [1, 2, 5, 6, 7, 9, 8], 'BWP-带宽部分全梳理.html', 'BWP 专题：带宽部分全梳理（整合版）')
pdcch_out = integrate('PDCCH', [1, 2, 3, 4, 5, 6, 7, 9, 8], 'PDCCH-物理下行控制信道全梳理.html', 'PDCCH 专题：物理下行控制信道全梳理（整合版）')
print('整合完成')
