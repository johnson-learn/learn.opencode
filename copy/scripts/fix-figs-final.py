# -*- coding: utf-8 -*-
"""修复：清空全部 figure，按锚点重插 9 图（图2=matplotlib、图8=Mermaid，其余 si-figs v2）"""
import re, os

f = r'<3GPP文档库目录>\系统消息-01-SSB-MIB-SIB1与OSI.html'
h = open(f, encoding='utf-8').read()

# 1) 全清 figure（每个 figure 独立匹配，安全）
h, n_del = re.subn(r'<figure[\s\S]*?</figure>', '', h)
print('清除 figure:', n_del)

# 2) 组装新图 2 与图 8
def wrap(figid, svg, caption):
    svg = svg.replace('<svg ', '<svg style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;" ')
    return (f'<figure style="margin:18px 0; text-align:center;">\n' + svg + '\n'
            + f'<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>{figid}</b> {caption}</figcaption>\n</figure>\n')

svg2 = open(r'<用户临时目录>\opencode\fig2-new.svg', encoding='utf-8').read()
new2 = wrap('图 2', svg2, 'SSB 时频结构块图（Table 7.4.3.1-1 的可视化，matplotlib 渲染：4 符号 × 240 子载波，PSS/SSS 各占符号 0/2 的中间 127 子载波，\\(v=N_{ID}^{cell}\\bmod 4\\)）')
svg8 = open(r'<用户临时目录>\opencode\fig8-new.svg', encoding='utf-8').read()
new8 = wrap('图 8', svg8, '按需 SI 双路径流程（Mermaid 渲染：Msg1 专用前导 / Msg3 RRCSystemInfoRequest；38.331 §5.2.2.3.3/§5.2.2.3.4 + 38.321 §5.1.4/§5.1.5）')

# 3) 按锚点插入（fig2/fig8 用新版；fig1/3/4/5/6/7/9 用 si-figs v2）
figdir = r'<用户临时目录>\opencode\si-figs'
anchors = [
    ('fig1', '<h3>1.3 SI 的', 'before'),
    ('fig2', '<h3>2.2 原文表', 'before', new2),
    ('fig3', '<h3>2.9 本讲小结</h3>', 'before'),
    ('fig4', '<div class="example"><b>例题 2.5</b>', 'before'),
    ('fig5', '<h3>3.4 PBCH 后续处理链（加扰 → CRC → Polar → 速率匹配 → 调制）</h3>', 'after'),
    ('fig6', '<div class="example"><b>例题 6.1</b>', 'before'),
    ('fig7', '<div class="orig"><b>38.331 V15.4.0 §6.5 Short Message', 'before'),
    ('fig8', '<h3>6.4 按需 SI（on-demand SI）的两种请求方式（38.331 §5.2.2.3.3 + 38.321）</h3>', 'after', new8),
    ('fig9', '<h2>7. 第 7 讲', 'after'),
]
ok = 0
for a in anchors:
    key, anchor, pos = a[0], a[1], a[2]
    if len(a) > 3:
        seg = a[3]
    else:
        seg = open(os.path.join(figdir, key + '.html'), encoding='utf-8').read()
    i = h.find(anchor)
    if i < 0:
        print('锚点缺失:', key)
        continue
    if pos == 'after':
        i += len(anchor)
    h = h[:i] + seg + '\n' + h[i:]
    ok += 1
print('插入成功:', ok, '/ 9')

open(f, 'w', encoding='utf-8').write(h)
print('SVG 数:', h.count('<svg'), '| figure:', h.count('<figure'), '| 大小:', len(h))
