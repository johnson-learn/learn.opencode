# -*- coding: utf-8 -*-
"""去重：保留最后一份 restore（清理版），删除前 3 份；重插 fig2/fig4"""
import re

f = r'C:\Users\job_p\Desktop\NR-f40\系统消息-01-SSB-MIB-SIB1与OSI.html'
h = open(f, encoding='utf-8').read()

P = [m.start() for m in re.finditer(r'<h3>1\.3 SI 的', h)]
print('1.3 位置:', P)
p29 = h.find('<h3>2.9 本讲小结')
print('2.9 位置:', p29)
assert len(P) == 4 and p29 > P[-1]

A = h[:P[0]]                      # head + 1.1/1.2 + fig1
B = h[P[-1]:p29]                  # 最后一份清理版 restore + fig3
C = h[p29:]                       # 2.9 及以后（fig5~fig9 在内）

# 在 B 内插 fig2、fig4（锚点唯一）
fig2 = open(r'C:\Users\job_p\AppData\Local\Temp\opencode\si-figs\fig2.html', encoding='utf-8').read()
i2 = B.find('<h3>2.2 原文表')
assert i2 > 0
B = B[:i2] + fig2 + '\n' + B[i2:]

fig4 = open(r'C:\Users\job_p\AppData\Local\Temp\opencode\si-figs\fig4.html', encoding='utf-8').read()
i4 = B.find('<div class="example"><b>例题 2.5</b>')
assert i4 > 0
B = B[:i4] + fig4 + '\n' + B[i4:]

new = A + B + C
open(f, 'w', encoding='utf-8').write(new)
print('重建完成 | 大小:', len(new))
print('1.3 份数:', len(re.findall(r'<h3>1\.3 SI 的', new)))
print('SVG 数:', new.count('<svg'), '| figure:', new.count('<figure'))
print('h2:', re.findall(r'<h2>([^<]+)', new))
