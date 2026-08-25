# -*- coding: utf-8 -*-
"""修复 BWP 两处 SVG 重叠"""
d = r'<3GPP文档库目录>'
f = d + r'\BWP-带宽部分全梳理.html'
h = open(f, encoding='utf-8').read()
h = h.replace('<text x="45" y="37" font-size="14" fill="#555">小区载波带宽（例如 100 MHz）</text>',
              '<text x="45" y="50" font-size="14" fill="#555">小区载波带宽（例如 100 MHz）</text>')
h = h.replace('<text x="72" y="150" font-size="11.5" fill="#555">（active DL BWP 是默认/初始 BWP）</text>',
              '<text x="72" y="158" font-size="11.5" fill="#555">（active DL BWP 是默认/初始 BWP）</text>')
h = h.replace('<text x="270" y="146" font-size="12" fill="#333">（到非默认 BWP）→ 启动 / 重启</text>',
              '<text x="270" y="136" font-size="12" fill="#333">（到非默认 BWP）→ 启动 / 重启</text>')
open(f, 'w', encoding='utf-8').write(h)
print('已修复')
