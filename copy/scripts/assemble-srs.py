# -*- coding: utf-8 -*-
"""组装 SRS 单文件 + 插图 + 校验"""
import re, os

base = r'<用户临时目录>\opencode'
outdir = r'<3GPP文档库目录>'
h = ''
for f in ('srs-r1.html', 'srs-r2.html', 'srs-r3.html'):
    h += open(os.path.join(base, f), encoding='utf-8').read() + '\n'

def wrap(figid, svg, caption):
    svg = svg.replace('<svg ', '<svg style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;" ')
    return (f'<figure style="margin:18px 0; text-align:center;">\n' + svg + '\n'
            + f'<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>{figid}</b> {caption}</figcaption>\n</figure>\n')

caps = {
    'srsfig1': ('图 1', 'SRS 四大用途（第 1 讲）：usage 字段决定 gNB 怎么用这份探测结果'),
    'srsfig2': ('图 2', 'SRS 梳齿复用示意（第 2 讲）：comb 决定频域隔点、CS 决定同梳齿内的码域区分；SRS 仅在时隙最后 6 个符号'),
    'srsfig3': ('图 3', '三种时域行为的启动方式（第 4 讲）：periodic=RRC 静态、SP=MAC CE、aperiodic=DCI 触发'),
}
anchors = [
    ('srsfig1', '<h3>1.2 四大用途（usage 字段，38.331 原文枚举）</h3>', 'before'),
    ('srsfig2', '<h3>2.3 原文：资源映射与梳齿（38.211 §6.4.1.4.3）【公式已核实】</h3>', 'before'),
    ('srsfig3', '<h3>4.1 Periodic SRS：RRC 配置即周期发送</h3>', 'before'),
]
for key, anchor, pos in anchors:
    svg = open(os.path.join(base, key + '.svg'), encoding='utf-8').read()
    fid, cap = caps[key]
    seg = wrap(fid, svg, cap)
    i = h.find(anchor)
    assert i > 0, '锚点缺失: ' + key
    if pos == 'after':
        i += len(anchor)
    h = h[:i] + seg + '\n' + h[i:]

target = os.path.join(outdir, 'SRS-探测参考信号全梳理.html')
open(target, 'w', encoding='utf-8').write(h)
print('大小:', len(h), '| SVG:', h.count('<svg'))

body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
print('比喻词:', len(re.findall(r'尺子|交卷|考卷|作业本|点名|挖空|灯塔|司令|户口本', body)))
nojs = re.sub(r'<script[\s\S]*?</script>', '', h)
print('伪公式(排除script):', len(re.findall(r'[\u2308\u230A]|N_RB\^|log2\(', nojs)))
print('MathJax:', len(re.findall(r'(?<!\\)\\\(', h)), '/', len(re.findall(r'(?<!\\)\\\)', h)), '|', len(re.findall(r'\\\[', h)), '/', len(re.findall(r'\\\]', h)))
toks = re.findall(r'<div[\s>]|</div>|<table[\s>]|</table>|<pre[\s>]|</pre>|<figure[\s>]|</figure>|<h2>|</h2>|<h3>|</h3>|<ol[\s>]|</ol>|<ul[\s>]|</ul>|<span[\s>]|</span>', h)
depth = 0
for t in toks:
    depth += -1 if t.startswith('</') else 1
    if depth < 0:
        depth = 0
print('标签深度:', depth, '| h2:', len(re.findall(r'<h2>', h)))
# SVG 重叠
ov = 0
for svg in re.findall(r'<svg\b.*?</svg>', h, re.S):
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
        boxes.append((x, y-hgt, x+w, y+3, content[:28], sz))
    for i in range(len(boxes)):
        for j in range(i+1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[0] < b[2]-0.5 and b[0] < a[2]-0.5 and a[1] < b[3]-0.5 and b[1] < a[3]-0.5:
                ovh = min(a[3], b[3]) - max(a[1], b[1])
                if ovh > 0.55*min(a[5], b[5]):
                    ov += 1
                    print('重叠 SVG:', a[4], '<<>>', b[4])
print('SVG 重叠:', ov)
