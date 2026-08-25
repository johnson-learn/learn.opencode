# -*- coding: utf-8 -*-
"""CSI 主线最终校验：重叠 + 结构"""
import re

f = r'C:\Users\job_p\Desktop\NR-f40\CSI-信道状态信息全梳理.html'
h = open(f, encoding='utf-8').read()
svgs = re.findall(r'<svg\b.*?</svg>', h, re.S)
total = 0
for si, svg in enumerate(svgs):
    texts = re.findall(r'(<text\b[^>]*>)([\s\S]*?)</text>', svg)
    boxes = []
    for tag, content in texts:
        m = re.search(r'x="([\d.]+)"', tag)
        n = re.search(r'y="([\d.]+)"', tag)
        fs = re.search(r'font-size="([\d.]+)"', tag)
        an = re.search(r'text-anchor="(\w+)"', tag)
        rot = re.search(r'transform="rotate', tag)
        if not (m and n and fs) or rot:
            continue
        x = float(m.group(1)); y = float(n.group(1)); sz = float(fs.group(1))
        content = re.sub(r'<[^>]+>', '', content)
        anchor = an.group(1) if an else 'start'
        w = sum(sz if ord(ch) > 0x2E80 else sz*0.58 for ch in content)
        hgt = sz * 1.25
        if anchor == 'middle': x -= w/2
        elif anchor == 'end': x -= w
        boxes.append((x, y-hgt, x+w, y+3, content[:28], sz))
    for i in range(len(boxes)):
        for j in range(i+1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[0] < b[2]-0.5 and b[0] < a[2]-0.5 and a[1] < b[3]-0.5 and b[1] < a[3]-0.5:
                ovh = min(a[3], b[3]) - max(a[1], b[1])
                if ovh > 0.55 * min(a[5], b[5]):
                    total += 1
                    print('重叠 SVG#%d: [%s] <<>> [%s]' % (si+1, a[4], b[4]))
print('SVG 重叠对数:', total)

body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
print('比喻词:', len(re.findall(r'尺子|交卷|考卷|作业本|点名|挖空|灯塔|司令|户口本', body)))
print('伪公式:', len(re.findall(r'[\u2308\u230A]|N_RB\^|log2\(', h)))
print('MathJax:', len(re.findall(r'(?<!\\)\\\(', h)), '/', len(re.findall(r'(?<!\\)\\\)', h)),
      '|', len(re.findall(r'\\\[', h)), '/', len(re.findall(r'\\\]', h)))
print('h2:', len(re.findall(r'<h2>', h)), '| 大小:', len(h))
