# -*- coding: utf-8 -*-
"""合并 CSI 片段 + 插入 5 图"""
import os

base = r'<用户临时目录>\opencode'
target = r'<3GPP文档库目录>\CSI-01-信道状态信息全梳理.html'

h = ''
for f in ('csi-r1.html', 'csi-r2.html', 'csi-r3.html', 'csi-r4.html'):
    h += open(os.path.join(base, f), encoding='utf-8').read() + '\n'

def wrap(figid, svg, caption):
    svg = svg.replace('<svg ', '<svg style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;" ')
    return (f'<figure style="margin:18px 0; text-align:center;">\n' + svg + '\n'
            + f'<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>{figid}</b> {caption}</figcaption>\n</figure>\n')

caps = {
    'csifig1': ('图 1', 'CSI 三层框架：CSI-MeasConfig 内的资源池 / 资源配置 / 上报配置 / 触发状态四者关系（38.214 §5.2.1）'),
    'csifig2': ('图 2', 'CSI-RS 资源映射示意（Table 7.4.1.5.3-1 Row 4：4 端口、密度 1、FD-CDM2；matplotlib 渲染，1 个 PRB 内局部）'),
    'csifig3': ('图 3', '三种上报类型的触发与激活流程（38.214 §5.2.1.4-1 组合矩阵的可视化，Mermaid 渲染）'),
    'csifig4': ('图 4', 'CSI 计算时延 Z / Z′ 时序示意（两个条件必须同时满足；matplotlib 渲染）'),
    'csifig5': ('图 5', 'aperiodic CSI 端到端流程 9 步（Mermaid 渲染）'),
}

anchors = [
    ('csifig1', '<h3>1.3 三层框架', 'before'),
    ('csifig2', '<h3>2.3 原文+公式：资源映射', 'before'),
    ('csifig3', '<h3>6.1 原文表', 'before'),
    ('csifig4', '<h3>7.3 原文+公式：计算时延 Z / Z′（38.214 §5.4）【公式已核实】</h3>', 'after'),
    ('csifig5', '<h2>8. 第 8 讲', 'after'),
]
ok = 0
for key, anchor, pos in anchors:
    svg = open(os.path.join(base, key + '.svg'), encoding='utf-8').read()
    fid, cap = caps[key]
    seg = wrap(fid, svg, cap)
    i = h.find(anchor)
    if i < 0:
        print('锚点缺失:', key)
        continue
    if pos == 'after':
        i += len(anchor)
    h = h[:i] + seg + '\n' + h[i:]
    ok += 1
print('插入图:', ok, '/ 5')

open(target, 'w', encoding='utf-8').write(h)
print('SVG 数:', h.count('<svg'), '| figure:', h.count('<figure'), '| 大小:', len(h))
