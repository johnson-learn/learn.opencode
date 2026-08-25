# -*- coding: utf-8 -*-
"""CSI 拆分后全量校验：8 个文件的结构/公式/变量/图链接/SVG 重叠"""
import re, glob, os

outdir = r'C:\Users\job_p\Desktop\NR-f40'
files = sorted(glob.glob(os.path.join(outdir, 'CSI-0*.html')))
print('文件:', [os.path.basename(f) for f in files])
bad = 0
for f in files:
    name = os.path.basename(f)
    h = open(f, encoding='utf-8').read()
    body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
    issues = []
    bw = len(re.findall(r'尺子|交卷|考卷|作业本|点名|挖空|灯塔|司令|户口本', body))
    if bw: issues.append(f'比喻词{bw}')
    pf = len(re.findall(r'[\u2308\u230A]|N_RB\^|log2\(', h))
    if pf: issues.append(f'伪公式{pf}')
    o = len(re.findall(r'(?<!\\)\\\(', h)); c = len(re.findall(r'(?<!\\)\\\)', h))
    if o != c: issues.append(f'math {o}/{c}')
    od = len(re.findall(r'\\\[', h)); cd = len(re.findall(r'\\\]', h))
    if od != cd: issues.append(f'display {od}/{cd}')
    toks = re.findall(r'<div[\s>]|</div>|<table[\s>]|</table>|<pre[\s>]|</pre>|<figure[\s>]|</figure>', h)
    depth = 0
    for t in toks:
        depth += -1 if t.startswith('</') else 1
        if depth < 0: depth = 0
    if depth != 0: issues.append(f'标签深度{depth}')
    # 导航链接检查
    for link in re.findall(r'href="(CSI-0\d[^"]*)"', h):
        if not os.path.exists(os.path.join(outdir, link)):
            issues.append(f'断链 {link}')
    print(f'{name}: {"OK" if not issues else " / ".join(issues)}')
    if issues: bad += 1

# SVG 重叠检测（所有 CSI 文件）
total = 0
for f in files:
    h = open(f, encoding='utf-8').read()
    svgs = re.findall(r'<svg\b.*?</svg>', h, re.S)
    for si, svg in enumerate(svgs):
        texts = re.findall(r'(<text\b[^>]*>)([\s\S]*?)</text>', svg)
        boxes = []
        for tag, content in texts:
            m = re.search(r'x="([\d.]+)"', tag); n = re.search(r'y="([\d.]+)"', tag)
            fs = re.search(r'font-size="([\d.]+)"', tag); an = re.search(r'text-anchor="(\w+)"', tag)
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
                        print(f'  重叠 {os.path.basename(f)} SVG#{si+1}: [{a[4]}] <<>> [{b[4]}]')
print('SVG 重叠对数:', total)
print('结构异常文件数:', bad)
