# -*- coding: utf-8 -*-
import re

f = r'<用户桌面目录>\NR-f40\系统消息-01-SSB-MIB-SIB1与OSI.html'
html = open(f, encoding='utf-8').read()
print('当前 SVG 数:', html.count('<svg'))

# 恢复图1、图2（此前正则误删）
for key, anchor in [('fig1', '<h3>1.3 SI 的"两层结构'), ('fig2', '<h3>2.2 原文表')]:
    seg = open(rf'<用户临时目录>\opencode\si-figs\{key}.html', encoding='utf-8').read()
    i = html.index(anchor)
    html = html[:i] + seg + '\n' + html[i:]
    print('恢复', key)

# 删除残留图3 并插入新图3
pat = re.compile(r'<figure[^>]*>.*?<b>图 3</b>.*?</figure>', re.S)
html, n3 = pat.subn('', html)
print('删除图3残留:', n3)
seg3 = open(r'<用户临时目录>\opencode\si-figs\fig3.html', encoding='utf-8').read()
i = html.index('<h3>2.9 本讲小结</h3>')
html = html[:i] + seg3 + '\n' + html[i:]

open(f, 'w', encoding='utf-8').write(html)
print('完成, SVG 数:', html.count('<svg'))
