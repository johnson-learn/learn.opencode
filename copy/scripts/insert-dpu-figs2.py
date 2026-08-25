# -*- coding: utf-8 -*-
"""插入补充图（PDSCH ×4 + PUSCH ×3）+ 校验"""
import re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
base = r'<用户临时目录>\opencode'
d = r'<用户桌面目录>\NR-f40'

def insert(fname, figs):
    f = d + '\\' + fname
    h = open(f, encoding='utf-8').read()
    for key, anchor, pos, cap in figs:
        svg = open(os.path.join(base, key + '.svg'), encoding='utf-8').read()
        svg = svg.replace('<svg ', '<svg style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;" ')
        seg = (f'<figure style="margin:18px 0; text-align:center;">\n' + svg + '\n'
               + f'<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>图</b> {cap}</figcaption>\n</figure>\n')
        i = h.find(anchor)
        assert i > 0, '锚点缺失: ' + key + ' in ' + fname
        if pos == 'after':
            i += len(anchor)
        h = h[:i] + seg + '\n' + h[i:]
        print(' ', key, '->', fname)
    open(f, 'w', encoding='utf-8').write(h)
    return h

h1 = insert('PDSCH-物理下行共享信道全梳理.html', [
    ('dfig3', '<h3>2.2 原文：频域分配 type 0 / type 1（38.214 §5.1.2.2）</h3>', 'before',
     '频域分配 type 0（RBG 位图）与 type 1（RIV 连续）对比示意（第 2 讲）'),
    ('dfig4', '<h3>3.2 原文+公式：TBS 四步确定（38.214 §5.1.3.2）【公式已核实】</h3>', 'before',
     'TBS 四步确定流程（第 3 讲）：可用 RE → 中间比特 → 量化 → 对齐'),
    ('dfig5', '<h3>3.1 MCS 三张表（38.214 §5.1.3.1，表 5.1.3.1-1/2/3）</h3>', 'after',
     'PDSCH MCS 三表谱效阶梯对比（第 3 讲）'),
    ('dfig6', '<h3>5.1 DM-RS 配置类型与端口（38.211 §7.4.1.1，要点 + 表）</h3>', 'before',
     'PDSCH DM-RS Type 1（梳状）与 Type 2（2×2 块）RE 图案对比（第 5 讲）'),
])

h2 = insert('PUSCH-物理上行共享信道全梳理.html', [
    ('ufig3', '<h3>3.1 原文：变换预编码（38.214 §6.1.3）</h3>', 'before',
     'CP-OFDM 与 DFT-s-OFDM（变换预编码）两条波形路径对比（第 3 讲）'),
    ('ufig4', '<h3>6.1 原文+公式：PUSCH 功率控制（38.213 §7.1.1）【公式已核实】</h3>', 'before',
     'P_PUSCH 功率公式分解示意（第 6 讲，对应例题 6.1）'),
    ('ufig5', '<h3>4.2 UCI 复用与 \\(\\beta_{offset}\\)（38.212 §6.3.2.4 要点）</h3>', 'before',
     'PUSCH 内 UCI 复用插入顺序（第 4 讲）：HARQ-ACK ＞ CSI Part1 ＞ CSI Part2，按 β_offset 折算 RE'),
])

for fname in ['PDSCH-物理下行共享信道全梳理.html', 'PUSCH-物理上行共享信道全梳理.html']:
    h = open(d + '\\' + fname, encoding='utf-8').read()
    body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
    nojs = re.sub(r'<script[\s\S]*?</script>', '', h)
    o = len(re.findall(r'(?<!\\)\\\(', h))
    c = len(re.findall(r'(?<!\\)\\\)', h))
    toks = re.findall(r'<div[\s>]|</div>|<table[\s>]|</table>|<pre[\s>]|</pre>|<figure[\s>]|</figure>|<h2>|</h2>|<h3>|</h3>|<span[\s>]|</span>', h)
    dep = 0
    for t in toks:
        dep += -1 if t.startswith('</') else 1
        if dep < 0:
            dep = 0
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
            boxes.append((x, y-hgt, x+w, y+3, sz))
        for i in range(len(boxes)):
            for j in range(i+1, len(boxes)):
                a, b = boxes[i], boxes[j]
                if a[0] < b[2]-0.5 and b[0] < a[2]-0.5 and a[1] < b[3]-0.5 and b[1] < a[3]-0.5:
                    ovh = min(a[3], b[3]) - max(a[1], b[1])
                    if ovh > 0.55*min(a[4], b[4]):
                        ov += 1
    print(fname, '| SVG:', h.count('<svg'), '| MathJax:', o, '/', c, '| 伪公式:', len(re.findall(r'[\u2308\u230A]|(?<![\\a-zA-Z])log2\(', nojs)), '| 标签深度:', dep, '| 重叠:', ov, '| 大小:', len(h))
