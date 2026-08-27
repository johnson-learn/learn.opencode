# -*- coding: utf-8 -*-
"""CSI 主线单文件：合并 4 片段 + 练习册段 + 插图"""
import os, re

base = r'<用户临时目录>\opencode'
outdir = r'<3GPP文档库目录>'

h = ''
for f in ('csi-main-r1.html', 'csi-main-r2.html', 'csi-main-r3.html', 'csi-main-r4.html'):
    h += open(os.path.join(base, f), encoding='utf-8').read() + '\n'

# 练习册+计算器+总结（从 csi-r4 片段提取）
r4 = open(os.path.join(base, 'csi-r4.html'), encoding='utf-8').read()
i = r4.index('<h2>9. 练习册（25 题含答案）</h2>')
j = r4.index('</body>')
ex = r4[i:j]
# 练习册标题改 9，计算器/总结顺延为 10/11
ex = ex.replace('<h2>10. 交互式计算器</h2>', '<h2>10. 交互式计算器</h2>')
h += ex + '\n'

h += '\n<p class="src">本专题依据：TS 38.211/38.212/38.213/38.214/38.215/38.321/38.331 V15.4.0（本机文档库，Rel-15 2018-12 版）。公式经 Pix2Text 对原文档渲染页识别核实（标注【公式已核实】）。本文为教学讲义，协议最终解释以 3GPP 官网正式文档为准。</p>\n</body>\n</html>\n'

# 插图（锚点全文，不用部分匹配）
def wrap(figid, svg, caption):
    svg = svg.replace('<svg ', '<svg style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;" ')
    return (f'<figure style="margin:18px 0; text-align:center;">\n' + svg + '\n'
            + f'<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>{figid}</b> {caption}</figcaption>\n</figure>\n')

caps = {
    'csifig1': ('图 1', 'CSI 三层框架（第 1 讲）：资源池 / 资源配置 / 上报配置 / 触发状态的关系（38.214 §5.2.1）'),
    'csifig2': ('图 2', 'CSI-RS 资源映射示意（第 2 讲）：Table 7.4.1.5.3-1 Row 4（4 端口、密度 1、FD-CDM2）'),
    'csifig3': ('图 3', '三种上报类型的触发与激活流程（第 6 讲，38.214 Table 5.2.1.4-1 可视化）'),
    'csifig4': ('图 4', 'CSI 计算时延 Z / Z′ 时序示意（第 7 讲：两个条件必须同时满足）'),
    'csifig5': ('图 5', '一次 aperiodic CSI 的九步全程（第 8 讲主线回顾）'),
}

anchors = [
    ('csifig1', '<h3>1.4 三层框架：gNB 用三个配置结构把任务派给 UE</h3>', 'before'),
    ('csifig2', '<h3>2.4 时频位置表：Table 7.4.1.5.3-1（18 行查表法）</h3>', 'before'),
    ('csifig3', '<h3>6.1 组合矩阵：上报类型 × 资源类型（38.214 Table 5.2.1.4-1）</h3>', 'before'),
    ('csifig4', '<h3>7.2 原文+公式：计算时延 Z / Z′（38.214 §5.4）【公式已核实】</h3>', 'after'),
    ('csifig5', '<h3>8.1 九步全程（每步标注对应讲次）</h3>', 'before'),
]
ok = 0
for key, anchor, pos in anchors:
    svg = open(os.path.join(base, key + '.svg'), encoding='utf-8').read()
    fid, cap = caps[key]
    seg = wrap(fid, svg, cap)
    i = h.find(anchor)
    if i < 0:
        print('锚点缺失:', key, anchor[:40])
        continue
    if pos == 'after':
        i += len(anchor)
    h = h[:i] + seg + '\n' + h[i:]
    ok += 1
print('插入图:', ok, '/ 5')

target = os.path.join(outdir, 'CSI-信道状态信息全梳理.html')
open(target, 'w', encoding='utf-8').write(h)
print('大小:', len(h), '| SVG:', h.count('<svg'))

# 校验
body = re.sub(r'<svg\b[\s\S]*?</svg>', '', h)
print('比喻词:', len(re.findall(r'尺子|交卷|考卷|作业本|点名|挖空|灯塔|司令|户口本', body)))
print('伪公式:', len(re.findall(r'[\u2308\u230A]|N_RB\^|log2\(', h)))
print('MathJax:', len(re.findall(r'(?<!\\)\\\(', h)), '/', len(re.findall(r'(?<!\\)\\\)', h)), '|', len(re.findall(r'\\\[', h)), '/', len(re.findall(r'\\\]', h)))
toks = re.findall(r'<div[\s>]|</div>|<table[\s>]|</table>|<pre[\s>]|</pre>|<figure[\s>]|</figure>|<h2>|</h2>|<h3>|</h3>', h)
depth = 0; err = 0
for t in toks:
    depth += -1 if t.startswith('</') else 1
    if depth < 0: err += 1; depth = 0
print('标签深度:', depth, '| 负深度:', err, '| h2 数:', len(re.findall(r'<h2>', h)))
