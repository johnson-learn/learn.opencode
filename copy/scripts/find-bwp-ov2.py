# -*- coding: utf-8 -*-
"""再查 BWP 剩余重叠"""
import re

d = r'C:\Users\job_p\Desktop\NR-f40'
h = open(d + r'\BWP-带宽部分全梳理.html', encoding='utf-8').read()
svgs = re.findall(r'<svg\b.*?</svg>', h, re.S)
for si, svg in enumerate(svgs):
    boxes = []
    for tag, content in re.findall(r'(<text\b[^>]*>)([\s\S]*?)</text>', svg):
        m = re.search(r'x="([\d.]+)"', tag)
        n = re.search(r'y="([\d.]+)"', tag)
        fs = re.search(r'font-size="([\d.]+)"', tag)
        an = re.search(r'text-anchor="(\w+)"', tag)
        if not (m and n and fs) or re.search(r'transform="rotate', tag):
            continue
        x = float(m.group(1)); y = float(n.group(1)); sz = float(fs.group(1))
        content = re.sub(r'<[^>]+>', '', content)
        anchor = an.group(1) if an else 'start'
        w = sum(sz if ord(ch) > 0x2E80 else sz*0.58 for ch in content)
        hgt = sz*1.25
        if anchor == 'middle': x -= w/2
        elif anchor == 'end': x -= w
        boxes.append((x, y-hgt, x+w, y+3, content[:34], sz, tag))
    for i in range(len(boxes)):
        for j in range(i+1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[0] < b[2]-0.5 and b[0] < a[2]-0.5 and a[1] < b[3]-0.5 and b[1] < a[3]-0.5:
                ovh = min(a[3], b[3]) - max(a[1], b[1])
                if ovh > 0.55*min(a[5], b[5]):
                    print('SVG#%d: [%s] <<>> [%s] y=%d~%d vs %d~%d' % (si+1, a[4], b[4], a[1], a[3], b[1], b[3]))
                    print('  A:', a[6][:100])
                    print('  B:', b[6][:100])
