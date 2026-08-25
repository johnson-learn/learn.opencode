# -*- coding: utf-8 -*-
"""三个文件校验 + 删除旧分文件"""
import re, os, glob

d = r'<用户桌面目录>\NR-f40'
files = ['系统消息-01-SSB-MIB-SIB1与OSI.html', 'BWP-带宽部分全梳理.html', 'PDCCH-物理下行控制信道全梳理.html']
bad = 0
for name in files:
    f = os.path.join(d, name)
    h = open(f, encoding='utf-8').read()
    body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
    issues = []
    bw = len(re.findall(r'灯塔|指路牌|司令部|户口本|门卫|白拿|尺子|交卷', body))
    if bw: issues.append(f'比喻词{bw}')
    pf = len(re.findall(r'[\u2308\u230A]|N_RB\^|log2\(', h))
    if pf: issues.append(f'伪公式{pf}')
    o = len(re.findall(r'(?<!\\)\\\(', h)); c = len(re.findall(r'(?<!\\)\\\)', h))
    if o != c: issues.append(f'math {o}/{c}')
    toks = re.findall(r'<div[\s>]|</div>|<table[\s>]|</table>|<pre[\s>]|</pre>|<figure[\s>]|</figure>|<h2>|</h2>|<h3>|</h3>|<ol[\s>]|</ol>|<ul[\s>]|</ul>|<span[\s>]|</span>', h)
    depth = 0
    for t in toks:
        depth += -1 if t.startswith('</') else 1
        if depth < 0: depth = 0
    if depth != 0: issues.append(f'标签{depth}')
    # SVG 重叠
    ov = 0
    for svg in re.findall(r'<svg\b.*?</svg>', h, re.S):
        boxes = []
        for tag, content in re.findall(r'(<text\b[^>]*>)([\s\S]*?)</text>', svg):
            m = re.search(r'x="([\d.]+)"', tag); n = re.search(r'y="([\d.]+)"', tag)
            fs = re.search(r'font-size="([\d.]+)"', tag); an = re.search(r'text-anchor="(\w+)"', tag)
            if not (m and n and fs) or re.search(r'transform="rotate', tag): continue
            x = float(m.group(1)); y = float(n.group(1)); sz = float(fs.group(1))
            content = re.sub(r'<[^>]+>', '', content)
            anchor = an.group(1) if an else 'start'
            w = sum(sz if ord(ch) > 0x2E80 else sz*0.58 for ch in content)
            hgt = sz*1.25
            if anchor == 'middle': x -= w/2
            elif anchor == 'end': x -= w
            boxes.append((x, y-hgt, x+w, y+3, sz))
        for i in range(len(boxes)):
            for j in range(i+1, len(boxes)):
                a, b = boxes[i], boxes[j]
                if a[0] < b[2]-0.5 and b[0] < a[2]-0.5 and a[1] < b[3]-0.5 and b[1] < a[3]-0.5:
                    ovh = min(a[3], b[3]) - max(a[1], b[1])
                    if ovh > 0.55*min(a[4], b[4]): ov += 1
    if ov: issues.append(f'重叠{ov}')
    print(f'{name}: {"OK" if not issues else " / ".join(issues)}')
    if issues: bad += 1

# 删除旧分文件
for pat in ['BWP-0*.html', 'PDCCH-0*.html']:
    for f in glob.glob(os.path.join(d, pat)):
        os.remove(f)
        print('已删除:', os.path.basename(f))
print('异常文件数:', bad)
