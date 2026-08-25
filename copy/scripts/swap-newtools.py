# -*- coding: utf-8 -*-
"""用新工具图替换文档中的图 2 与图 8"""
import re

f = r'<用户桌面目录>\NR-f40\系统消息-01-SSB-MIB-SIB1与OSI.html'
h = open(f, encoding='utf-8').read()

# 新图 2（matplotlib）
svg2 = open(r'<用户临时目录>\opencode\fig2-new.svg', encoding='utf-8').read()
svg2 = svg2.replace('<svg ', '<svg style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;" ')
fig2 = ('<figure style="margin:18px 0; text-align:center;">\n'
        + svg2 + '\n'
        + '<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>图 2</b> '
        + 'SSB 时频结构块图（Table 7.4.3.1-1 的可视化，matplotlib 渲染：4 符号 × 240 子载波，'
        + 'PSS/SSS 各占符号 0/2 的中间 127 子载波，\(v=N_{ID}^{cell}\bmod 4\)）</figcaption>\n</figure>\n')

# 新图 8（Mermaid）
svg8 = open(r'<用户临时目录>\opencode\fig8-new.svg', encoding='utf-8').read()
svg8 = svg8.replace('<svg ', '<svg style="max-width:100%; height:auto; background:#fff; border:1px solid #bbb;" ')
fig8 = ('<figure style="margin:18px 0; text-align:center;">\n'
        + svg8 + '\n'
        + '<figcaption style="font-size:13px; color:#555; margin-top:6px;"><b>图 8</b> '
        + '按需 SI 双路径流程（Mermaid 渲染：Msg1 专用前导 / Msg3 RRCSystemInfoRequest；'
        + '38.331 §5.2.2.3.3/§5.2.2.3.4 + 38.321 §5.1.4/§5.1.5）</figcaption>\n</figure>\n')

pat = re.compile(r'<figure[\s\S]*?<b>图 2</b>[\s\S]*?</figure>')
h, n2 = pat.subn(lambda m: fig2, h, count=1)
print('替换图2:', n2)
pat8 = re.compile(r'<figure[\s\S]*?<b>图 8</b>[\s\S]*?</figure>')
h, n8 = pat8.subn(lambda m: fig8, h, count=1)
print('替换图8:', n8)

open(f, 'w', encoding='utf-8').write(h)
print('SVG 数:', h.count('<svg'), '| 大小:', len(h))
