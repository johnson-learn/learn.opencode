# -*- coding: utf-8 -*-
d = r'<3GPP文档库目录>'
f = d + r'\BWP-带宽部分全梳理.html'
h = open(f, encoding='utf-8').read()
h = h.replace('<text x="270" y="136" font-size="12" fill="#333">（到非默认 BWP）→ 启动 / 重启</text>',
              '<text x="270" y="146" font-size="12" fill="#333">（到非默认 BWP）→ 启动 / 重启</text>')
open(f, 'w', encoding='utf-8').write(h)
print('ok')
