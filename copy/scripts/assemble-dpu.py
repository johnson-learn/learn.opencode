# -*- coding: utf-8 -*-
"""组装 PDSCH/PUSCH 两个文件 + 插图 + 校验"""
import re, os

base = r'<用户临时目录>\opencode'
outdir = r'<用户桌面目录>\NR-f40'

def build(parts, figs, target):
    h = ''
    for f in parts:
        h += open(os.path.join(base, f), encoding='utf-8').read() + '\n'

    def wrap(figid, svg, caption):
        svg = svg.replace('<svg ', '<svg style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;" ')
        return (f'<figure style="margin:18px 0; text-align:center;">\n' + svg + '\n'
                + f'<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>{figid}</b> {caption}</figcaption>\n</figure>\n')

    for key, anchor, pos, cap in figs:
        svg = open(os.path.join(base, key + '.svg'), encoding='utf-8').read()
        seg = wrap('图', svg, cap)
        i = h.find(anchor)
        assert i > 0, '锚点缺失: ' + key
        if pos == 'after':
            i += len(anchor)
        h = h[:i] + seg + '\n' + h[i:]

    t = os.path.join(outdir, target)
    open(t, 'w', encoding='utf-8').write(h)
    print(target, len(h))

    body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
    nojs = re.sub(r'<script[\s\S]*?</script>', '', h)
    print('  比喻词:', len(re.findall(r'尺子|交卷|考卷|作业本|点名|挖空|灯塔|司令|户口本', body)),
          '| 伪公式:', len(re.findall(r'[\u2308\u230A]|N_RB\^|log2\(', nojs)),
          '| MathJax:', len(re.findall(r'(?<!\\)\\\(', h)), '/', len(re.findall(r'(?<!\\)\\\)', h)),
          '| h2:', len(re.findall(r'<h2>', h)))
    toks = re.findall(r'<div[\s>]|</div>|<table[\s>]|</table>|<pre[\s>]|</pre>|<figure[\s>]|</figure>|<h2>|</h2>|<h3>|</h3>|<ol[\s>]|</ol>|<ul[\s>]|</ul>|<span[\s>]|</span>', h)
    depth = 0
    for x in toks:
        depth += -1 if x.startswith('</') else 1
        if depth < 0:
            depth = 0
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
    print('  标签深度:', depth, '| SVG 重叠:', ov)

build(['pdsch-r1.html', 'pdsch-r2.html', 'pdsch-r3.html'],
      [
          ('dfig1', '<h3>4.1 处理链总览（38.212 §7.2 目录 + 原文归纳）</h3>', 'before', 'PDSCH 处理链（第 4 讲）：TB → CRC → BG 选择 → 分段 → LDPC → 速率匹配 → 级联 → 加扰 → 调制 → 层映射'),
          ('dfig2', '<h3>2.3 本讲小结（把球交给下一讲）</h3>', 'before', 'PDSCH 映射类型 A 示意（第 2/5 讲）：前载 DM-RS 固定在时隙级符号、PDSCH 从 S 起长 L'),
      ],
      'PDSCH-物理下行共享信道全梳理.html')

build(['pusch-r1.html', 'pusch-r2.html'],
      [
          ('ufig1', '<h3>4.1 UL-SCH 处理链（38.212 §6.2 目录）</h3>', 'before', 'PUSCH 处理链（第 4 讲）：与 PDSCH 同构 + 上行独有的 UCI 复用与可选变换预编码'),
          ('ufig2', '<h3>2.4 本讲小结（把球交给下一讲）</h3>', 'before', 'PUSCH intraSlot 跳频示意（第 2 讲）：前半符号第 1 跳、后半符号第 2 跳（偏移 RB_offset）'),
      ],
      'PUSCH-物理上行共享信道全梳理.html')
